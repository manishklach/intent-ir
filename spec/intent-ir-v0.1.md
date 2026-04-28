# INTENT-IR Specification v0.1.0

## 1. Introduction
INTENT-IR is a deterministic intermediate representation designed for AI agent execution. It provides a structured way to represent agent goals, tool calls, and resource management.

## 2. Instruction Set
| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 0x00 | HALT | Terminate execution |
| 0x01 | DECLARE_AGENT | Set the identity of the executing agent |
| 0x02 | DECLARE_TASK | Set the current task context |
| 0x03 | ALLOC_BUDGET | Allocate tokens/memory for execution |
| 0x04 | REQUEST_RESOURCE| Request access to a file or API |
| 0x05 | SEND | Send message to another agent |
| 0x06 | CALL_TOOL | Invoke an external tool |
| 0x07 | WAIT | Pause until a condition is met |
| 0x08 | ASSERT | Verify a state condition |
| 0x09 | COMMIT | Finalize and record task output |
| 0x0A | FAIL | Terminate with error |
| 0x0B | TRACE | (Reserved) Manual trace injection |
| 0x0C | RELEASE | Release a held resource |
| 0x0D | LOAD_CONST | Load a constant into virtual register |
| 0x0E | LOG | Emit an observability log |

## 3. Binary Format
The binary format consists of a header, an instruction stream, and a payload table.

### Header
- Magic: `INTENTIR` (8 bytes)
- Version: `0x0001` (2 bytes)
- Metadata Length: (4 bytes)
- Metadata: JSON-encoded string

### Instruction Stream
Each instruction is:
- Opcode (1 byte)
- Argument Count (1 byte)
- Arguments: Array of 4-byte indexes into the payload table

### Payload Table
A sequence of:
- Length (4 bytes)
- Data (JSON-encoded)
