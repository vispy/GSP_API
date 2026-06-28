# tools/agentctl

`tools/agentctl` is a minimal repo-local Mission Control CLI intended to be called by Codex.

Useful commands:

```bash
tools/agentctl brief
tools/agentctl review-now
tools/agentctl next
tools/agentctl usage
tools/agentctl mission list
tools/agentctl mission show M001
tools/agentctl task list
tools/agentctl runs
tools/agentctl launch-approved
tools/agentctl pro-packet
```

The first version is intentionally simple and uses only Python standard library.
- `compare-review-examples`: runs `examples/review/[0-9]*.py` through Matplotlib and Datoviz review paths. It opens live windows by default; pass `--offscreen` to write artifacts under `artifacts/example_review/`.
