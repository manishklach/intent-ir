from __future__ import annotations

from pathlib import Path

from .binary import Instruction, Opcode, PayloadRef, Program, decode_program
from .trace import TraceWriter
from .transport import should_deliver
from .verifier import VerificationError, Verifier


class AgentRuntime:
    def __init__(self, agent_name: str, execute: bool = False, trace_path: str | None = None):
        self.agent_name = agent_name
        self.execute = execute
        self.trace_writer = TraceWriter(trace_path) if trace_path else None
        self.state = {
            "sender": None,
            "task": None,
            "budget": {},
            "payloads": {},
            "recipient": None,
            "calls": [],
            "commits": [],
            "released": [],
            "status": "ready",
        }

    def close(self) -> None:
        if self.trace_writer:
            self.trace_writer.close()

    def recv_binary(self, path: str | Path):
        try:
            packet_path = Path(path)
            program = decode_program(packet_path.read_bytes())
            self._record(None, None, f"received packet {packet_path.name}", {"instruction_count": len(program.instructions)})
            verifier = Verifier()
            try:
                verifier.verify(program, receiver_agent=self.agent_name)
            except VerificationError as exc:
                message = str(exc)
                self.state["status"] = "rejected"
                self._record(None, None, "verification failed", {"outcome": "reject", "reason": message})
                self._record(None, None, f"rejected packet: {message}", {"outcome": "reject"})
                return {
                    "packet": packet_path.name,
                    "instruction_count": len(program.instructions),
                    "verified": False,
                    "delivered": False,
                    "executed": False,
                    "rejected": True,
                    "error": message,
                }
            self._record(None, None, "verification passed", {"outcome": "verify-pass"})
            if not should_deliver(program, self.agent_name):
                message = f"packet not addressed to agent '{self.agent_name}'"
                self._record(None, None, "drop", message)
                return {
                    "packet": packet_path.name,
                    "instruction_count": len(program.instructions),
                    "verified": True,
                    "delivered": False,
                    "executed": False,
                    "message": message,
                }
            if not self.execute:
                message = f"packet delivered to agent '{self.agent_name}'"
                self._record(None, None, "deliver", message)
                return {
                    "packet": packet_path.name,
                    "instruction_count": len(program.instructions),
                    "verified": True,
                    "delivered": True,
                    "executed": False,
                    "message": message,
                }
            result = self.execute_program(program)
            return {
                "packet": packet_path.name,
                "instruction_count": len(program.instructions),
                "verified": True,
                "delivered": True,
                "executed": True,
                "state": result,
                "executed_tools": [call["tool"] for call in result["calls"]],
                "committed_artifacts": [
                    commit["artifact"] for commit in result["commits"] if isinstance(commit, dict) and "artifact" in commit
                ],
            }
        finally:
            self.close()

    def execute_program(self, program: Program):
        self.state["status"] = "running"
        try:
            for pc, instruction in enumerate(program.instructions):
                self._execute_instruction(pc, instruction)
                if self.state["status"] in {"halted", "failed"}:
                    break
        finally:
            self.close()
        return self.state

    def _execute_instruction(self, pc: int, instruction: Instruction) -> None:
        opcode = instruction.opcode
        if opcode == Opcode.AGENT:
            self.state["sender"] = _operand(instruction, "name")
            self._record(pc, opcode.name, "set sender")
        elif opcode == Opcode.TASK:
            self.state["task"] = {operand.key: operand.value for operand in instruction.operands}
            self._record(pc, opcode.name, "set task")
        elif opcode == Opcode.BUDGET:
            for operand in instruction.operands:
                self.state["budget"][operand.key] = operand.value
            self._record(pc, opcode.name, "allocated budget")
        elif opcode == Opcode.PAYLOAD:
            payload_name = str(_operand(instruction, "name"))
            self.state["payloads"][payload_name] = _operand(instruction, "value")
            self._record(pc, opcode.name, f"registered payload {payload_name}")
        elif opcode == Opcode.SEND:
            self.state["recipient"] = _operand(instruction, "to")
            self._record(pc, opcode.name, f"delivery target {self.state['recipient']}")
        elif opcode == Opcode.CALL:
            tool_name = _operand(instruction, "tool")
            payload_value = _resolve_payload(_operand(instruction, "payload"), self.state["payloads"])
            call_record = {"tool": tool_name, "payload": payload_value}
            self.state["calls"].append(call_record)
            message = f"receiver executed CALL {tool_name}"
            self._record(pc, opcode.name, message, {"call": call_record})
        elif opcode == Opcode.ASSERT:
            self._record(pc, opcode.name, f"recorded assertion {_operand(instruction, 'condition')}")
        elif opcode == Opcode.COMMIT:
            commit_record = {operand.key: operand.value for operand in instruction.operands}
            self.state["commits"].append(commit_record)
            self._record(pc, opcode.name, "commit recorded", {"commit": commit_record})
        elif opcode == Opcode.FAIL:
            reason = _operand(instruction, "reason") or "intent packet requested failure"
            self.state["status"] = "failed"
            self._record(pc, opcode.name, f"execution failed: {reason}")
        elif opcode == Opcode.TRACE:
            self._record(pc, opcode.name, "trace marker")
        elif opcode == Opcode.RELEASE:
            resource = _operand(instruction, "resource")
            self.state["released"].append(resource)
            self._record(pc, opcode.name, f"released {resource}")
        elif opcode == Opcode.HALT:
            self.state["status"] = "halted"
            self._record(pc, opcode.name, "halted")
        else:
            raise VerificationError(f"runtime does not implement opcode {opcode.name}")

    def _record(self, pc: int | None, opcode: str | None, message: str, extra: dict | None = None) -> None:
        if self.trace_writer:
            event = {
                "event": "execute" if opcode else "transport",
                "agent": self.agent_name,
                "pc": pc,
                "opcode": opcode,
                "message": message,
                "state": self.state,
            }
            if extra:
                event.update(extra)
            self.trace_writer.record(event)


def _operand(instruction: Instruction, key: str):
    for operand in instruction.operands:
        if operand.key == key:
            return operand.value
    return None


def _resolve_payload(value, payloads: dict[str, object]):
    if isinstance(value, PayloadRef):
        return payloads.get(value.name)
    return value
