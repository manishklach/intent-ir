from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .binary import Instruction, Opcode, Operand, PayloadRef, Program
from .disassembler import render_intentasm


def _compact_json(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.loads(json.dumps(value, separators=(",", ":"), sort_keys=True))
    return value


def compile_message(data: dict[str, Any]) -> Program:
    instructions: list[Instruction] = []
    sender = data.get("sender") or data.get("agent") or data.get("from")
    recipient = data.get("recipient") or data.get("to")
    task = data.get("task", {})
    budget = data.get("budget", {})
    payloads = data.get("payloads", {})
    call = data.get("call")
    asserts = data.get("asserts", [])
    trace_data = data.get("trace")
    commit = data.get("commit")
    release = data.get("release", [])
    fail = data.get("fail")

    if sender:
        instructions.append(Instruction(Opcode.AGENT, [Operand("name", str(sender))]))

    if task:
        operands = []
        for key in ("id", "summary", "kind", "priority"):
            if key in task:
                operands.append(Operand(key, task[key]))
        instructions.append(Instruction(Opcode.TASK, operands))

    if budget:
        instructions.append(
            Instruction(
                Opcode.BUDGET,
                [Operand(key, value) for key, value in budget.items()],
            )
        )

    for payload_name, payload_value in payloads.items():
        instructions.append(
            Instruction(
                Opcode.PAYLOAD,
                [
                    Operand("name", payload_name),
                    Operand("format", "json"),
                    Operand("value", _compact_json(payload_value)),
                ],
            )
        )

    if recipient:
        instructions.append(Instruction(Opcode.SEND, [Operand("to", str(recipient))]))

    if call:
        call_operands = [Operand("tool", call["tool"])]
        if "payload" in call:
            call_operands.append(Operand("payload", PayloadRef(str(call["payload"]))))
        if "mode" in call:
            call_operands.append(Operand("mode", call["mode"]))
        instructions.append(Instruction(Opcode.CALL, call_operands))

    for condition in asserts:
        instructions.append(Instruction(Opcode.ASSERT, [Operand("condition", str(condition))]))

    if trace_data:
        if isinstance(trace_data, dict):
            operands = [Operand(key, value) for key, value in trace_data.items()]
        else:
            operands = [Operand("name", str(trace_data))]
        instructions.append(Instruction(Opcode.TRACE, operands))

    if commit:
        if isinstance(commit, dict):
            operands = [Operand(key, value) for key, value in commit.items()]
        else:
            operands = [Operand("status", str(commit))]
        instructions.append(Instruction(Opcode.COMMIT, operands))

    for resource in release:
        instructions.append(Instruction(Opcode.RELEASE, [Operand("resource", str(resource))]))

    if fail:
        instructions.append(Instruction(Opcode.FAIL, [Operand("reason", str(fail))]))

    instructions.append(Instruction(Opcode.HALT, []))
    return Program(instructions=instructions)


def compile_message_file(path: str | Path) -> Program:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return compile_message(data)


def compile_message_to_asm(path: str | Path) -> str:
    return render_intentasm(compile_message_file(path))
