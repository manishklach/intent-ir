import struct
import json
import hashlib
from .ir import Program, Instruction, Opcode

MAGIC = b"INTENTIR"
VERSION = 1

def encode_program(program: Program) -> bytes:
    # Header: Magic(8) + Version(2) + MetadataLen(4) + Metadata(N) + InstCount(4)
    meta_json = json.dumps(program.metadata).encode('utf-8')
    header = struct.pack("<8sH I", MAGIC, VERSION, len(meta_json))
    
    # Instructions and Payloads
    # We'll store operands as indexes into a payload table to keep instruction size uniformish
    payload_table = []
    def get_payload_id(val):
        if val in payload_table:
            return payload_table.index(val)
        payload_table.append(val)
        return len(payload_table) - 1

    inst_data = []
    for inst in program.instructions:
        arg_ids = [get_payload_id(arg) for arg in inst.operands]
        # Opcode(1) + ArgCount(1) + Args(4 each, max 4 args for simplicity in fixed size?)
        # Let's just do dynamic size per instruction for better flexibility
        inst_data.append(struct.pack("<B B", inst.opcode.value, len(arg_ids)))
        for aid in arg_ids:
            inst_data.append(struct.pack("<I", aid))

    inst_blob = b"".join(inst_data)
    
    # Payload table serialization
    payload_blobs = []
    for p in payload_table:
        p_json = json.dumps(p).encode('utf-8')
        payload_blobs.append(struct.pack("<I", len(p_json)) + p_json)
    payload_blob = b"".join(payload_blobs)
    
    # Full body
    body = meta_json + struct.pack("<I", len(program.instructions)) + inst_blob + struct.pack("<I", len(payload_table)) + payload_blob
    
    # Checksum over body
    checksum = hashlib.sha256(body).digest()[:4]
    
    return header + body + checksum

def decode_program(data: bytes) -> Program:
    offset = 0
    magic, version, meta_len = struct.unpack_from("<8sH I", data, offset)
    offset += 14
    if magic != MAGIC:
        raise ValueError("Invalid magic header")
    
    meta_json = data[offset:offset+meta_len]
    offset += meta_len
    metadata = json.loads(meta_json.decode('utf-8'))
    
    inst_count = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    
    # We need to skip instructions for a moment to find payload table
    # Or just parse instructions and payloads in order if we know counts
    # Let's read instructions first
    temp_instructions = []
    for _ in range(inst_count):
        opcode_val, arg_count = struct.unpack_from("<B B", data, offset)
        offset += 2
        arg_ids = []
        for _ in range(arg_count):
            arg_ids.append(struct.unpack_from("<I", data, offset)[0])
            offset += 4
        temp_instructions.append((opcode_val, arg_ids))
        
    payload_count = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    
    payload_table = []
    for _ in range(payload_count):
        p_len = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        p_json = data[offset:offset+p_len]
        offset += p_len
        payload_table.append(json.loads(p_json.decode('utf-8')))
        
    # Reconstruct instructions
    instructions = []
    for op_val, arg_ids in temp_instructions:
        args = [payload_table[aid] for aid in arg_ids]
        instructions.append(Instruction(opcode=Opcode(op_val), operands=args))
        
    # Check checksum (last 4 bytes)
    body_end = offset
    checksum = data[offset:offset+4]
    body = data[14:body_end]
    actual_checksum = hashlib.sha256(body).digest()[:4]
    if checksum != actual_checksum:
        raise ValueError(f"Checksum mismatch: expected {checksum.hex()}, got {actual_checksum.hex()}")

    return Program(instructions=instructions, metadata=metadata)
