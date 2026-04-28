import json
from .ir import Program, Instruction, Opcode
from .packets import encode_program

def assemble(program: Program) -> bytes:
    return encode_program(program)

def parse_assembly(text: str) -> Program:
    # Minimalist assembly parser
    instructions = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(maxsplit=1)
        op_name = parts[0]
        args = []
        if len(parts) > 1:
            # Very simple arg parsing: comma separated JSON-like
            # In a real system, this would be a proper lexer/parser
            try:
                args = json.loads(f"[{parts[1]}]")
            except:
                args = [parts[1].strip('"')]
        
        instructions.append(Instruction(Opcode[op_name], args))
    return Program(instructions=instructions)
