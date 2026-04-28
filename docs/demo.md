# Demo

The safety demo shows the value of verifiable agent packets.

## Why this matters

- Normal tool-calling often lets an agent request arbitrary tools without a deterministic receiver-side policy gate.
- INTENT-IR makes the request inspectable before execution because the packet can be disassembled and verified first.
- The receiver can reject unsafe packets deterministically instead of relying on prompt behavior.
- The trace proves whether execution happened or whether the packet was rejected before any call ran.

## Demo flow

Run:

```bash
make demo-safety
```

The demo sends two packets from a planner agent to a worker agent:

1. `safe_repo_scan`
   - calls `repo.scan`
   - passes verification
   - executes
   - commits `repo_scan.report`
2. `unsafe_shell`
   - attempts `shell.exec`
   - fails verification
   - is not executed
   - writes a rejection event to trace
3. `unsafe_budget`
   - uses an allowed tool
   - exceeds `worker.policy.json` memory budget
   - fails verification before execution
   - writes a rejection event to trace

## Expected terminal shape

Safe packet:

```text
[recv] agent=worker packet=safe_repo_scan.intentbin
[disasm] decoded 11 instructions
[policy] loaded policies/worker.policy.json
[verify] passed
[execute] CALL repo.scan
[commit] repo_scan.report
[trace] wrote traces/safe_repo_scan.intenttrace.jsonl
```

Unsafe packet:

```text
[recv] agent=worker packet=unsafe_shell.intentbin
[disasm] decoded 8 instructions
[policy] loaded policies/worker.policy.json
[verify] failed
[reject] tool "shell.exec" not allowed by policy "worker.policy.json"
[execute] skipped
[trace] wrote traces/unsafe_shell.intenttrace.jsonl
```

Budget overflow:

```text
[recv] agent=worker packet=unsafe_budget.intentbin
[disasm] decoded 10 instructions
[policy] loaded policies/worker.policy.json
[verify] failed
[reject] memory 2048MB exceeds policy limit 512MB
[execute] skipped
[trace] wrote traces/unsafe_budget.intenttrace.jsonl
```

Replay then confirms whether the packet executed or was rejected.
