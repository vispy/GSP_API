# AGENTIC-OPS-002 - Inventory aisw providers safely

## Goal

Safely inspect available aisw profiles and update provider placeholders where unambiguous.

## Mission

M010

## Acceptance

- `.agent/providers.json` reflects known usable providers.
- Missing Claude profile is kept as an explicit open issue if unresolved.
- No token or credential material is committed.

## Stop conditions

Stop if aisw requires manual login or emits sensitive data.
