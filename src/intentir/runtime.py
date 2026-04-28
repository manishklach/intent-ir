from typing import Any, Dict, List, Optional
from .ir import Program, Opcode, Instruction
from .trace import Tracer

class Runtime:
    def __init__(self, tracer: Optional[Tracer] = None):
        self.tracer = tracer
        self.pc = 0
        self.state: Dict[str, Any] = {
            "agent": None,
            "task": None,
            "budget": {},
            "resources": [],
            "logs": [],
            "committed_data": None,
            "status": "ready"
        }

    def run(self, program: Program):
        self.state["status"] = "running"
        while self.pc < len(program.instructions):
            inst = program.instructions[self.pc]
            self.execute_instruction(inst)
            if self.state["status"] in ["halted", "failed"]:
                break
            self.pc += 1
        
        return self.state

    def execute_instruction(self, inst: Instruction):
        opcode = inst.opcode
        args = inst.operands
        delta = {}

        if opcode == Opcode.DECLARE_AGENT:
            self.state["agent"] = args[0]
            delta["agent"] = args[0]
        elif opcode == Opcode.DECLARE_TASK:
            self.state["task"] = args[0]
            delta["task"] = args[0]
        elif opcode == Opcode.ALLOC_BUDGET:
            self.state["budget"][args[1]] = args[0]
            delta["budget"] = self.state["budget"]
        elif opcode == Opcode.REQUEST_RESOURCE:
            self.state["resources"].append(args[0])
            delta["resources"] = self.state["resources"]
        elif opcode == Opcode.CALL_TOOL:
            # Mock tool call
            print(f"[*] Tool Call: {args[0]}({args[1]})")
            delta["tool_call"] = {"name": args[0], "result": "ok"}
        elif opcode == Opcode.LOG:
            self.state["logs"].append(args[0])
            print(f"[LOG] {args[0]}")
        elif opcode == Opcode.ASSERT:
            # Simple mock assertion
            print(f"[*] Asserting: {args[0]}")
        elif opcode == Opcode.COMMIT:
            self.state["committed_data"] = args[0]
            delta["committed"] = args[0]
        elif opcode == Opcode.FAIL:
            self.state["status"] = "failed"
            self.state["error"] = args[0]
            delta["status"] = "failed"
        elif opcode == Opcode.HALT:
            self.state["status"] = "halted"
            delta["status"] = "halted"

        if self.tracer:
            self.tracer.record(self.pc, opcode.name, args, delta)
