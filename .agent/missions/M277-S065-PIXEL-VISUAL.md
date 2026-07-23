# M277 - S065 PixelVisual end-to-end

## Status

Completed and independently accepted. Target repositories: `gsp`, `vispy2`; Datoviz was
read-only evidence.

## Goal

Implement the PixelVisual contract from protocol through both backends and VisPy2.

## Required scope

- Section 3 of `.agent/S065_TECHNICAL_BASELINE.md`.
- Protocol dataclass, validation, exports, Scene union, capability registry, conformance fixtures.
- Matplotlib deterministic 2D and adapted 3D lowering.
- Datoviz public `dvz_pixel` lowering and exact logical-size capability evidence.
- VisPy2 2D/3D/module-level producers.
- Positive, malformed-array, nonfinite, color, size, view mismatch, capability, and unsupported tests.
- Installed-wheel 2D/3D example and visual artifact.

## Locks

- `gsp`: protocol visuals/exports/scene/capabilities/render dispatch/tests/spec
- `vispy2`: producer exports/tests/example/docs

## Acceptance

Both backends render the representative cases without silent field loss. Datoviz strict and
Matplotlib strict/adapted claims are evidence-backed. Full tests, typing, lint, wheels, examples,
and diff checks pass.

## Stop conditions

Stop if exact pixel semantics require device pixels instead of GSP logical pixels, raw item-state
flags, or backend handles.
