# S035 Closeout - Retained View2D Navigation and Pan/Zoom

Status: completed.

## What Landed

- Accepted semantic `View2D` navigation actions: `pan_by`, `zoom_about`, `set_view`, `reset_view`.
- Deterministic navigation math for normal and reversed finite `View2D` limits.
- Revision/layout snapshot validation through `NavigationResult`.
- Backend-neutral pointer adapter that lowers resolved pointer events to semantic actions.
- Matplotlib programmatic reference and live drag/wheel review example.
- Datoviz v0.4 retained update proof through panel domain/View2D state updates.
- Performance smoke that records update/frame counts and verifies unchanged visual-buffer upload
  count remains zero during Datoviz retained navigation.

## Review Commands

```bash
uv run python examples/protocol_view2d_navigation.py --backend matplotlib
uv run python examples/protocol_view2d_navigation.py --backend matplotlib --scripted-smoke
uv run python tools/s035_navigation_smoke.py --backend both --steps 40 --points 25000
```

## Validation Snapshot

- `uv run ruff check src/gsp/protocol/navigation.py src/gsp/protocol/__init__.py tests/test_navigation_protocol.py tests/test_navigation_smoke.py`
- `uv run mypy src/gsp/protocol/ src/gsp_matplotlib/ src/gsp_datoviz/ --strict --show-error-codes`
- `uv run pytest tests/ -q`
- `GSP_TEST=True uv run python examples/protocol_view2d_navigation.py --backend matplotlib --scripted-smoke`
- `uv run python tools/s035_navigation_smoke.py --backend both --steps 40 --points 25000`

Latest full-suite result during closeout: `462 passed, 3 skipped`.

## Support Boundary

| Area | Status |
|---|---:|
| Matplotlib programmatic S035 actions | supported |
| Matplotlib native drag/wheel review | supported |
| Datoviz retained `View2D` update target | supported |
| Datoviz visual-buffer stability during navigation | supported by fake-facade smoke |
| Datoviz v0.4 native pointer callbacks | deferred |
| Public cross-backend raw event system | deferred |
| Public `View3D`/camera/projection navigation | deferred |

## Next Stage Recommendation

Open S036 as a scoping/consultation stage for minimal `View3D`, camera, projection, and 3D
navigation semantics. Do not implement public 3D API or Datoviz camera bindings before a ChatGPT Pro
consultation packet is created and answered, because this is an architecture/public API decision.

Recommended first S036 mission:

1. Create a self-contained ChatGPT Pro packet for `View3D`/camera/projection/navigation semantics.
2. Convert the accepted response into an ADR and spec baseline.
3. Only then implement protocol dataclasses, Matplotlib reference behavior, and Datoviz capability
   gates.
