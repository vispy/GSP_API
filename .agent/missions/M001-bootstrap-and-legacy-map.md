# M001 - Bootstrap agentic control plane and legacy map

## Goal

Complete the first usable agent-centric project-control layer in the current branch, then inspect the existing GSP_API repository and write `LEGACY_MAP.md` so future agents know what to reuse, refactor, mine, or ignore.

## Autonomy

L2 for repository inspection and documentation.

Do this mission in the current interactive Codex session unless working provider contexts are already configured.

## Required reading

- AGENTS.md
- PROJECT_CHARTER.md
- ARCHITECTURE.md
- SPEC_INDEX.md
- STATUS.md
- .agent/project.json
- .agent/status.json

## Tasks

- AGENTCTL-001: verify `tools/agentctl` works and improve only if needed.
- LEGACY-MAP-001: inspect existing repo and replace `LEGACY_MAP.md`.
- PROVIDERS-001: inspect `aisw` availability and provider contexts without exposing secrets.
- MISSION-PLAN-001: refine M002/M003/M004 mission files if obvious.

## Allowed paths

- LEGACY_MAP.md
- .agent/**
- tools/agentctl
- STATUS.md
- AGENTS.md if clarification is needed

## Forbidden paths

Do not change implementation source yet:

- src/**
- examples/**
- tests/**

Do not modify external repos.

## Acceptance criteria

1. `tools/agentctl brief` runs successfully.
2. `LEGACY_MAP.md` is no longer a placeholder and covers major repo directories.
3. `.agent/providers.json` records any usable `aisw` contexts found, or records the exact missing information needed from the user.
4. `.agent/status.json` marks M001 completed or blocked with a clear reason.
5. Commit changes with message: `M001: create legacy map and provider inventory`.

## Stop conditions

Stop and ask the user if:

- `aisw` is not installed or not configured;
- provider context names are ambiguous;
- repo structure is very different from expected;
- you would need to edit implementation source to proceed;
- you need a high-reasoning architectural decision.

## Final report

End with:

- files changed;
- command checks run;
- provider contexts found or missing;
- recommended next mission;
- whether ChatGPT Pro consultation is needed.
