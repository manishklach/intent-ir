from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .binary import Opcode, PayloadRef, Program


class VerificationError(ValueError):
    pass


class Verifier:
    def verify(
        self,
        program: Program,
        receiver_agent: str | None = None,
        policy: dict[str, Any] | None = None,
        policy_name: str | None = None,
    ) -> bool:
        if not program.instructions:
            raise VerificationError("program cannot be empty")
        if program.instructions[0].opcode != Opcode.AGENT:
            raise VerificationError("program must begin with AGENT")
        if program.instructions[-1].opcode != Opcode.HALT:
            raise VerificationError("program must end with HALT")

        seen_task = False
        seen_send = False
        seen_assert = False
        seen_commit = False
        payload_names: set[str] = set()
        effective_receiver = receiver_agent or _find_receiver_agent(program)
        effective_policy = policy or {}
        effective_policy_name = policy_name or "<inline-policy>"

        for index, instruction in enumerate(program.instructions):
            if instruction.opcode == Opcode.TASK:
                seen_task = True
            elif instruction.opcode == Opcode.SEND:
                seen_send = True
            elif instruction.opcode == Opcode.ASSERT:
                seen_assert = True
            elif instruction.opcode == Opcode.COMMIT:
                seen_commit = True
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
                    self._verify_tool_policy(str(tool_name), effective_policy, effective_policy_name)
            elif instruction.opcode == Opcode.BUDGET:
                if not instruction.operands:
                    raise VerificationError(f"instruction {index}: BUDGET requires at least one operand")
                self._verify_budget_policy(instruction, effective_policy)
        if effective_policy.get("require_asserts") and not seen_assert:
            raise VerificationError("missing ASSERT instruction (policy requires asserts)")
        if effective_policy.get("require_commit") and not seen_commit:
            raise VerificationError("missing COMMIT instruction (policy requires commit)")
        return True

    def _verify_tool_policy(self, tool_name: str, policy: dict[str, Any], policy_name: str) -> None:
        denied_tools = set(policy.get("denied_tools", []))
        if tool_name in denied_tools:
            raise VerificationError(f'tool "{tool_name}" not allowed by policy "{policy_name}"')
        allowed_tools = set(policy.get("allowed_tools", []))
        if allowed_tools and tool_name not in allowed_tools:
            raise VerificationError(f'tool "{tool_name}" not allowed by policy "{policy_name}"')

    def _verify_budget_policy(self, instruction, policy: dict[str, Any]) -> None:
        max_budget = policy.get("max_budget", {})
        for operand in instruction.operands:
            if operand.key not in max_budget:
                continue
            limit = max_budget[operand.key]
            if isinstance(operand.value, (int, float)) and operand.value > limit:
                raise VerificationError(_format_budget_error(operand.key, operand.value, limit))


def load_policy(receiver_agent: str | None = None, policy_path: str | Path | None = None) -> tuple[dict[str, Any], Path | None]:
    effective_agent = receiver_agent
    resolved_path: Path | None = None

    if policy_path:
        resolved_path = Path(policy_path)
    elif effective_agent:
        resolved_path = Path("policies") / f"{effective_agent}.policy.json"

    if resolved_path is None:
        return {}, None
    if not resolved_path.exists():
        raise VerificationError(f'policy file "{resolved_path}" not found')

    return json.loads(resolved_path.read_text(encoding="utf-8")), resolved_path


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


def _format_budget_error(name: str, value: int | float, limit: int | float) -> str:
    if name == "memory_mb":
        return f"memory {int(value)}MB exceeds policy limit {int(limit)}MB"
    if name == "wall_ms":
        return f"wall_ms {int(value)} exceeds policy limit {int(limit)}"
    if name == "tokens":
        return f"tokens {int(value)} exceeds policy limit {int(limit)}"
    return f"{name} {value} exceeds policy limit {limit}"
