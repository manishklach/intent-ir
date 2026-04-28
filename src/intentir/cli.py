from __future__ import annotations

import argparse
from pathlib import Path

from .agent_runtime import AgentRuntime
from .assembler import assemble_file
from .disassembler import disassemble_file, render_intentasm
from .intentasm_parser import parse_intentasm_file
from .message_compiler import compile_message_file
from .trace import replay_trace
from .verifier import VerificationError, Verifier


def main() -> None:
    parser = argparse.ArgumentParser(description="INTENT-IR assembly-style agent packet toolchain")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_message_parser = subparsers.add_parser(
        "compile-message",
        help="Compile an agent message JSON document into IntentASM",
    )
    compile_message_parser.add_argument("input")
    compile_message_parser.add_argument("-o", "--output", required=True)

    asm_parser = subparsers.add_parser("asm", help="Assemble IntentASM into IntentBin")
    asm_parser.add_argument("input")
    asm_parser.add_argument("-o", "--output", required=True)

    disasm_parser = subparsers.add_parser("disasm", help="Disassemble IntentBin into IntentASM")
    disasm_parser.add_argument("input")
    disasm_parser.add_argument("-o", "--output", required=True)

    verify_parser = subparsers.add_parser("verify", help="Verify IntentASM")
    verify_parser.add_argument("input")

    recv_parser = subparsers.add_parser("recv", help="Receive an IntentBin packet")
    recv_parser.add_argument("input")
    recv_parser.add_argument("--agent", required=True)
    recv_parser.add_argument("--execute", action="store_true")
    recv_parser.add_argument("--trace")

    replay_parser = subparsers.add_parser("replay", help="Replay an execution trace")
    replay_parser.add_argument("input")

    args = parser.parse_args()

    if args.command == "compile-message":
        program = compile_message_file(args.input)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_intentasm(program), encoding="utf-8")
        print(f"[compile-message] wrote {output}")
        return

    if args.command == "asm":
        binary_blob = assemble_file(args.input)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(binary_blob)
        print(f"[asm] wrote {output}")
        return

    if args.command == "disasm":
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(disassemble_file(args.input), encoding="utf-8")
        print(f"[disasm] wrote {output}")
        return

    if args.command == "verify":
        program = parse_intentasm_file(args.input)
        Verifier().verify(program)
        print("[verify] verification passed")
        return

    if args.command == "recv":
        result = AgentRuntime(agent_name=args.agent, execute=args.execute, trace_path=args.trace).recv_binary(args.input)
        print(f"[recv] agent={args.agent} packet={Path(args.input).name}")
        print(f"[disasm] decoded {result['instruction_count']} instructions")
        if result.get("verified"):
            print("[verify] passed")
        else:
            print("[verify] failed")
            print(f"[reject] {result['error']}")
        if result.get("executed"):
            for tool_name in result.get("executed_tools", []):
                print(f"[execute] CALL {tool_name}")
            for artifact in result.get("committed_artifacts", []):
                print(f"[commit] {artifact}")
        else:
            print("[execute] skipped")
        if args.trace:
            print(f"[trace] wrote {args.trace}")
        return

    if args.command == "replay":
        replay_trace(args.input)
        return


if __name__ == "__main__":
    try:
        main()
    except VerificationError as exc:
        raise SystemExit(f"verification failed: {exc}")
