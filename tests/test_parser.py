from intentir.binary import Opcode, PayloadRef
from intentir.intentasm_parser import parse_intentasm


def test_parse_intentasm_program():
    program = parse_intentasm(
        """
        # minimal packet
        AGENT name="planner"
        TASK id="repo-scan" summary="Scan repository"
        PAYLOAD name="scan_request" value={"root":"src"}
        SEND to="worker"
        CALL tool="repo.scan" payload=@scan_request mode="sync"
        HALT
        """
    )

    assert len(program.instructions) == 6
    assert program.instructions[0].opcode == Opcode.AGENT
    assert program.instructions[4].opcode == Opcode.CALL
    assert isinstance(program.instructions[4].operands[1].value, PayloadRef)
    assert program.instructions[4].operands[1].value.name == "scan_request"
