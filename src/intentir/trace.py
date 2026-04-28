import json
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

@dataclass
class TraceEntry:
    timestamp: float
    pc: int
    opcode: str
    args: List[Any]
    state_delta: Dict[str, Any]
    event: str = "exec"

class Tracer:
    def __init__(self):
        self.entries: List[TraceEntry] = []

    def record(self, pc: int, opcode: str, args: List[Any], delta: Dict[str, Any]):
        self.entries.append(TraceEntry(
            timestamp=time.time(),
            pc=pc,
            opcode=opcode,
            args=args,
            state_delta=delta
        ))

    def save(self, path: str):
        with open(path, 'w') as f:
            for entry in self.entries:
                f.write(json.dumps(asdict(entry)) + '\n')

class Replayer:
    def replay(self, trace_path: str):
        print(f"[*] Replaying trace: {trace_path}")
        with open(trace_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                print(f"[{entry['timestamp']:.4f}] PC={entry['pc']} OP={entry['opcode']} ARGS={entry['args']}")
                if entry['state_delta']:
                    print(f"    Delta: {entry['state_delta']}")
