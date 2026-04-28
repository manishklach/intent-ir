# INTENT-IR

Assembly-style communication layer for AI agents — compile messages into verifiable, replayable instruction packets.

Agents shouldn’t blindly execute requests. INTENT-IR lets them disassemble, verify, reject, execute, trace, and replay agent packets.

## Demo: safe vs unsafe packets

```bash
make demo-safety
```

```text
[recv] agent=worker packet=safe_repo_scan.intentbin
[policy] loaded policies/worker.policy.json
[verify] passed
[execute] CALL repo.scan
[commit] repo_scan.report

[recv] agent=worker packet=unsafe_shell.intentbin
[policy] loaded policies/worker.policy.json
[verify] failed
[reject] tool "shell.exec" not allowed by policy "worker.policy.json"

[recv] agent=worker packet=unsafe_budget.intentbin
[policy] loaded policies/worker.policy.json
[verify] failed
[reject] memory 2048MB exceeds policy limit 512MB
```

See the polished terminal transcript in [docs/demo-output.txt](docs/demo-output.txt).
See the full canonical transcript in [docs/demo-transcript.md](docs/demo-transcript.md).

## Status

INTENT-IR is a research prototype.

The ISA, binary format, verifier rules, and policy files are intentionally small and explicit so they can be inspected, debated, and extended. This repository is not presented as production-ready agent middleware.

## Why this exists

Most agent systems still communicate through natural language transcripts or opaque tool invocations.

That is flexible, but it leaves important questions unanswered:

- What exactly did the sender ask the receiver to do?
- Which payload was referenced by the tool call?
- Was the packet structurally valid before execution?
- Can the same receiver behavior be replayed later?

INTENT-IR answers those questions with a small instruction set, an inspectable assembly format, and a policy-enforced receiver.

## The Assembly Path

```text
Agent Message JSON
  -> compile-message
IntentASM
  -> asm
IntentBin
  -> disasm / recv / verify
Verified Receiver Execution
  -> trace
Replayable Trace
```

The sender-side flow turns a JSON message into human-readable IntentASM, then into a compact `IntentBin` packet.

The receiver can disassemble the packet for inspection, verify it before execution, and record a replayable trace when it runs the packet.

## Policy Enforcement

INTENT-IR does not rely on implicit trust.

Each agent enforces an explicit execution policy:

- allowed tools
- resource limits
- required invariants

Packets are verified against policy before execution.

If `--policy` is omitted on `recv`, INTENT-IR auto-loads `policies/{agent}.policy.json`.

Example `worker.policy.json`:

```json
{
  "allowed_tools": ["repo.scan", "artifact.write", "trace.emit"],
  "denied_tools": ["shell.exec", "file.delete", "network.post", "secrets.read"],
  "max_budget": {
    "memory_mb": 512,
    "tokens": 5000,
    "wall_ms": 5000
  },
  "require_asserts": true,
  "require_commit": true
}
```

## Quickstart

Install the package in editable mode:

```bash
pip install -e .
```

Run the assembly path end to end:

```bash
intentir compile-message examples/messages/repo_scan.json -o build/repo_scan.intentasm
intentir asm build/repo_scan.intentasm -o build/repo_scan.intentbin
intentir disasm build/repo_scan.intentbin -o build/repo_scan.disasm.intentasm
intentir verify build/repo_scan.intentasm --agent worker --policy policies/worker.policy.json
intentir recv build/repo_scan.intentbin --agent worker --policy policies/worker.policy.json --execute --trace traces/repo_scan.intenttrace.jsonl
intentir replay traces/repo_scan.intenttrace.jsonl
```

If you are on WSL or Linux, `python3` is the default interpreter used by the Makefile.

## Demo Targets

Run the launch-ready safety demo:

```bash
make demo-safety
```

Run the broader sender-to-receiver flow:

```bash
make demo
```

Run the test suite:

```bash
make test
```

## Repository Layout

```text
spec/                Language, opcode, schema, and binary format docs
src/intentir/        Parser, assembler, verifier, runtime, trace, and CLI
examples/messages/   Example agent messages in JSON
examples/asm/        Example IntentASM programs
policies/            Agent policy JSON files
tests/               Parser, roundtrip, verifier, runtime, and replay tests
traces/              Canonical demo traces
docs/                Demo transcripts and repo health notes
```

## Example Packet

The `examples/messages/repo_scan.json` message compiles to an assembly packet in `examples/asm/repo_scan.intentasm` with explicit sender, task, budget, payload, send, call, trace, commit, and halt instructions.

The binary encoding preserves those instructions with opcode records and a payload table, while the verifier enforces structural and policy rules before execution.

## Design Constraints

- Compact instruction packets over free-form execution requests
- Verifiable sender intent before receiver execution
- Stable roundtrip from `.intentasm` to `.intentbin` and back
- Replay-first runtime traces for postmortem analysis
- Minimal claims: verification and replayability are in scope; production-hardening is not

## Specs

- [spec/intentasm-v0.1.md](spec/intentasm-v0.1.md)
- [spec/opcodes.md](spec/opcodes.md)
- [spec/binary-format.md](spec/binary-format.md)
- [spec/message-schema.json](spec/message-schema.json)

## Docs

- [docs/demo-output.txt](docs/demo-output.txt)
- [docs/demo-transcript.md](docs/demo-transcript.md)
- [docs/demo.md](docs/demo.md)
- [docs/repo-health.md](docs/repo-health.md)

## License

MIT
