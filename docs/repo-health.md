# Repo Health

## Checklist

- `make demo-safety`
- `make test`
- `python3` is the default interpreter in the Makefile
- WSL/Linux is the expected path for `make`
- `pytest` must be installed for `make test`
- canonical traces:
  - `traces/safe_repo_scan.intenttrace.jsonl`
  - `traces/unsafe_shell.intenttrace.jsonl`
  - `traces/unsafe_budget.intenttrace.jsonl`

## Notes

- If `make demo-safety` changes behavior, refresh the checked-in traces.
- If parser or binary roundtrip behavior changes, run `make test` before updating traces.
- `make demo-safety` is the primary launch-readiness check.
