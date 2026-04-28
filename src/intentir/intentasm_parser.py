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


def _tokenize_shorthand(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        if text[index] == "\"":
            token, index = _parse_string(text, index)
            tokens.append(token)
        elif text[index] == "{":
            token, index = _parse_balanced(text, index, "{", "}")
            tokens.append(token)
        elif text[index] == "[":
            token, index = _parse_balanced(text, index, "[", "]")
            tokens.append(token)
        else:
            start = index
            while index < len(text) and not text[index].isspace():
                index += 1
            tokens.append(text[start:index])
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


def _parse_keyword_pairs(tokens: list[str], start: int, keyword_map: dict[str, str] | None = None) -> list[Operand]:
    operands: list[Operand] = []
    keyword_map = keyword_map or {}
    index = start
    while index < len(tokens):
        if index + 1 >= len(tokens):
            raise IntentASMParseError(f"keyword '{tokens[index]}' is missing a value")
        keyword = tokens[index]
        key = keyword_map.get(keyword.upper(), keyword.lower())
        value = _parse_value(tokens[index + 1])
        if key in {"payload", "args"} and isinstance(value, str):
            value = PayloadRef(value)
        operands.append(Operand(key=key, value=value))
        index += 2
    return operands


def _parse_shorthand_operands(opcode_name: str, operand_text: str) -> list[Operand]:
    tokens = _tokenize_shorthand(operand_text)
    if not tokens:
        return []

    if opcode_name == "AGENT":
        return [Operand("name", _parse_value(tokens[0]))]

    if opcode_name == "TASK":
        operands = [Operand("id", _parse_value(tokens[0]))]
        operands.extend(
            _parse_keyword_pairs(tokens, 1, {"TYPE": "type", "KIND": "kind", "PRIORITY": "priority", "SUMMARY": "summary"})
        )
        return operands

    if opcode_name == "BUDGET":
        operands = [Operand("task", _parse_value(tokens[0]))]
        operands.extend(_parse_keyword_pairs(tokens, 1, {"MEMORY": "memory", "TIME": "time", "TOKENS": "tokens"}))
        return operands

    if opcode_name == "PAYLOAD":
        if len(tokens) < 3:
            raise IntentASMParseError("PAYLOAD shorthand requires name, format, and value")
        return [
            Operand("name", _parse_value(tokens[0])),
            Operand("format", str(_parse_value(tokens[1])).lower()),
            Operand("value", _parse_value(tokens[2])),
        ]

    if opcode_name == "SEND":
        operands = []
        if len(tokens) >= 2 and tokens[1].upper() not in {"CHANNEL", "PAYLOAD"}:
            operands.append(Operand("from", _parse_value(tokens[0])))
            operands.append(Operand("to", _parse_value(tokens[1])))
            start = 2
        else:
            operands.append(Operand("to", _parse_value(tokens[0])))
            start = 1
        operands.extend(_parse_keyword_pairs(tokens, start, {"CHANNEL": "channel", "PAYLOAD": "payload"}))
        return operands

    if opcode_name == "CALL":
        operands = []
        start = 0
        if len(tokens) >= 1 and tokens[0].upper() not in {"TOOL", "ARGS", "PAYLOAD", "MODE"}:
            operands.append(Operand("agent", _parse_value(tokens[0])))
            start = 1
        operands.extend(_parse_keyword_pairs(tokens, start, {"TOOL": "tool", "ARGS": "payload", "PAYLOAD": "payload", "MODE": "mode"}))
        return operands

    if opcode_name == "ASSERT":
        return [Operand("condition", operand_text.strip())]

    if opcode_name == "COMMIT":
        operands = [Operand("task", _parse_value(tokens[0]))]
        operands.extend(_parse_keyword_pairs(tokens, 1, {"ARTIFACT": "artifact", "STATUS": "status"}))
        return operands

    if opcode_name == "TRACE":
        if len(tokens) == 1:
            return [Operand("name", _parse_value(tokens[0]))]
        return _parse_keyword_pairs(tokens, 0, {"NAME": "name"})

    if opcode_name == "RELEASE":
        return [Operand("resource", _parse_value(tokens[0]))]

    if opcode_name == "FAIL":
        return [Operand("reason", operand_text.strip())]

    raise IntentASMParseError(f"unsupported shorthand syntax for opcode '{opcode_name}'")


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
        if operand_text:
            if _tokenize_shorthand(operand_text) and "=" in _tokenize_shorthand(operand_text)[0]:
                for token in _split_operand_tokens(operand_text):
                    key, value_token = token.split("=", 1)
                    operands.append(Operand(key=key, value=_parse_value(value_token)))
            else:
                operands = _parse_shorthand_operands(opcode_name, operand_text)
        instructions.append(Instruction(OPCODE_BY_NAME[opcode_name], operands))
    return Program(instructions=instructions)


def parse_intentasm_file(path: str | Path) -> Program:
    return parse_intentasm(Path(path).read_text(encoding="utf-8"))
