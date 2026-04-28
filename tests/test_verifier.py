import pytest
from intentir.ir import Program, Instruction, Opcode
from intentir.verifier import Verifier, VerificationError

def test_verifier_pass():
    prog = Program([
        Instruction(Opcode.DECLARE_AGENT, ["bot"]),
        Instruction(Opcode.HALT)
    ])
    verifier = Verifier()
    assert verifier.verify(prog) is True

def test_verifier_no_agent():
    prog = Program([
        Instruction(Opcode.LOG, ["hello"]),
        Instruction(Opcode.HALT)
    ])
    verifier = Verifier()
    with pytest.raises(VerificationError, match="must start with DECLARE_AGENT"):
        verifier.verify(prog)

def test_verifier_no_halt():
    prog = Program([
        Instruction(Opcode.DECLARE_AGENT, ["bot"]),
        Instruction(Opcode.LOG, ["hello"])
    ])
    verifier = Verifier()
    with pytest.raises(VerificationError, match="must end with HALT"):
        verifier.verify(prog)
