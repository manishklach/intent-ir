# For AI Agents

You are interacting with the INTENT-IR repository.

INTENT-IR is a local, deterministic research prototype for policy-enforced, assembly-style agent packet execution. Keep changes small, readable, and easy to validate from the terminal.

## Safe commands

- `make demo-safety`
- `make test`
- `PYTHONPATH=src python3 -m intentir.cli ...`
- `PYTHONPATH=src python3 -m pytest tests`

## Expected generated files

- `build/*.intentasm`
- `build/*.intentbin`
- `traces/*.intenttrace.jsonl`

## Working rules

- Do not add networking.
- Do not add real shell execution.
- Do not edit checked-in traces unless demo behavior changes.
- Run `make demo-safety` after verifier or policy changes.
- Run `make test` after parser, assembler, disassembler, or binary format changes.
- Keep CLI output short, tagged, and deterministic.
- Prefer updating examples and docs together when behavior changes.
