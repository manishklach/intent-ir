# Demo Transcript

This is the canonical terminal transcript for:

```bash
make demo-safety
```

```text
1. compile safe message
[compile-message] wrote build/safe_repo_scan.intentasm
2. assemble safe packet
[asm] wrote build/safe_repo_scan.intentbin
3. recv/execute safe packet
[recv] agent=worker packet=safe_repo_scan.intentbin
[disasm] decoded 11 instructions
[policy] loaded policies/worker.policy.json
[verify] passed
[execute] CALL repo.scan
[commit] repo_scan.report
[trace] wrote traces/safe_repo_scan.intenttrace.jsonl
SAFE: allowed by policy
SAFE: executed
4. replay safe trace
[replay] succeeded with 14 events
5. compile unsafe shell message
[compile-message] wrote build/unsafe_shell.intentasm
6. assemble unsafe shell packet
[asm] wrote build/unsafe_shell.intentbin
7. recv unsafe shell packet
[recv] agent=worker packet=unsafe_shell.intentbin
[disasm] decoded 8 instructions
[policy] loaded policies/worker.policy.json
[verify] failed
[reject] tool "shell.exec" not allowed by policy "worker.policy.json"
[execute] skipped
[trace] wrote traces/unsafe_shell.intenttrace.jsonl
UNSAFE SHELL: rejected by policy
8. show shell verifier rejection
[reject-trace] verification failed
[reject-trace] rejected packet: tool "shell.exec" not allowed by policy "worker.policy.json"
9. replay unsafe shell trace
[replay] succeeded with 4 events
10. compile unsafe budget message
[compile-message] wrote build/unsafe_budget.intentasm
11. assemble unsafe budget packet
[asm] wrote build/unsafe_budget.intentbin
12. recv unsafe budget packet
[recv] agent=worker packet=unsafe_budget.intentbin
[disasm] decoded 10 instructions
[policy] loaded policies/worker.policy.json
[verify] failed
[reject] memory 2048MB exceeds policy limit 512MB
[execute] skipped
[trace] wrote traces/unsafe_budget.intenttrace.jsonl
UNSAFE BUDGET: rejected by policy
13. replay unsafe budget trace
[replay] succeeded with 4 events
```
