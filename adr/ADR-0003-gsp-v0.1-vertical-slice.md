# ADR-0003 - GSP v0.1 Vertical Slice

## Status

Accepted

## Context

M001-M005 established the first GSP protocol spine, point/image visual models, Matplotlib protocol renderer, Datoviz v0.4 assessment, and reference panel-query proof.

The project needs a stable mini-contract before expanding into Datoviz implementation, VisPy2 producer APIs, extensions, virtual data sources, and distributed rendering.

This ADR defines the contract that M006 hardens. It is deliberately small: a vertical slice that future agents can consume, test, and extend without inventing parallel models.

## Decision

The GSP v0.1 vertical slice is accepted as the current mini-contract for this branch. It covers:

- stable GSP identifiers;
- capability snapshots;
- resource and command-batch model;
- local in-process transport;
- point visual;
- image visual;
- Matplotlib reference rendering;
- deterministic reference panel query for point-over-image;
- conformance fixtures and tests for the above.

The local desktop path must not require JSON/base64. JSON/base64 may exist only for fixtures, debug, replay, or transport-specific paths.

The authoritative implementation surface for this slice is:

- `src/gsp/protocol/`
- `src/gsp_matplotlib/protocol_renderer.py`
- `src/gsp_matplotlib/protocol_query.py`
- `fixtures/conformance/`
- `tests/test_*protocol*` and `tests/test_conformance_baseline.py`

## In scope

- In-process local protocol objects.
- Point/image visual semantic contracts.
- Matplotlib reference/conformance path.
- Deterministic CPU reference query.
- Basic capability model sufficient for the current slice.
- Tests and fixtures that protect current behavior.
- Capability baseline for the v0.1 slice.

## Out of scope

- Extension manifests.
- Virtual/tiled data sources.
- Production remote renderer.
- Datoviz query execution.
- Full Datoviz v0.4 backend.
- Full VisPy2 plotting API.
- Full Matplotlib compatibility.
- Arbitrary custom visual plugins.
- Production transport format.
- Mandatory JSON/base64 for local execution.
- Datoviz implementation changes.
- VisPy2 implementation changes.

## Consequences

- Future Datoviz and VisPy2 missions must consume this mini-contract rather than inventing parallel models.
- Matplotlib remains the reference backend for this slice.
- Datoviz v0.4 remains the flagship GPU backend target, but is not required to pass v0.1 conformance until its adapter slice exists.
- Query semantics can be hardened incrementally, but M006 must not broaden them beyond the first deterministic reference proof.
- Conformance fixtures should prefer Python/in-process objects. If serialized fixtures are added later, they must be secondary debug/replay artifacts and not the local fast path.
- Breaking changes to identifiers, visual field requirements, query statuses, or Matplotlib reference assumptions must update this ADR or supersede it.

## Open questions

- Exact future fixture serialization format.
- Exact extension/virtual data-source model.
- Exact Datoviz v0.4 runtime capability query binding.
