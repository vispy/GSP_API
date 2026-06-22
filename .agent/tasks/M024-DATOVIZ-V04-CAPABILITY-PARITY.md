# M024-DATOVIZ-V04-CAPABILITY-PARITY - Datoviz v0.4 capability parity

## Mission

M024

## Goal

Translate Datoviz v0.4 capability snapshots into GSP `CapabilitySnapshot` conservatively.

## Acceptance

- `dvz_capability_snapshot()` is used when available from the v0.4 facade.
- Fake/synthetic capability snapshot tests verify resource, texture, readback, and metadata mapping.
- Ambiguous Datoviz fields stay in metadata.
- Query support remains unadvertised until query decode parity.
- Real Datoviz capability smoke skips cleanly when the installed binding lacks the v0.4 symbol.

## Stop conditions

Stop before Datoviz query decode/runtime query support, Datoviz repository edits, sampled-field
parity, capture parity, or tiled-source support.
