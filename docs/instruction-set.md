# Instruction Set Architecture (ISA)

## Agent Lifecycle
- `DECLARE_AGENT <id>`: Initializes the execution context with the agent's identity.
- `DECLARE_TASK <name>`: Scopes the execution to a specific task.
- `HALT`: Cleanly terminates the execution.
- `FAIL <reason>`: Terminates with an error status.

## Resource & Budget
- `ALLOC_BUDGET <amount> <unit>`: Sets a resource limit (e.g., 100 tokens, 50MB).
- `REQUEST_RESOURCE <uri>`: Requests read/write access to a specific URI.
- `RELEASE <uri>`: Relinquishes access to a resource.

## Interaction
- `CALL_TOOL <name> <args_list>`: Invokes an external capability. Arguments must be a JSON-serializable list.
- `SEND <agent_id> <message>`: Async message passing to another agent.
- `WAIT <condition>`: Blocks execution until the condition (e.g., a message receipt) is true.

## Observability
- `LOG <message>`: Appends a message to the execution log.
- `ASSERT <condition>`: Runtime check. If false, the interpreter should trigger a `FAIL`.
- `COMMIT <data>`: Records the final output of the task.
- `TRACE <meta>`: Manual event injection into the trace stream.
