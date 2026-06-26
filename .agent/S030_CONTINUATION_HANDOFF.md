# S030 Continuation Handoff

## Current State

Stage S030 is open. M120 is complete and committed. The GSP worktree is clean on
`agentic-gsp-vispy2`, ahead of `origin/agentic-gsp-vispy2` by one commit:

- `cf800e0 Harden Datoviz offscreen capture handling`

Recent prior commits:

- `99baa58 Complete S030 Datoviz guide-axis proof`
- `7d1fdc3 Close S029 review pack`

Mission Control currently lists:

| Mission | State | Recommendation |
| --- | --- | --- |
| M121 | draft | Revise before execution as an axis-only adapted Datoviz guide review path. |
| M122 | draft | Close S030 after M121 evidence, promoting only what is proven. |

## What M120 Proved

Datoviz v0.4 native panel-axis behavior is now proven with captured artifacts when the local
MoltenVK runtime environment is configured:

- backend tick policy
- grid rendering
- axis label rendering
- reversed `View2D` domains
- explicit tick values and labels via `dvz_axis_set_ticks`

Evidence:

- `.agent/S030_DATOVIZ_GUIDE_AXIS_PROOF.md`
- `artifacts/visual_qa/s030/datoviz-guide-axis-proof/report.json`
- `artifacts/visual_qa/s030/datoviz-guide-axis-proof/guide_view2d_auto_grid.png`
- `artifacts/visual_qa/s030/datoviz-guide-axis-proof/guide_view2d_reversed_explicit.png`

## What Was Fixed

GSP now handles Datoviz runtime failures more cleanly:

- `dvz_app()` returning a ctypes NULL handle becomes `DatovizV04Unavailable`.
- `dvz_view_offscreen()` returning a ctypes NULL handle becomes `DatovizV04Unavailable`.
- interactive `dvz_view()` NULL handles are guarded the same way.
- Datoviz facade/dylib load `RuntimeError` is wrapped as `DatovizV04Unavailable`.
- axis labels are passed as UTF-8 bytes to `dvz_axis_set_label`.

This prevents missing or partial Vulkan/MoltenVK setup from cascading into Datoviz C assertions.

## Remaining Blockers

Do not claim strict GSP guide parity yet. Remaining blockers:

- Datoviz panel title API is not exposed/proven: no `dvz_panel_set_title` or `dvz_panel_title`.
- Datoviz guide/all-rendered query support is not exposed/proven.
- GSP production Datoviz renderer still rejects explicit ticks in `configure_view2d_axes(..., backend_auto_ticks=False)`.
- The current Datoviz DATA visual path still CPU-adapts `View2D` positions while native axes use Datoviz panel domains. Treat that as adapted/review behavior unless reconciled.

## Recommended Next Mission

Revise and execute M121 with bounded scope:

1. Wire an axis-only Datoviz guide review path for the two guide rows.
2. Support native Datoviz axes for:
   - backend-resolved ticks,
   - grid,
   - labels,
   - reversed domains,
   - explicit tick values/labels through `dvz_axis_set_ticks`.
3. Emit structured unsupported diagnostics for:
   - `PanelTextGuide` title,
   - guide/all-rendered query,
   - any unsupported strict GSP tick contract.
4. Keep classification adapted/review unless title and guide query are explicitly excluded from the row contract.
5. Stop if implementation would approximate titles or query behavior silently.

## Validation Already Run

After `cf800e0`:

- `PYTHONPATH=. uv run pytest tests/test_datoviz_v04_protocol_renderer.py -q`: 67 passed, 6 skipped
- `PYTHONPATH=. uv run pytest tests/test_visual_qa_harness.py -q`: 24 passed
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`: success
- `PYTHONPATH=. uv run python -m compileall -q tools/probe_datoviz_guide_axis.py`: success
- `git diff --check`: clean

Runtime proof command that succeeded:

```bash
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz
export GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1
export VK_ICD_FILENAMES="$DATOVIZ_REPO/libs/vulkan/macos_arm64/MoltenVK_icd.json"
export DYLD_LIBRARY_PATH="$DATOVIZ_REPO/libs/vulkan/macos_arm64${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
PATH="$DATOVIZ_REPO/.venv/bin:$PATH" PYTHONPATH="$DATOVIZ_REPO:." \
  uv run python tools/probe_datoviz_guide_axis.py \
    --capture \
    --out artifacts/visual_qa/s030/datoviz-guide-axis-proof
```

## External Checkout State

Sibling Datoviz checkout `/Users/cyrille/GIT/Viz/datoviz` has local changes unrelated to this GSP
handoff. Do not revert or edit them unless explicitly asked.

Observed status:

```text
## v0.4-dev...origin/v0.4-dev
 M NOTES
 m data
 M include/datoviz/input/pointer.h
```

