import json

from intentir.agent_runtime import AgentRuntime
from intentir.assembler import assemble_file


def test_receiver_executes_valid_packet(tmp_path, capsys):
    binary_path = tmp_path / "repo_scan.intentbin"
    binary_path.write_bytes(assemble_file("examples/asm/repo_scan.intentasm"))
    trace_path = tmp_path / "repo_scan.intenttrace.jsonl"

    runtime = AgentRuntime(agent_name="worker", execute=True, trace_path=trace_path)
    result = runtime.recv_binary(binary_path)

    assert result["delivered"] is True
    assert result["executed"] is True
    assert result["executed_tools"] == ["repo.scan"]
    assert trace_path.exists()


def test_trace_replay_succeeds(tmp_path, capsys):
    binary_path = tmp_path / "hello.intentbin"
    binary_path.write_bytes(assemble_file("examples/asm/hello_agent.intentasm"))
    trace_path = tmp_path / "hello.intenttrace.jsonl"

    runtime = AgentRuntime(agent_name="worker", execute=True, trace_path=trace_path)
    runtime.recv_binary(binary_path)

    from intentir.trace import replay_trace

    entries = replay_trace(trace_path)
    captured = capsys.readouterr()

    assert len(entries) >= 1
    assert "[replay] succeeded" in captured.out
    first = json.loads(trace_path.read_text(encoding="utf-8").splitlines()[0])
    assert first["event"] in {"execute", "transport"}
