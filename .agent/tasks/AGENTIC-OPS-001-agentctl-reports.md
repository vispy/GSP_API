# AGENTIC-OPS-001 - Harden agentctl review and next-step reports

## Goal

Improve `tools/agentctl` as the command backend for Codex Mission Control.

## Mission

M010

## Acceptance

- `tools/agentctl brief` returns useful project state.
- `tools/agentctl review-now` identifies review items.
- `tools/agentctl next` recommends next missions.
- `tools/agentctl usage` reports provider status without credentials.

## Stop conditions

Stop if provider inspection risks exposing tokens or credentials.
