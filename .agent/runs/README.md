# Agent Run Logs

`tools/agentctl launch` and `tools/agentctl launch-approved` write one directory per prepared or
launched worker run:

```text
.agent/runs/<RUN_ID>/
  prompt.md
  run.json
  launcher.log
  events.jsonl
  stderr.log
```

Required `run.json` fields:

- `id`
- `mission`
- `provider`
- `status`
- `created_at`
- `prompt_file`

Allowed statuses:

- `prepared`
- `manual_required`
- `running`
- `completed`
- `failed`
- `blocked`

Do not store credentials, credential paths, tokens, raw environment dumps, or private auth files in
run logs.
