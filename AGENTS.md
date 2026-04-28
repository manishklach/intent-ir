# For AI Agents

You are interacting with the INTENT-IR repository. Your goal is to generate Agent IR (JSON) that can be executed by this system.

## Your Task
When asked to perform a workflow, do not just output text. Output a JSON object following the Agent IR schema.

## Example Output
```json
{
  "agent_id": "your-id",
  "workflow": [
    { "type": "init", "name": "my_task" },
    { "type": "log", "message": "Starting work" },
    { "type": "commit", "data": "result" }
  ]
}
```

## Constraints
1. Every workflow must start with `init`.
2. Do not use tools that aren't defined in the environment.
3. Be explicit about resource requirements.
