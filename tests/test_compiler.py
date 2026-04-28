import pytest
import json
import os
from intentir.compiler import Compiler
from intentir.ir import Opcode

def test_compile_basic():
    agent_ir = {
        "agent_id": "test-agent",
        "workflow": [
            { "type": "init", "name": "test-task" },
            { "type": "log", "message": "hello" }
        ]
    }
    compiler = Compiler()
    program = compiler.compile(agent_ir)
    
    assert program.instructions[0].opcode == Opcode.DECLARE_AGENT
    assert program.instructions[0].operands == ["test-agent"]
    assert program.instructions[1].opcode == Opcode.DECLARE_TASK
    assert program.instructions[2].opcode == Opcode.LOG
    assert program.instructions[-1].opcode == Opcode.HALT
