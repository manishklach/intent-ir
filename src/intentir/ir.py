from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import List, Any, Dict, Optional

class Opcode(IntEnum):
    HALT = 0
    DECLARE_AGENT = 1
    DECLARE_TASK = 2
    ALLOC_BUDGET = 3
    REQUEST_RESOURCE = 4
    SEND = 5
    CALL_TOOL = 6
    WAIT = 7
    ASSERT = 8
    COMMIT = 9
    FAIL = 10
    TRACE = 11
    RELEASE = 12
    LOAD_CONST = 13
    LOG = 14

@dataclass
class Instruction:
    opcode: Opcode
    operands: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "op": self.opcode.name,
            "args": self.operands,
            "meta": self.metadata
        }

@dataclass
class Program:
    instructions: List[Instruction]
    version: str = "0.1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "version": self.version,
            "metadata": self.metadata,
            "instructions": [inst.to_dict() for inst in self.instructions]
        }
