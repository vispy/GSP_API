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
- `workspace`
- `repositories` (repository key, source, writable policy, baseline HEAD, worktree, branch, locks)
- `path_locks`
- `pid` (`null` until a provider starts)
- `command` (`null` for manual preparation)

Allowed statuses:

- `prepared`
- `manual_required`
- `running`
- `completed`
- `failed`
- `blocked`

Do not store credentials, credential paths, tokens, raw environment dumps, or private auth files in
run logs.

For multi-repository runs, all writable linked worktrees live below the recorded coordination
workspace. Read-only evidence repositories record `null` for both `worktree` and `branch`.
`prepared`, `manual_required`, and `running` runs hold their recorded path locks; terminal runs do
not.

Mission Control reviews and integrates repository commits explicitly. The launcher does not merge,
mark missions complete, remove successful worktrees, push, or create pull requests.
