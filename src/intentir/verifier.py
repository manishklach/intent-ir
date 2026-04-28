from __future__ import annotations

from .binary import Opcode, PayloadRef, Program

ALLOWED_TOOLS_BY_AGENT = {
    "worker": {"repo.scan", "artifact.write", "trace.emit"},
}

DENIED_TOOLS = {"shell.exec", "file.delete", "network.post", "secrets.read"}


class VerificationError(ValueError):
    pass


class Verifier:
    def verify(self, program: Program, receiver_agent: str | None = None) -> bool:
        if not program.instructions:
            raise VerificationError("program cannot be empty")
        if program.instructions[0].opcode != Opcode.AGENT:
            raise VerificationError("program must begin with AGENT")
        if program.instructions[-1].opcode != Opcode.HALT:
            raise VerificationError("program must end with HALT")

        seen_task = False
        seen_send = False
        payload_names: set[str] = set()
        effective_receiver = receiver_agent or _find_receiver_agent(program)

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
                tool_name = _operand_value(instruction, "tool")
                if effective_receiver and tool_name:
                    self._verify_tool_policy(effective_receiver, str(tool_name))
            elif instruction.opcode == Opcode.BUDGET and not instruction.operands:
                raise VerificationError(f"instruction {index}: BUDGET requires at least one operand")
        return True

    def _verify_tool_policy(self, receiver_agent: str, tool_name: str) -> None:
        if tool_name in DENIED_TOOLS:
            raise VerificationError(f'tool "{tool_name}" is not allowed for agent "{receiver_agent}"')
        allowed_tools = ALLOWED_TOOLS_BY_AGENT.get(receiver_agent)
        if allowed_tools is not None and tool_name not in allowed_tools:
            raise VerificationError(f'tool "{tool_name}" is not allowed for agent "{receiver_agent}"')


def _operand_value(instruction, key: str):
    for operand in instruction.operands:
        if operand.key == key:
            return operand.value
    return None


def _find_receiver_agent(program: Program) -> str | None:
    for instruction in program.instructions:
        if instruction.opcode == Opcode.SEND:
            target = _operand_value(instruction, "to")
            if target:
                return str(target)
    return None
