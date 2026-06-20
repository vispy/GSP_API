# PROVIDERS-001 - Inventory aisw provider contexts

Goal: inspect available `aisw` contexts and update `.agent/providers.json` with usable provider entries.

Rules:

- Do not expose tokens or credential file contents.
- It is OK to run `aisw list --json` and `aisw status --json` if available.
- If context names are ambiguous, leave placeholders disabled and add an open question to `.agent/status.json`.

Acceptance:

- `.agent/providers.json` contains either enabled real providers or clear disabled placeholders.
- `.agent/status.json` records whether provider configuration is complete or blocked.
