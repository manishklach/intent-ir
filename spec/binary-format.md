# IntentBin binary format

IntentBin is the binary packet encoding for IntentASM programs.

## Header

The packet begins with a fixed-size header:

- `magic`: `IASM`
- `version`: `1`
- `instruction_count`: number of instruction records
- `payload_table_offset`: byte offset from the start of the packet to the payload table
- `checksum`: SHA-256 of the packet body

## Instruction records

Each instruction record encodes:

- opcode byte
- operand count byte
- two reserved bytes
- repeated operand reference pairs

Each operand reference pair contains:

- `key_ref`: 16-bit index into the payload table
- `value_ref`: 16-bit index into the payload table

This keeps the instruction stream compact while allowing repeated keys and values to be interned once.

## Payload table

The payload table stores canonical JSON blobs. It begins with a payload count, followed by repeated:

- payload length
- payload bytes

Both operand keys and operand values are interned in this table. Payload references in IntentASM such as `@scan_request` are serialized as tagged JSON objects so they roundtrip back into `PayloadRef` values when decoded.

## Design intent

The binary format is built for:

- deterministic roundtrip from `.intentasm` to `.intentbin` and back
- compact packet transport between agents
- explicit checksum validation before receiver execution

The format is deliberately simple so it can be audited during research and prototype work.
