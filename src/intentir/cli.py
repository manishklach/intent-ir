import argparse
import sys
import os
import json
from .compiler import compile_json
from .assembler import assemble
from .disassembler import disassemble, program_to_asm
from .packets import decode_program
from .runtime import Runtime
from .verifier import Verifier, VerificationError
from .trace import Tracer, Replayer

def main():
    parser = argparse.ArgumentParser(description="INTENT-IR Toolchain")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Compile
    compile_p = subparsers.add_parser("compile", help="Compile Agent IR (JSON) to INTENT-IR")
    compile_p.add_argument("input", help="Agent IR JSON file")
    compile_p.add_argument("-o", "--output", help="Output IR file", default="out.ir")

    # Asm
    asm_p = subparsers.add_parser("asm", help="Assemble IR to binary")
    asm_p.add_argument("input", help="IR file (JSON format)")
    asm_p.add_argument("-o", "--output", help="Output binary file", default="out.bin")

    # Disasm
    disasm_p = subparsers.add_parser("disasm", help="Disassemble binary to text")
    disasm_p.add_argument("input", help="Binary file")

    # Run
    run_p = subparsers.add_parser("run", help="Run IR program")
    run_p.add_argument("input", help="IR file (JSON format)")
    run_p.add_argument("--trace", help="Path to save trace")

    # Verify
    verify_p = subparsers.add_parser("verify", help="Verify IR program")
    verify_p.add_argument("input", help="IR file (JSON format)")

    # Replay
    replay_p = subparsers.add_parser("replay", help="Replay a trace file")
    replay_p.add_argument("input", help="Trace JSONL file")

    args = parser.parse_args()

    if args.command == "compile":
        program = compile_json(args.input)
        with open(args.output, 'w') as f:
            json.dump(program.to_dict(), f, indent=2)
        print(f"[*] Compiled {args.input} to {args.output}")

    elif args.command == "asm":
        with open(args.input, 'r') as f:
            data = json.load(f)
        # Convert dict back to Program object (simplified)
        from .ir import Program, Instruction, Opcode
        instructions = [Instruction(Opcode[i['op']], i['args'], i['meta']) for i in data['instructions']]
        program = Program(instructions=instructions, metadata=data.get('metadata', {}))
        binary = assemble(program)
        with open(args.output, 'wb') as f:
            f.write(binary)
        print(f"[*] Assembled {args.input} to {args.output}")

    elif args.command == "disasm":
        with open(args.input, 'rb') as f:
            data = f.read()
        print(disassemble(data))

    elif args.command == "run":
        with open(args.input, 'r') as f:
            data = json.load(f)
        from .ir import Program, Instruction, Opcode
        instructions = [Instruction(Opcode[i['op']], i['args'], i['meta']) for i in data['instructions']]
        program = Program(instructions=instructions, metadata=data.get('metadata', {}))
        
        tracer = Tracer() if args.trace else None
        runtime = Runtime(tracer=tracer)
        runtime.run(program)
        
        if args.trace:
            tracer.save(args.trace)
            print(f"[*] Trace saved to {args.trace}")

    elif args.command == "verify":
        with open(args.input, 'r') as f:
            data = json.load(f)
        from .ir import Program, Instruction, Opcode
        instructions = [Instruction(Opcode[i['op']], i['args'], i['meta']) for i in data['instructions']]
        program = Program(instructions=instructions, metadata=data.get('metadata', {}))
        
        verifier = Verifier()
        try:
            verifier.verify(program)
            print("[+] Program verified successfully")
        except VerificationError as e:
            print(f"[-] Verification failed: {e}")
            sys.exit(1)

    elif args.command == "replay":
        replayer = Replayer()
        replayer.replay(args.input)

if __name__ == "__main__":
    main()
