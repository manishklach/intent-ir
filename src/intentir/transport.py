from __future__ import annotations

from .binary import Opcode, Program


def extract_send_target(program: Program) -> str | None:
    for instruction in program.instructions:
        if instruction.opcode == Opcode.SEND:
            for operand in instruction.operands:
                if operand.key == "to":
                    return str(operand.value)
    return None


def should_deliver(program: Program, receiver_agent: str) -> bool:
    target = extract_send_target(program)
    return target is None or target == receiver_agent
