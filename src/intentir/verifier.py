from typing import List, Dict, Any
from .ir import Program, Opcode

class VerificationError(Exception):
    pass

class Verifier:
    def verify(self, program: Program):
        if not program.instructions:
            raise VerificationError("Empty program")
        
        has_agent = False
        has_halt = False
        budget_allocated = False
        
        for i, inst in enumerate(program.instructions):
            if inst.opcode == Opcode.DECLARE_AGENT:
                has_agent = True
            elif inst.opcode == Opcode.HALT:
                has_halt = True
            elif inst.opcode == Opcode.ALLOC_BUDGET:
                budget_allocated = True
            elif inst.opcode == Opcode.CALL_TOOL:
                # Basic rule: Tools need budgets (hypothetical constraint)
                # if not budget_allocated:
                #    raise VerificationError(f"Instruction {i}: CALL_TOOL requires prior ALLOC_BUDGET")
                pass
                
        if not has_agent:
            raise VerificationError("Program must start with DECLARE_AGENT")
        if not has_halt:
            raise VerificationError("Program must end with HALT")
            
        return True
