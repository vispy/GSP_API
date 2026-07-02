# M185 - S043 GSP partial Datoviz snapshot adapter

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Completed locally in GSP_API commit `2c14c95`.

## Result

Added a guarded Datoviz M184 panel-frame snapshot adapter in GSP. The Datoviz v0.4 protocol renderer
now detects the frame snapshot APIs, maps reported panel/plot/grid rectangles, device scale, visible
View2D ranges, guide layout boxes, and rendered contribution identities into a partial
`ResolvedLayoutSnapshot`, and preserves explicit diagnostics for guide query/all-rendered strictness
gaps. Capability metadata now advertises `resolved_layout_produce="partial"` only when those Datoviz
APIs are present, while keeping `layout_strict=False` and native grid clipping independent.

Validation completed:

```sh
uv run pytest tests/ -q
uv run mypy src/ --strict --show-error-codes
GSP_BACKEND=matplotlib uv run python -c "import gsp; print('Matplotlib backend OK')"
GSP_BACKEND=datoviz uv run python -c "import gsp; print('DatoViz backend OK')"
git diff --check
```

Results: 549 passed, 2 skipped; strict mypy clean; both backend import smokes passed.

## Summary

Map available Datoviz panel frame snapshot fields into GSP `ResolvedLayoutSnapshot` while preserving
adapted diagnostics for missing strict guide semantics.

## Deliverables

- Datoviz snapshot binding/facade detection in GSP.
- Mapping from Datoviz panel/plot/grid rects, device scale, view transforms, diagnostics, and
  available guide fields into GSP layout snapshot structures.
- New partial snapshot capability and diagnostics.
- Native grid clipping capability remains independently detectable.
- Focused tests for snapshot id equality on available fields.
- Review-pack diagnostics that distinguish native grid clipping from full guide strictness.

## Acceptance

- GSP does not synthesize strict fields Datoviz cannot report.
- Pixel-unit/device-scale assumptions are explicit.
- Existing adapted guide rows remain adapted until guide query/contribution evidence exists.

## Stop Conditions

- Stop if GSP must invent guide boxes or contribution ids not reported by Datoviz.
- Stop if Datoviz and GSP disagree on logical pixel or device-scale units.
