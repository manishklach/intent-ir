# Opcodes

INTENT-IR uses a compact opcode set for agent-to-agent instruction packets.

| Opcode | Mnemonic | Purpose |
| --- | --- | --- |
| `0x01` | `AGENT` | Declares the sending agent identity. |
| `0x02` | `TASK` | Declares the task context for the packet. |
| `0x03` | `BUDGET` | Conveys bounded execution budgets such as tokens, memory, or wall time. |
| `0x04` | `PAYLOAD` | Declares named structured payload data. |
| `0x05` | `SEND` | Declares the intended receiving agent. |
| `0x06` | `CALL` | Requests a receiver-side tool or capability invocation. |
| `0x07` | `ASSERT` | Encodes a sender-side expectation or precondition. |
| `0x08` | `COMMIT` | Records a commit/status outcome for the packet flow. |
| `0x09` | `FAIL` | Marks an intentional failure path. |
| `0x0A` | `TRACE` | Declares trace intent or trace label metadata. |
| `0x0B` | `RELEASE` | Releases a named resource or reservation. |
| `0xFF` | `HALT` | Terminates the packet program. |

## Notes

- `CALL` is the most sensitive opcode because it can request receiver-side action.
- `PAYLOAD` plus `CALL payload=@name` provides compact structured argument passing without embedding large opaque strings into every instruction.
- `HALT` is explicit so packets have a clear terminal instruction for verification and replay.
