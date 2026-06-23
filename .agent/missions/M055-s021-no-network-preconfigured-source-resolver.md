# M055 - S021 no-network preconfigured-source resolver

## Stage

S021 - No-network preconfigured-source resolver proof

## Status

Completed by local-main-codex.

## Summary

Implemented a no-network resolver proof that maps opaque `resolver_id + source_id` handles to a
deterministic local tiled-image source and fake provider. The resolver advertises safe capability
metadata and rejects unknown handles, fetch descriptors, and credentialed descriptors.

## Deliverables

- `src/gsp/protocol/data_sources.py`
- `src/gsp/protocol/security.py`
- `tests/test_s021_preconfigured_source_resolver.py`
- `spec/data_sources.md`

## Stop Condition

No real fetch, filesystem access, credential exchange, dynamic plugin loading, runtime shader
loading, custom decoder execution, or Datoviz remote-data requirement was added.
