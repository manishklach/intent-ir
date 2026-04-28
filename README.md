# INTENT-IR

Assembly-style communication layer for AI agents — compile messages into verifiable, replayable instruction packets.

INTENT-IR is an assembly-style communication layer for AI agents.

Agents should be able to send small verifiable instruction packets to other agents. The receiver can disassemble, verify, execute, trace, and replay exactly what happened.

INTENT-IR is a research prototype for agent-to-agent communication. The repository treats an agent message as a compact instruction packet that can be compiled, assembled, verified, executed by a receiver runtime, and replayed from trace. The goal is not to replace every text exchange between agents. The goal is to make high-value handoffs inspectable, bounded, and reproducible.

## Why assembly-style packets

Most agent systems still communicate through natural language transcripts or opaque tool invocations. That is flexible, but it also leaves important questions unanswered:

- What exactly did the sender ask the receiver to do?
- Which payload was referenced by the tool call?
- Was the packet structurally valid before execution?
- Can the same receiver behavior be replayed later?

INTENT-IR answers those questions with a small instruction set and a binary packet format designed for verification and auditability.

## Status

INTENT-IR is a research-prototype assembly pipeline. The ISA, binary format, and verifier rules are intentionally small and explicit so they can be inspected, debated, and extended. This repository is not presented as production-ready agent middleware.

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

The sender-side flow turns a JSON message into human-readable IntentASM, then into a compact `IntentBin` packet. The receiver can disassemble the packet for inspection, verify it before execution, and record a replayable trace when it runs the packet.

## Killer Demo: Verifiable Agent Packets

Run:

```bash
make demo-safety
```

This demo shows a planner agent sending two packets to a worker agent:

- `safe_repo_scan` passes verification, executes `CALL repo.scan`, commits `repo_scan.report`, and writes a trace.
- `unsafe_shell` is rejected deterministically because `shell.exec` is not allowed for `worker`, is not executed, and writes a rejection trace.

Expected output:

```text
[recv] agent=worker packet=safe_repo_scan.intentbin
[disasm] decoded 11 instructions
[verify] passed
[execute] CALL repo.scan
[commit] repo_scan.report
[trace] wrote traces/safe_repo_scan.intenttrace.jsonl

[recv] agent=worker packet=unsafe_shell.intentbin
[disasm] decoded 8 instructions
[verify] failed
[reject] tool "shell.exec" is not allowed for agent "worker"
[execute] skipped
[trace] wrote traces/unsafe_shell.intenttrace.jsonl
```

## Repository layout

```text
spec/                Language, opcode, schema, and binary format docs
src/intentir/        Parser, assembler, verifier, runtime, trace, and CLI
examples/messages/   Example agent messages in JSON
examples/asm/        Example IntentASM programs
tests/               Parser, roundtrip, verifier, runtime, and replay tests
traces/              Example output location for execution traces
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
intentir verify build/repo_scan.intentasm
intentir recv build/repo_scan.intentbin --agent worker --execute --trace traces/repo_scan.intenttrace.jsonl
intentir replay traces/repo_scan.intenttrace.jsonl
```

## Demo

Run the full sender-to-receiver flow:

```bash
make demo
```

The demo prints:

1. compiled assembly
2. binary packet created
3. disassembly
4. verification passed
5. receiver executed CALL
6. trace written
7. replay succeeded

## Example packet

The `examples/messages/repo_scan.json` message compiles to an assembly packet in `examples/asm/repo_scan.intentasm` with explicit sender, task, budget, payload, send, call, trace, commit, and halt instructions. The binary encoding preserves those instructions with opcode records and a payload table, while the verifier enforces basic structural rules before execution.

## Design constraints

- Compact instruction packets over free-form execution requests
- Verifiable sender intent before receiver execution
- Stable roundtrip from `.intentasm` to `.intentbin` and back
- Replay-first runtime traces for postmortem analysis
- Minimal claims: verification and replayability are in scope; production-hardening is not

## Specification entry points

- [spec/intentasm-v0.1.md](/C:/Users/ManishKL/Documents/Playground/intent-ir/spec/intentasm-v0.1.md)
- [spec/opcodes.md](/C:/Users/ManishKL/Documents/Playground/intent-ir/spec/opcodes.md)
- [spec/binary-format.md](/C:/Users/ManishKL/Documents/Playground/intent-ir/spec/binary-format.md)
- [spec/message-schema.json](/C:/Users/ManishKL/Documents/Playground/intent-ir/spec/message-schema.json)

## License

MIT
