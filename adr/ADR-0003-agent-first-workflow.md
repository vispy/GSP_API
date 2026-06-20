# ADR-0003 - Codex-first Mission Control workflow

Status: accepted initial decision

## Decision

Use Codex as the primary natural-language Mission Control interface. Avoid building a separate dashboard initially.

Codex should use `tools/agentctl` under the hood to inspect status, update mission/task files, launch workers, and track runs.

## Rationale

This keeps the workflow agent-centric and avoids building UI before the process is proven.

## Consequences

The repo needs stable command-line reports that Codex can call and summarize.
