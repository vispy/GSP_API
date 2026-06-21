# M010 - Agentic control-plane provider hardening

## Goal

Improve the agentic workflow enough to support longer autonomous sessions with less manual work.

This mission should fix provider inventory, capture missing Claude aisw profile details as an open question, improve run/review status reporting, and make `tools/agentctl` more useful to Codex Mission Control.

## State

Completed.

## Required reading

- AGENTS.md
- .agent/project.json
- .agent/providers.json
- .agent/status.json
- tools/agentctl
- STATUS.md

## Expected tasks

- Inspect current aisw availability with safe commands:
  - `aisw list --json`
  - `aisw status --json`
  if available.
- Update `.agent/providers.json` with real provider names only when clear.
- Keep missing Claude profile as an explicit open issue if not configured.
- Improve `tools/agentctl brief`, `review-now`, `next`, `runs`, and `usage` output if needed.
- Add a simple run-log convention under `.agent/runs/`.
- Ensure Mission Control can answer:
  - what needs review;
  - what mission is next;
  - what is blocked;
  - what providers are available.

## Allowed paths

- AGENTS.md
- tools/agentctl
- .agent/
- STATUS.md
- docs/agentic_workflow.md if useful

## Forbidden paths

- src/gsp/
- src/gsp_matplotlib/
- src/gsp_datoviz/
- src/vispy2/
- ../datoviz/
- Any credential/token files

## Acceptance criteria

- `tools/agentctl brief` works.
- `tools/agentctl review-now` works.
- `tools/agentctl next` works.
- Provider status is clearer than before.
- No credentials or tokens are printed or committed.
- STATUS.md reflects the Claude profile issue or resolution.

## Stop conditions

Stop if:

- aisw commands reveal sensitive credential paths or token material;
- provider setup requires manual human login;
- changing provider logic risks breaking current Codex workflow.

## Notes

This mission can run in parallel with protocol/backend work because it should not touch implementation source.
