from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .binary import PayloadRef


def _jsonable(value: Any) -> Any:
    if isinstance(value, PayloadRef):
        return {"payload_ref": value.name}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(val) for key, val in value.items()}
    return value


class TraceWriter:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("w", encoding="utf-8")

    def record(self, event: dict[str, Any]) -> None:
        payload = dict(event)
        payload.setdefault("timestamp", time.time())
        self.handle.write(json.dumps(_jsonable(payload), sort_keys=True) + "\n")
        self.handle.flush()

    def close(self) -> None:
        if not self.handle.closed:
            self.handle.close()


def replay_trace(path: str | Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            entry = json.loads(line)
            entries.append(entry)
            message = entry.get("message") or entry.get("opcode")
            detail = entry.get("outcome") or entry.get("opcode") or entry.get("event")
            print(f"[replay] pc={entry.get('pc')} event={entry.get('event')} detail={detail} message={message}")
    print(f"[replay] succeeded with {len(entries)} events")
    return entries
