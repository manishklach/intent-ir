import pytest
from intentir.ir import Program, Instruction, Opcode
from intentir.packets import encode_program, decode_program

def test_encode_decode():
    insts = [
        Instruction(Opcode.DECLARE_AGENT, ["bot-1"]),
        Instruction(Opcode.HALT)
    ]
    prog = Program(instructions=insts, metadata={"ver": 1})
    
    encoded = encode_program(prog)
    decoded = decode_program(encoded)
    
    assert decoded.metadata == {"ver": 1}
    assert len(decoded.instructions) == 2
    assert decoded.instructions[0].opcode == Opcode.DECLARE_AGENT
    assert decoded.instructions[0].operands == ["bot-1"]
