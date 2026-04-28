from __future__ import annotations

import os
import subprocess
import sys


def test_demo_safety_path_components_work(tmp_path):
    env = dict(os.environ)
    env["PYTHONPATH"] = "src"

    safe_asm = tmp_path / "safe.intentasm"
    safe_bin = tmp_path / "safe.intentbin"
    safe_trace = tmp_path / "safe.intenttrace.jsonl"

    commands = [
        [sys.executable, "-m", "intentir.cli", "compile-message", "examples/messages/safe_repo_scan.json", "-o", str(safe_asm)],
        [sys.executable, "-m", "intentir.cli", "asm", str(safe_asm), "-o", str(safe_bin)],
        [sys.executable, "-m", "intentir.cli", "recv", str(safe_bin), "--agent", "worker", "--policy", "policies/worker.policy.json", "--execute", "--trace", str(safe_trace)],
        [sys.executable, "-m", "intentir.cli", "replay", str(safe_trace)],
    ]

    outputs: list[str] = []
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=".",
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        outputs.append(completed.stdout)

    combined = "\n".join(outputs)
    assert "[compile-message]" in combined
    assert "[asm]" in combined
    assert "[policy] loaded policies/worker.policy.json" in combined
    assert "[verify] passed" in combined
    assert "[execute] CALL repo.scan" in combined
    assert "[trace] wrote" in combined
    assert "[replay] succeeded" in combined
