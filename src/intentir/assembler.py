from __future__ import annotations

from pathlib import Path

from .binary import Program, encode_program
from .intentasm_parser import parse_intentasm, parse_intentasm_file


def assemble_program(program: Program) -> bytes:
    return encode_program(program)


def assemble_intentasm(text: str) -> bytes:
    return assemble_program(parse_intentasm(text))


def assemble_file(path: str | Path) -> bytes:
    return assemble_program(parse_intentasm_file(path))
