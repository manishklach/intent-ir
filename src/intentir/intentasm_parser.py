from __future__ import annotations

import json
from pathlib import Path

from .binary import Instruction, OPCODE_BY_NAME, Operand, PayloadRef, Program


class IntentASMParseError(ValueError):
    pass


def _parse_string(text: str, start: int) -> tuple[str, int]:
    escaped = False
    index = start + 1
    while index < len(text):
        char = text[index]
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "\"":
            return text[start:index + 1], index + 1
        index += 1
    raise IntentASMParseError("unterminated string literal")


def _parse_balanced(text: str, start: int, open_char: str, close_char: str) -> tuple[str, int]:
    depth = 1
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "\"":
            _, index = _parse_string(text, index)
            continue
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return text[start:index + 1], index + 1
        index += 1
    raise IntentASMParseError(f"unterminated {open_char}{close_char} expression")


def _split_operand_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        start = index
        while index < len(text) and text[index] != "=":
            index += 1
        if index >= len(text):
            raise IntentASMParseError("operand is missing '=' separator")
        key = text[start:index].strip()
        if not key:
            raise IntentASMParseError("operand key cannot be empty")
        index += 1
        if index >= len(text):
            raise IntentASMParseError(f"operand '{key}' is missing a value")
        if text[index] == "\"":
            value_token, index = _parse_string(text, index)
        elif text[index] == "{":
            value_token, index = _parse_balanced(text, index, "{", "}")
        elif text[index] == "[":
            value_token, index = _parse_balanced(text, index, "[", "]")
        else:
            value_start = index
            while index < len(text) and not text[index].isspace():
                index += 1
            value_token = text[value_start:index]
        tokens.append(f"{key}={value_token}")
    return tokens


def _parse_value(token: str):
    if token.startswith("@"):
        return PayloadRef(token[1:])
    if token.startswith("\""):
        return json.loads(token)
    if token.startswith("{") or token.startswith("["):
        return json.loads(token)
    if token in {"true", "false", "null"}:
        return json.loads(token)
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token


def parse_intentasm(text: str) -> Program:
    instructions: list[Instruction] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#", 1)[0].rstrip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        opcode_name = parts[0].upper()
        if opcode_name not in OPCODE_BY_NAME:
            raise IntentASMParseError(f"line {line_number}: unknown opcode '{opcode_name}'")
        operand_text = parts[1] if len(parts) > 1 else ""
        operands: list[Operand] = []
        for token in _split_operand_tokens(operand_text):
            key, value_token = token.split("=", 1)
            operands.append(Operand(key=key, value=_parse_value(value_token)))
        instructions.append(Instruction(OPCODE_BY_NAME[opcode_name], operands))
    return Program(instructions=instructions)


def parse_intentasm_file(path: str | Path) -> Program:
    return parse_intentasm(Path(path).read_text(encoding="utf-8"))
