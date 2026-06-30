# M165 - S037 Datoviz View3D evidence spike

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Completed by local-main-codex.

## Summary

Determine whether the active Datoviz v0.4 bindings can privately lower public GSP `View3D`
semantics for retained `(N, 3)` `MeshVisual` rendering.

## Deliverables

- Binding/header evidence for public View3D/camera-equivalent APIs.
- Runtime probe or structured unsupported report.
- Minimal retained 3D triangle fixture plan for DATA, NDC3, and depth evidence.
- Capability recommendation for Datoviz 3D support.

## Acceptance

- Either evidence passes and M166 can proceed, or current unsupported diagnostics remain.
- No public Datoviz camera, controller, draw-state, or material names leak into GSP API.

## Stop Condition

Stop if the only path depends on private ABI details, unavailable symbols, silent z flattening, or
unverified coordinate/depth semantics.

## Result

Completed. Added `tools/probe_datoviz_view3d.py` and
`.agent/S037_DATOVIZ_VIEW3D_EVIDENCE.md`.

The active local Datoviz import exposes promising camera/depth symbols, but the Python-visible
`DvzCameraView` and `DvzCameraDesc` types do not expose the fields/factories needed to safely lower
canonical GSP `Camera3D` and `OrthographicProjection3D`. Datoviz orthographic projection also
exposes height/near/far rather than the full S036 explicit x/y bounds contract. Therefore M166
implementation is blocked and current `mesh3d_coordinate_space_unsupported` diagnostics must remain.

Validation performed:

```bash
tools/probe_datoviz_view3d.py
python -m json.tool .agent/status.json >/dev/null
tools/agentctl next
uv run ruff check tools/probe_datoviz_view3d.py
```

`tools/probe_datoviz_view3d.py` correctly exits nonzero while reporting `status: not-ready`.
