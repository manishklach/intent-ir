import pytest

from intentir.binary import Instruction, Opcode, Operand, Program
from intentir.intentasm_parser import parse_intentasm
from intentir.verifier import VerificationError, Verifier


def test_verifier_accepts_valid_program():
    program = parse_intentasm(
        """
        AGENT name="planner"
        TASK id="hello" summary="Say hello"
        SEND to="worker"
        CALL tool="agent.echo" mode="sync"
        HALT
        """
    )

    assert Verifier().verify(program) is True


def test_verifier_rejects_call_without_task_or_send():
    program = Program(
        instructions=[
            Instruction(Opcode.AGENT, [Operand("name", "planner")]),
            Instruction(Opcode.CALL, [Operand("tool", "repo.scan")]),
            Instruction(Opcode.HALT, []),
        ]
    )

    with pytest.raises(VerificationError, match="CALL requires prior TASK and SEND"):
        Verifier().verify(program)
