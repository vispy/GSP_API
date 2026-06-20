# AGENTCTL-001 - Verify agentctl

Goal: verify `tools/agentctl` runs and returns useful Mission Control tables.

Allowed files:

- tools/agentctl
- .agent/status.json
- .agent/providers.json

Acceptance:

```bash
tools/agentctl brief
tools/agentctl review-now
tools/agentctl next
tools/agentctl mission list
```

all run without errors.
