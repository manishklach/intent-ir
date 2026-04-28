import json
from pathlib import Path

import pytest

from intentir.agent_runtime import AgentRuntime
from intentir.assembler import assemble_file
from intentir.intentasm_parser import parse_intentasm_file
from intentir.trace import replay_trace
from intentir.verifier import VerificationError, Verifier, load_policy


WORKER_POLICY, WORKER_POLICY_PATH = load_policy("worker")


def test_policy_allows_safe_packet():
    program = parse_intentasm_file("examples/asm/safe_repo_scan.intentasm")

    assert Verifier().verify(
        program,
        receiver_agent="worker",
        policy=WORKER_POLICY,
        policy_name=WORKER_POLICY_PATH.name,
    ) is True


def test_safe_repo_scan_executes_repo_scan(tmp_path):
    binary_path = tmp_path / "safe_repo_scan.intentbin"
    binary_path.write_bytes(assemble_file("examples/asm/safe_repo_scan.intentasm"))
    trace_path = tmp_path / "safe_repo_scan.intenttrace.jsonl"

    result = AgentRuntime(agent_name="worker", execute=True, trace_path=trace_path).recv_binary(binary_path)

    assert result["verified"] is True
    assert result["executed"] is True
    assert result["executed_tools"] == ["repo.scan"]
    assert result["committed_artifacts"] == ["repo_scan.report"]


def test_policy_rejects_shell_exec():
    program = parse_intentasm_file("examples/asm/unsafe_shell.intentasm")

    with pytest.raises(VerificationError, match='tool "shell.exec" not allowed by policy "worker.policy.json"'):
        Verifier().verify(
            program,
            receiver_agent="worker",
            policy=WORKER_POLICY,
            policy_name=WORKER_POLICY_PATH.name,
        )


def test_unsafe_shell_does_not_execute_and_trace_contains_rejection(tmp_path):
    binary_path = tmp_path / "unsafe_shell.intentbin"
    binary_path.write_bytes(assemble_file("examples/asm/unsafe_shell.intentasm"))
    trace_path = tmp_path / "unsafe_shell.intenttrace.jsonl"

    result = AgentRuntime(agent_name="worker", execute=True, trace_path=trace_path).recv_binary(binary_path)

    assert result["verified"] is False
    assert result["executed"] is False
    entries = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    assert any(entry.get("event") == "REJECT" for entry in entries)
    assert any(entry.get("reason") == "policy_violation" for entry in entries)
    assert any(entry.get("detail") == "tool shell.exec not allowed" for entry in entries)


def test_policy_rejects_budget_overflow():
    program = parse_intentasm_file("examples/asm/unsafe_budget.intentasm")

    with pytest.raises(VerificationError, match="memory 2048MB exceeds policy limit 512MB"):
        Verifier().verify(
            program,
            receiver_agent="worker",
            policy=WORKER_POLICY,
            policy_name=WORKER_POLICY_PATH.name,
        )


def test_policy_requires_assert():
    program = parse_intentasm_file("examples/asm/hello_agent.intentasm")

    with pytest.raises(VerificationError, match="missing ASSERT instruction \\(policy requires asserts\\)"):
        Verifier().verify(
            program,
            receiver_agent="worker",
            policy=WORKER_POLICY,
            policy_name=WORKER_POLICY_PATH.name,
        )


def test_policy_requires_commit():
    program_text = Path("examples/asm/safe_repo_scan.intentasm").read_text(encoding="utf-8").replace(
        'COMMIT status="delegated" artifact="repo_scan.report"\n',
        "",
    )
    from intentir.intentasm_parser import parse_intentasm

    program = parse_intentasm(program_text)

    with pytest.raises(VerificationError, match="missing COMMIT instruction \\(policy requires commit\\)"):
        Verifier().verify(
            program,
            receiver_agent="worker",
            policy=WORKER_POLICY,
            policy_name=WORKER_POLICY_PATH.name,
        )


def test_replay_works_for_both_traces(tmp_path):
    safe_binary = tmp_path / "safe.intentbin"
    safe_binary.write_bytes(assemble_file("examples/asm/safe_repo_scan.intentasm"))
    safe_trace = tmp_path / "safe.intenttrace.jsonl"
    AgentRuntime(agent_name="worker", execute=True, trace_path=safe_trace).recv_binary(safe_binary)

    unsafe_binary = tmp_path / "unsafe.intentbin"
    unsafe_binary.write_bytes(assemble_file("examples/asm/unsafe_shell.intentasm"))
    unsafe_trace = tmp_path / "unsafe.intenttrace.jsonl"
    AgentRuntime(agent_name="worker", execute=True, trace_path=unsafe_trace).recv_binary(unsafe_binary)

    safe_entries = replay_trace(safe_trace)
    unsafe_entries = replay_trace(unsafe_trace)

    assert len(safe_entries) >= 1
    assert len(unsafe_entries) >= 1
