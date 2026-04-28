import json
from typing import Dict, Any, List
from .ir import Program, Instruction, Opcode

class Compiler:
    def compile(self, agent_ir: Dict[str, Any]) -> Program:
        instructions = []
        
        agent_id = agent_ir.get("agent_id", "default_agent")
        instructions.append(Instruction(Opcode.DECLARE_AGENT, [agent_id]))
        
        metadata = agent_ir.get("metadata", {})
        
        for step in agent_ir.get("workflow", []):
            step_type = step.get("type")
            
            if step_type == "init":
                instructions.append(Instruction(Opcode.DECLARE_TASK, [step.get("name")]))
            elif step_type == "budget":
                instructions.append(Instruction(Opcode.ALLOC_BUDGET, [step.get("amount"), step.get("currency", "tokens")]))
            elif step_type == "resource":
                instructions.append(Instruction(Opcode.REQUEST_RESOURCE, [step.get("path")]))
            elif step_type == "tool":
                instructions.append(Instruction(Opcode.CALL_TOOL, [step.get("name"), step.get("args", [])]))
            elif step_type == "wait":
                instructions.append(Instruction(Opcode.WAIT, [step.get("condition")]))
            elif step_type == "assert":
                instructions.append(Instruction(Opcode.ASSERT, [step.get("condition")]))
            elif step_type == "log":
                instructions.append(Instruction(Opcode.LOG, [step.get("message")]))
            elif step_type == "commit":
                instructions.append(Instruction(Opcode.COMMIT, [step.get("data")]))
            elif step_type == "fail":
                instructions.append(Instruction(Opcode.FAIL, [step.get("reason")]))
            elif step_type == "send":
                instructions.append(Instruction(Opcode.SEND, [step.get("to"), step.get("message")]))
        
        instructions.append(Instruction(Opcode.HALT))
        
        return Program(instructions=instructions, metadata=metadata)

def compile_json(json_path: str) -> Program:
    with open(json_path, 'r') as f:
        data = json.load(f)
    compiler = Compiler()
    return compiler.compile(data)
