from __future__ import annotations

import json
from pathlib import Path

from .binary import PayloadRef, Program, decode_program


def _render_value(value) -> str:
    if isinstance(value, PayloadRef):
        return f"@{value.name}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), sort_keys=True)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def render_intentasm(program: Program) -> str:
    lines: list[str] = []
    for instruction in program.instructions:
        if instruction.operands:
            operand_text = " ".join(
                f"{operand.key}={_render_value(operand.value)}" for operand in instruction.operands
            )
            lines.append(f"{instruction.opcode.name} {operand_text}")
        else:
            lines.append(instruction.opcode.name)
    return "\n".join(lines) + "\n"


def disassemble_binary(data: bytes) -> str:
    return render_intentasm(decode_program(data))


def disassemble_file(path: str | Path) -> str:
    return disassemble_binary(Path(path).read_bytes())
