from intentir.binary import Opcode, PayloadRef
from intentir.intentasm_parser import parse_intentasm


def test_parse_intentasm_program():
    program = parse_intentasm(
        """
        # assembly-style packet
        AGENT planner
        TASK t1 TYPE "repo_scan" SUMMARY "Scan repository"
        PAYLOAD scan_request JSON {"root":"src"}
        SEND planner worker CHANNEL "task" PAYLOAD scan_request
        CALL worker TOOL "repo.scan" ARGS scan_request
        ASSERT LAST.status == "ok"
        HALT
        """
    )

    assert len(program.instructions) == 7
    assert program.instructions[0].opcode == Opcode.AGENT
    assert program.instructions[4].opcode == Opcode.CALL
    assert isinstance(program.instructions[4].operands[2].value, PayloadRef)
    assert program.instructions[4].operands[2].value.name == "scan_request"
    assert program.instructions[5].operands[0].value == 'LAST.status == "ok"'
