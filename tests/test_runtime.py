import pytest
from intentir.ir import Program, Instruction, Opcode
from intentir.runtime import Runtime

def test_runtime_basic():
    prog = Program([
        Instruction(Opcode.DECLARE_AGENT, ["bot"]),
        Instruction(Opcode.LOG, ["hello"]),
        Instruction(Opcode.HALT)
    ])
    runtime = Runtime()
    state = runtime.run(prog)
    
    assert state["agent"] == "bot"
    assert state["status"] == "halted"
    assert "hello" in state["logs"]

def test_runtime_fail():
    prog = Program([
        Instruction(Opcode.DECLARE_AGENT, ["bot"]),
        Instruction(Opcode.FAIL, ["critical error"])
    ])
    runtime = Runtime()
    state = runtime.run(prog)
    
    assert state["status"] == "failed"
    assert state["error"] == "critical error"
