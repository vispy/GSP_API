# M013 - Matplotlib AxisGuide and PanelTextGuide rendering

## Goal

Render semantic `AxisGuide` and `PanelTextGuide` objects through Matplotlib native axes while keeping
GSP-resolved ticks as the strict conformance source.

## State

Completed.

## Required reading

- `adr/ADR-0005-axis-realization-providers-v04dev.md`
- `.agent/consultations/P003-response.md`
- `.agent/missions/M012-strict-tick-resolver-guide-foundation.md`
- `src/gsp/protocol/guides.py`
- `src/gsp/protocol/ticks.py`
- `src/gsp/protocol/panels.py`
- `src/gsp_matplotlib/protocol_renderer.py`
- `src/vispy2/protocol.py`
- `tests/test_tick_resolver.py`

## Expected tasks

- Add Matplotlib rendering support for `AxisGuide` ticks, labels, visibility, and grid intent.
- Add Matplotlib rendering support for `PanelTextGuide` title intent.
- Use `resolve_ticks()` for strict tick values and labels.
- Preserve existing point/image rendering.
- Preserve `Figure.visuals()` as user data visuals only.
- Add tests for explicit ticks, auto ticks, labels, title, grid visibility, and point/image coexistence.

## Allowed paths

- `src/gsp_matplotlib/**`
- `src/vispy2/**`
- `src/gsp/protocol/**`, only for minor integration/export helpers
- `tests/**`
- `spec/**`, only for brief notes
- `.agent/**`
- `STATUS.md`

## Forbidden paths

- External Datoviz repositories.
- Datoviz v0.3 plotting APIs.
- Matplotlib native locator output as conformance truth.
- Appending generated axes/guides/ticks/title into `Figure.visuals()`.
- Query scope implementation; that belongs to M014/M021.

## Acceptance criteria

- Matplotlib x/y ticks and tick labels come from GSP `resolve_ticks()`.
- Explicit ticks and labels render exactly.
- Axis labels and panel title render from semantic guide objects.
- Grid visibility follows `AxisGuide.grid_visible`.
- Existing point/image rendering still works with guides present.
- Tests pass with `PYTHONPATH=. uv run pytest`.

## Result

Completed by local-main-codex. Added `src/gsp_matplotlib/guides.py`, wired VisPy2
Matplotlib rendering to realize semantic axis guides, and added
`tests/test_matplotlib_guides.py`.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 88 passed, 1 skipped.

## Stop conditions

Stop if guide rendering requires changing `AxisGuide` semantics at ADR scope, if tests depend on
pixel-perfect font/layout comparisons, or if implementation would make generated guide primitives
part of the user visual stream.
