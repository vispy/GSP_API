# ADR-0003 - GSP v0.1 vertical slice

## Status

Proposed

## Context

M001-M005 established the first GSP protocol spine, point/image visual models, Matplotlib protocol renderer, Datoviz v0.4 assessment, and reference panel-query proof.

The project needs a stable mini-contract before expanding into Datoviz implementation, VisPy2 producer APIs, extensions, virtual data sources, and distributed rendering.

## Decision

The GSP v0.1 vertical slice covers:

- stable GSP identifiers;
- capability snapshots;
- resource and command-batch model;
- local in-process transport;
- point visual;
- image visual;
- Matplotlib reference rendering;
- deterministic reference panel query for point-over-image.

The local desktop path must not require JSON/base64. JSON/base64 may exist only for fixtures, debug, replay, or transport-specific paths.

## In scope

- In-process local protocol objects.
- Point/image visual semantic contracts.
- Matplotlib reference/conformance path.
- Deterministic CPU reference query.
- Basic capability model sufficient for the current slice.
- Tests and fixtures that protect current behavior.

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

## Consequences

- Future Datoviz and VisPy2 missions must consume this mini-contract rather than inventing parallel models.
- Matplotlib remains the reference backend for this slice.
- Datoviz v0.4 remains the flagship GPU backend target, but is not required to pass v0.1 conformance until its adapter slice exists.
- Query semantics can be hardened incrementally, but M006 must not broaden them beyond the first deterministic reference proof.

## Open questions

- Exact future fixture serialization format.
- Exact extension/virtual data-source model.
- Exact Datoviz v0.4 runtime capability query binding.
