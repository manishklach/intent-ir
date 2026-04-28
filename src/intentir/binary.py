from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

MAGIC = b"IASM"
VERSION = 1
HEADER_STRUCT = struct.Struct("<4sB3xII32s")
INSTRUCTION_HEADER_STRUCT = struct.Struct("<BBBB")
OPERAND_REF_STRUCT = struct.Struct("<HH")
PAYLOAD_COUNT_STRUCT = struct.Struct("<I")
PAYLOAD_LEN_STRUCT = struct.Struct("<I")


class Opcode(IntEnum):
    AGENT = 0x01
    TASK = 0x02
    BUDGET = 0x03
    PAYLOAD = 0x04
    SEND = 0x05
    CALL = 0x06
    ASSERT = 0x07
    COMMIT = 0x08
    FAIL = 0x09
    TRACE = 0x0A
    RELEASE = 0x0B
    HALT = 0xFF


OPCODE_BY_NAME = {opcode.name: opcode for opcode in Opcode}


@dataclass(frozen=True)
class PayloadRef:
    name: str


@dataclass
class Operand:
    key: str
    value: Any


@dataclass
class Instruction:
    opcode: Opcode
    operands: list[Operand] = field(default_factory=list)


@dataclass
class Program:
    instructions: list[Instruction]


def _value_to_jsonable(value: Any) -> Any:
    if isinstance(value, PayloadRef):
        return {"__intentir_payload_ref__": value.name}
    return value


def _jsonable_to_value(value: Any) -> Any:
    if isinstance(value, dict) and "__intentir_payload_ref__" in value:
        return PayloadRef(str(value["__intentir_payload_ref__"]))
    return value


def _canonical_blob(value: Any) -> bytes:
    return json.dumps(_value_to_jsonable(value), sort_keys=True, separators=(",", ":")).encode("utf-8")


def _decode_blob(blob: bytes) -> Any:
    return _jsonable_to_value(json.loads(blob.decode("utf-8")))


def encode_program(program: Program) -> bytes:
    payload_index: dict[bytes, int] = {}
    payload_values: list[bytes] = []

    def intern(value: Any) -> int:
        blob = _canonical_blob(value)
        if blob not in payload_index:
            payload_index[blob] = len(payload_values)
            payload_values.append(blob)
        return payload_index[blob]

    instruction_chunks: list[bytes] = []
    for instruction in program.instructions:
        operand_count = len(instruction.operands)
        instruction_chunks.append(
            INSTRUCTION_HEADER_STRUCT.pack(int(instruction.opcode), operand_count, 0, 0)
        )
        for operand in instruction.operands:
            key_ref = intern(operand.key)
            value_ref = intern(operand.value)
            instruction_chunks.append(OPERAND_REF_STRUCT.pack(key_ref, value_ref))

    instruction_blob = b"".join(instruction_chunks)

    payload_chunks = [PAYLOAD_COUNT_STRUCT.pack(len(payload_values))]
    for blob in payload_values:
        payload_chunks.append(PAYLOAD_LEN_STRUCT.pack(len(blob)))
        payload_chunks.append(blob)
    payload_blob = b"".join(payload_chunks)

    payload_table_offset = HEADER_STRUCT.size + len(instruction_blob)
    body = instruction_blob + payload_blob
    checksum = hashlib.sha256(body).digest()
    header = HEADER_STRUCT.pack(
        MAGIC,
        VERSION,
        len(program.instructions),
        payload_table_offset,
        checksum,
    )
    return header + body


def decode_program(data: bytes) -> Program:
    if len(data) < HEADER_STRUCT.size:
        raise ValueError("binary too short to contain IntentBin header")

    magic, version, instruction_count, payload_table_offset, checksum = HEADER_STRUCT.unpack_from(data, 0)
    if magic != MAGIC:
        raise ValueError("invalid IntentBin magic")
    if version != VERSION:
        raise ValueError(f"unsupported IntentBin version: {version}")
    if payload_table_offset > len(data):
        raise ValueError("payload table offset points outside the packet")

    body = data[HEADER_STRUCT.size:]
    actual_checksum = hashlib.sha256(body).digest()
    if checksum != actual_checksum:
        raise ValueError("IntentBin checksum mismatch")

    payload_section_offset = payload_table_offset
    cursor = HEADER_STRUCT.size
    payload_cursor = payload_section_offset
    payload_count = PAYLOAD_COUNT_STRUCT.unpack_from(data, payload_cursor)[0]
    payload_cursor += PAYLOAD_COUNT_STRUCT.size

    payload_table: list[Any] = []
    for _ in range(payload_count):
        payload_len = PAYLOAD_LEN_STRUCT.unpack_from(data, payload_cursor)[0]
        payload_cursor += PAYLOAD_LEN_STRUCT.size
        payload_blob = data[payload_cursor:payload_cursor + payload_len]
        payload_cursor += payload_len
        payload_table.append(_decode_blob(payload_blob))

    instructions: list[Instruction] = []
    for _ in range(instruction_count):
        opcode_value, operand_count, _, _ = INSTRUCTION_HEADER_STRUCT.unpack_from(data, cursor)
        cursor += INSTRUCTION_HEADER_STRUCT.size
        operands: list[Operand] = []
        for _ in range(operand_count):
            key_ref, value_ref = OPERAND_REF_STRUCT.unpack_from(data, cursor)
            cursor += OPERAND_REF_STRUCT.size
            try:
                key = payload_table[key_ref]
                value = payload_table[value_ref]
            except IndexError as exc:
                raise ValueError("operand references invalid payload table entry") from exc
            operands.append(Operand(str(key), value))
        instructions.append(Instruction(Opcode(opcode_value), operands))

    return Program(instructions=instructions)
