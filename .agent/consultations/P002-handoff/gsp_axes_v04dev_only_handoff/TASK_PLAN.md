# Task Plan For Codex Agents

## 0. Replace/supersede the earlier handoff

Likely paths:

- `docs/adr/`
- `docs/missions/`
- local planning notes

Task:

- Mark any earlier “Datoviz may lack axes” wording as superseded.
- Add a note that Datoviz `v0.4-dev` GitHub branch is source of truth for Datoviz implementation.
- Add a note that datoviz.org/v0.3-era Python plotting docs are not authoritative for this mission.

Stop condition:

- Documentation only.

## 1. Capture the ADR

Likely paths:

- `docs/adr/ADR-002-axis-realization-providers.md`
- `docs/architecture/axes.md`

Task:

- Add the ADR from this bundle.
- State semantic GSP axis intent and provider realization.
- Name Matplotlib and Datoviz native providers.
- State generated primitives are implementation artifacts.

Stop condition:

- No protocol code yet.

## 2. Add semantic `Panel` and `View2D`

Likely paths:

- `src/gsp/protocol/panels.py`
- `src/gsp/protocol/views.py`
- `src/gsp/protocol/scene.py`
- `tests/gsp/protocol/`

Task:

- Add `Panel`/`PlotPanel` with stable IDs.
- Add `View2D` with linear x/y ranges, aspect policy, and panel attachment.
- Add visual attachment to panel/view where protocol shape allows.

Stop condition:

- No ticks/labels/title.
- No generated axes.

## 3. VisPy2 view APIs

Likely paths:

- `src/vispy2/`
- `tests/vispy2/`

Task:

- Add internal `View2D` to each `Axes`.
- Add `set_xlim`, `set_ylim`, `get_xlim`, `get_ylim`.
- Attach `scatter`/`imshow` visuals to the view in the full scene accessor.
- Keep `Figure.visuals()` returning only user data visuals.

Stop condition:

- No title/labels/ticks stable API yet.

## 4. Matplotlib `View2D` rendering

Likely paths:

- `src/gsp_matplotlib/`
- `tests/gsp_matplotlib/`
- `src/vispy2/`

Task:

- Configure Matplotlib axes limits from `View2D`.
- Preserve existing point/image rendering.
- Add tests proving limits match exactly.

Stop condition:

- Native Matplotlib default ticks may still appear visually, but do not call this GSP tick conformance.

## 5. Provider/capability schema

Likely paths:

- `src/gsp/capabilities.py`
- `src/gsp/axes/providers.py`
- `src/gsp_matplotlib/capabilities.py`
- `src/gsp_datoviz/capabilities.py`
- `tests/gsp/`

Task:

- Add axis-provider capability declarations.
- Add provider request/selection model.
- Add strict/adapted provider status and diagnostics.

Stop condition:

- Pure schema/selection. No full axis rendering yet.

## 6. GSP tick resolver

Likely paths:

- `src/gsp/axes/ticks.py`
- `tests/gsp/axes/`
- legacy source: `src/vispy2/axes/*`

Task:

- Extract deterministic `auto-linear-nice-v0` from legacy locator/formatter ideas.
- Add explicit tick spec support.
- Add tests for fixed ranges.

Stop condition:

- Pure resolver only.

## 7. Semantic guide protocol objects

Likely paths:

- `src/gsp/protocol/guides.py`
- `src/gsp/protocol/scene.py`
- `tests/gsp/protocol/`

Task:

- Add `AxisGuide`, `TickSpec`, `PanelTextGuide`.
- Add `ResolvedGuideContribution` model.
- Add query policy fields.

Stop condition:

- Do not implement log/date/category/polar/3D axes.

## 8. Matplotlib native axis provider

Likely paths:

- `src/gsp_matplotlib/axes.py`
- `src/gsp_matplotlib/protocol_renderer.py`
- `tests/gsp_matplotlib/`

Task:

- Render semantic guides using native Matplotlib axes artists.
- In strict mode, use GSP-resolved ticks/labels explicitly.
- Add diagnostics if native Matplotlib behavior is used in adapted mode.

Stop condition:

- No broad Matplotlib compatibility layer.

## 9. Datoviz v0.4-dev native axis provider proof

Likely paths:

- `src/gsp_datoviz/axes.py`
- `src/gsp_datoviz/capabilities.py`
- `tests/gsp_datoviz/`

Precondition:

- Local checkout has verified v0.4-dev symbols and Python/raw binding exposure.

Verification commands:

```bash
rg -n "dvz_panel_set_domain|dvz_panel_set_view2d|dvz_panel_axis|dvz_axis_set_label|dvz_axis_set_tick_policy|DvzPanelView2D|DvzAxisTickPolicy|DvzAxisStyle" include src spec examples tests datoviz
```

Task:

- Map GSP panel/view to Datoviz panel/domain/view2d.
- Use `dvz_panel_axis()` for x/y axes if available.
- Configure visibility/label/tick policy/style/grid only where supported.
- If explicit ticks are not supported, emit adapted-provider diagnostics.
- If guide text query is not supported, advertise render-only guide support and guide-query unsupported.

Stop condition:

- Do not call v0.3-style `panel.axes(...)` from obsolete examples.
- Do not invent Datoviz API names.
- Do not block the mission on perfect guide text query.

## 10. Generated primitive fallback provider

Likely paths:

- `src/gsp/axes/resolve.py`
- `src/gsp_reference/`
- `src/gsp_datoviz/axes_fallback.py`
- `tests/gsp/axes/`

Task:

- Convert `ResolvedGuideContribution` to line/text primitives as a backend realization artifact.
- Ensure generated contributions carry `generated_from` semantic metadata.

Stop condition:

- Do not append fallback primitives to `Figure.visuals()`.

## 11. Query scopes and guide query

Likely paths:

- `src/gsp/query/`
- `src/gsp_matplotlib/query.py`
- `src/gsp_datoviz/query.py`
- `tests/gsp/query/`

Task:

- Add `scope="data" | "guides" | "all-rendered"`.
- Add guide result fields: source guide ID, role, axis dimension, tick value, text value.
- Datoviz provider returns `unsupported` when native guide query cannot be decoded.

Stop condition:

- Bounding-box text query is enough for reference path.
- No exact glyph outline hit testing.
