# Spécification API pour llm_agent

POST /think
Request:
{
  "user_id": "user-123",
  "input": "Planifie ma journée et réserve un taxi pour 9h",
  "context": ["calendar events", "preferences"],
  "tools": ["calendar", "notifier", "action_exec"]
}

Response:
{
  "id":"tx-abc",
  "plan":[{"step":1,"action":"check_calendar","args":{}}],
  "tool_calls":[{"tool":"calendar","call":{"method":"create","args":{}}}],
  "explanation":"J'explique pourquoi...",
  "need_user_confirmation":true,
  "safety":{"risk":"low","notes":"..."}
}
