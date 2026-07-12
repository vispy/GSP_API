# Project status

GSP and VisPy2 are experimental `0.1.0` research prototypes. They require Python 3.13 or newer, are
installed from source, and do not yet offer stable API compatibility.

## Available today

- Validated protocol records for core 2D and bounded 3D scenes.
- Matplotlib reference rendering and query paths for documented scopes.
- A capability-gated Datoviz v0.4 adapter with substantial 2D and 3D coverage.
- VisPy2 producer helpers for many accepted visual, guide, transform, color, and mesh records.
- Conformance fixtures, structured diagnostics, and visual review tooling.

## Important gaps

- The complete application-facing session that executes arbitrary command batches is not shipped.
- Datoviz support is not global; text, guides, queries, and textures have narrower or blocked scopes.
- A production current-protocol remote transport is not available.
- Protocol acceptance does not guarantee producer or renderer support.
- Several large-data and extension paths remain bounded research proofs.

Internal delivery history is not a product maturity signal. Use the [feature matrix](support/feature-matrix.md)
and runtime capabilities to assess a concrete use case.
