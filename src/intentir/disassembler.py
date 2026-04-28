import json
from .ir import Program
from .packets import decode_program

def disassemble(data: bytes) -> str:
    program = decode_program(data)
    lines = []
    for inst in program.instructions:
        args_str = ", ".join(json.dumps(arg) for arg in inst.operands)
        lines.append(f"{inst.opcode.name:15} {args_str}")
    return "\n".join(lines)

def program_to_asm(program: Program) -> str:
    lines = []
    for inst in program.instructions:
        args_str = ", ".join(json.dumps(arg) for arg in inst.operands)
        lines.append(f"{inst.opcode.name:15} {args_str}")
    return "\n".join(lines)
