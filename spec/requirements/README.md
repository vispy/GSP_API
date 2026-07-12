# GSP 0.2 requirement traceability

This directory prevents semantic loss during the pre-1.0 specification and API consolidation.

## Stable identifiers

Normative requirements use `GSP-<DOMAIN>-NNN`, where `<DOMAIN>` is one of:

| Domain | Scope |
|---|---|
| `CORE` | conformance language, identifiers, ownership, and common validation |
| `LIFE` | initialization, sessions, commands, batches, frames, and shutdown |
| `SCENE` | panels, views, visuals, guides, attachments, and state relationships |
| `DATA` | buffers, textures, locality, virtual sources, and materialization |
| `VIS` | cross-cutting and family-specific visual semantics |
| `VIEW` | coordinate spaces, transforms, layout, navigation, and cameras |
| `CAP` | capability negotiation, adaptation, limits, and diagnostics |
| `QUERY` | panel queries, readback, payloads, ordering, and snapshots |
| `XPORT` | in-process, debug JSON, binary, and network transport contracts |
| `EXT` | extensions, manifests, security policy, and custom data sources |
| `PROD` | producer conformance requirements |

Identifiers are never reused. Removing or replacing a requirement records a disposition instead of
deleting its history.

## Files

- `source_inventory.json` classifies every specification, ADR, and accepted decision source.
- `source_dispositions.json` records the GSP 0.2 destination of every detailed specification.
- `requirements.json` is the normative requirement registry populated during M237.
- `schema.json` defines the machine-checkable registry format.

Run `uv run python tools/spec_traceability.py --check` after changing specification authority or
the registries.
