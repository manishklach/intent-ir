from pathlib import Path

from intentir.assembler import assemble_intentasm
from intentir.disassembler import disassemble_binary, render_intentasm
from intentir.message_compiler import compile_message_file


def test_assemble_disassemble_roundtrip():
    source = Path("examples/asm/repo_scan.intentasm").read_text(encoding="utf-8")
    binary_blob = assemble_intentasm(source)
    rendered = disassemble_binary(binary_blob)
    expected = source if source.endswith("\n") else source + "\n"

    assert rendered == expected


def test_disassembled_output_contains_call():
    source = Path("examples/asm/repo_scan.intentasm").read_text(encoding="utf-8")
    rendered = disassemble_binary(assemble_intentasm(source))

    assert 'CALL tool="repo.scan"' in rendered


def test_message_json_to_intentasm_matches_example():
    program = compile_message_file("examples/messages/repo_scan.json")
    rendered = render_intentasm(program)
    expected = Path("examples/asm/repo_scan.intentasm").read_text(encoding="utf-8")
    expected_rendered = expected if expected.endswith("\n") else expected + "\n"

    assert rendered == expected_rendered
