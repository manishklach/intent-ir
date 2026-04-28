import json

import pytest

from intentir.agent_runtime import AgentRuntime
from intentir.assembler import assemble_file
from intentir.intentasm_parser import parse_intentasm_file
from intentir.trace import replay_trace
from intentir.verifier import VerificationError, Verifier


def test_safe_repo_scan_verifies_successfully():
    program = parse_intentasm_file("examples/asm/safe_repo_scan.intentasm")

    assert Verifier().verify(program, receiver_agent="worker") is True


def test_safe_repo_scan_executes_repo_scan(tmp_path):
    binary_path = tmp_path / "safe_repo_scan.intentbin"
    binary_path.write_bytes(assemble_file("examples/asm/safe_repo_scan.intentasm"))
    trace_path = tmp_path / "safe_repo_scan.intenttrace.jsonl"

    result = AgentRuntime(agent_name="worker", execute=True, trace_path=trace_path).recv_binary(binary_path)

    assert result["verified"] is True
    assert result["executed"] is True
    assert result["executed_tools"] == ["repo.scan"]
    assert result["committed_artifacts"] == ["repo_scan.report"]


def test_unsafe_shell_fails_verification():
    program = parse_intentasm_file("examples/asm/unsafe_shell.intentasm")

    with pytest.raises(VerificationError, match='tool "shell.exec" is not allowed for agent "worker"'):
        Verifier().verify(program, receiver_agent="worker")


def test_unsafe_shell_does_not_execute_and_trace_contains_rejection(tmp_path):
    binary_path = tmp_path / "unsafe_shell.intentbin"
    binary_path.write_bytes(assemble_file("examples/asm/unsafe_shell.intentasm"))
    trace_path = tmp_path / "unsafe_shell.intenttrace.jsonl"

    result = AgentRuntime(agent_name="worker", execute=True, trace_path=trace_path).recv_binary(binary_path)

    assert result["verified"] is False
    assert result["executed"] is False
    entries = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    assert any(entry.get("outcome") == "reject" for entry in entries)
    assert any('shell.exec' in entry.get("message", "") for entry in entries)


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
