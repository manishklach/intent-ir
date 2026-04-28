# IntentASM v0.1

IntentASM is the textual assembly format for INTENT-IR. It exists to make agent instruction packets reviewable before they are assembled into `IntentBin`.

## Scope

IntentASM is intentionally small:

- one instruction per line
- uppercase opcode mnemonic
- canonical `key=value` operands for stable disassembly
- optional shorthand assembly input for common packet forms
- JSON values for structured payloads
- `@payload_name` references for named payload reuse

The format is designed for research, debugging, and review. It is not positioned as a final standard.

## Example

```text
AGENT name="planner"
TASK id="repo-scan" kind="analysis" priority="normal" summary="Scan repository layout"
BUDGET tokens=1200 memory_mb=256 wall_ms=1500
PAYLOAD name="scan_request" format="json" value={"depth":"shallow","root":"src"}
SEND to="worker"
CALL tool="repo.scan" payload=@scan_request mode="sync"
TRACE name="repo_scan_trace"
COMMIT status="delegated"
HALT
```

The parser also accepts a more assembly-shaped shorthand input for common packet forms:

```text
AGENT planner
TASK t1 TYPE "repo_scan"
BUDGET t1 MEMORY 512MB TIME 30000MS TOKENS 4096
PAYLOAD p1 JSON {"repo":".","include":["*.md","*.py"]}
SEND planner worker CHANNEL "task" PAYLOAD p1
CALL worker TOOL "repo.scan" ARGS p1
ASSERT LAST.status == "ok"
COMMIT t1 ARTIFACT "repo_summary.json"
HALT
```

The disassembler emits canonical `key=value` output even when shorthand input is accepted.

## Syntax rules

- Comments begin with `#`.
- Strings use JSON quoting.
- Dictionaries and arrays use JSON syntax.
- Bare numbers, booleans, and `null` are accepted.
- `@name` means "reference the payload previously declared as `name`."

## Verification expectations

The reference verifier in this repository currently checks:

- the program begins with `AGENT`
- the program ends with `HALT`
- `CALL` appears only after `TASK` and `SEND`
- payload references point to previously declared `PAYLOAD` instructions

Those rules are intentionally conservative. More policy can be layered on later, but the base packet should stay readable.
