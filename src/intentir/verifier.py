from __future__ import annotations

from .binary import Opcode, PayloadRef, Program


class VerificationError(ValueError):
    pass


class Verifier:
    def verify(self, program: Program) -> bool:
        if not program.instructions:
            raise VerificationError("program cannot be empty")
        if program.instructions[0].opcode != Opcode.AGENT:
            raise VerificationError("program must begin with AGENT")
        if program.instructions[-1].opcode != Opcode.HALT:
            raise VerificationError("program must end with HALT")

        seen_task = False
        seen_send = False
        payload_names: set[str] = set()

        for index, instruction in enumerate(program.instructions):
            if instruction.opcode == Opcode.TASK:
                seen_task = True
            elif instruction.opcode == Opcode.SEND:
                seen_send = True
            elif instruction.opcode == Opcode.PAYLOAD:
                payload_name = _operand_value(instruction, "name")
                if not payload_name:
                    raise VerificationError(f"instruction {index}: PAYLOAD requires name")
                payload_names.add(str(payload_name))
            elif instruction.opcode == Opcode.CALL:
                if not seen_task or not seen_send:
                    raise VerificationError("CALL requires prior TASK and SEND")
                payload_operand = _operand_value(instruction, "payload")
                if isinstance(payload_operand, PayloadRef) and payload_operand.name not in payload_names:
                    raise VerificationError(
                        f"instruction {index}: CALL references undefined payload '{payload_operand.name}'"
                    )
            elif instruction.opcode == Opcode.BUDGET and not instruction.operands:
                raise VerificationError(f"instruction {index}: BUDGET requires at least one operand")
        return True


def _operand_value(instruction, key: str):
    for operand in instruction.operands:
        if operand.key == key:
            return operand.value
    return None
