# S035 Next Stage Scoping - Retained View2D Navigation and Pan/Zoom

## Decision

Open S035 as the next implementation stage after the reviewed static 2D API. The stage adds useful
2D pan/zoom without defining a broad public event system.

## Public Shape

- Public input is semantic navigation actions: `pan_by`, `zoom_about`, `set_view`, `reset_view`.
- Public output is an explicit updated `View2D` plus revision/snapshot identifiers and diagnostics.
- Native mouse, wheel, keyboard, and backend controller events are adapters into these actions, not
  public protocol semantics.

## Performance Invariant

For retained GPU backends, navigation must update small panel/view/projection state, such as
data-to-clip matrices or equivalent uniform buffers. It must not re-upload unchanged point, image,
mesh, path, segment, marker, or text geometry buffers in the strict fast path.

CPU remapping remains allowed only as an explicit adapted fallback and must not be advertised as the
high-performance interactive path.

## Mission Order

1. M147 - ADR/spec baseline.
2. M148 - protocol dataclasses and validation.
3. M149 - deterministic numeric fixtures.
4. M150 - Matplotlib programmatic reference.
5. M151 - Datoviz retained View2D proof.
6. M152 - live review and performance smoke.
7. M153 - closeout and next-stage recommendation.
