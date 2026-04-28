# INTENT-IR

**Deterministic, Inspectable Intermediate Representation for AI Agents.**

INTENT-IR is a research prototype for an execution substrate where agents emit structured intent instead of vague text. By compiling agent workflows into a verifiable IR, we enable:

- **Deterministic Execution**: Replay any agent run with bit-for-bit fidelity.
- **Verifiable Safety**: Use eBPF-style checks to enforce budgets and resource limits before execution.
- **Rich Observability**: Wireshark-style inspection of every instruction, tool call, and state transition.
- **Trace/Replay**: Trace generation for auditing and high-fidelity debugging.

---

## Quickstart

### Installation
```bash
make install
```

### Running a Demo
```bash
make demo
```

### Manual Usage
```bash
# Compile Agent IR (JSON) to INTENT-IR
intentir compile examples/repo_scan/task.json -o build/repo_scan.ir

# Assemble to Binary
intentir asm build/repo_scan.ir -o build/repo_scan.bin

# Run with Tracing
intentir run build/repo_scan.ir --trace traces/repo_scan.trace.jsonl

# Replay Trace
intentir replay traces/repo_scan.trace.jsonl
```

---

## Instruction Set Architecture (ISA)

INTENT-IR instructions are designed for the "Agent-Native" era:

- `DECLARE_AGENT`: Identity and capability declaration.
- `ALLOC_BUDGET`: Token and compute resource allocation.
- `CALL_TOOL`: Structured interface for external interaction.
- `ASSERT`: Verifiable state checks within the execution flow.
- `COMMIT`: Immutable recording of agent outputs.

---

## Architecture Pipeline

![Architecture](diagrams/architecture.svg)

1. **LLM** emits Agent IR (JSON).
2. **Compiler** lowers JSON to INTENT-IR instructions.
3. **Verifier** ensures the IR is safe and budgeted.
4. **Runtime** executes instructions and generates a `.trace` file.
5. **Human Auditor** inspects the trace via `intentir replay`.

---

## Comparison vs API-calling Agents

| Feature | API Agents | INTENT-IR Agents |
|---------|------------|------------------|
| Intent | Opaque Text | Structured IR |
| Verification | Post-hoc | Pre-execution |
| Replay | Impossible/Flaky | Deterministic |
| Budgeting | Soft-limits | Hard-enforcement |
| Inspectability | Log-based | Instruction-level |

---

## License
MIT
