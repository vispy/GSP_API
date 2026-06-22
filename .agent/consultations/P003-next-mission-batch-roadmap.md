# P003 - Next mission batch roadmap for GSP / VisPy2

Status: pending ChatGPT Pro response.

## Why This Is Needed

The GSP / VisPy2 repository has completed its first foundation sequence through `S011`, and a
follow-up semantic axes/provider proof has been committed. Mission Control currently reports no
queued next missions. We need a larger batch of upcoming stages/missions/tasks so local Codex and
worker agents can keep moving without repeatedly pausing for architectural triage.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

You are a roadmap and architecture reviewer for the GSP / VisPy2 project. Your task is to generate
a coherent next batch of stages, missions, and implementation tasks for local Codex agents.

GSP is a backend-independent Graphics Server Protocol for semantic scientific visualization.
VisPy2 is the high-level Python producer API that targets GSP. Matplotlib is the
reference/conformance/publication backend. Datoviz v0.4-dev is the flagship GPU backend. The project
uses mission-control files under `.agent/` and durable architecture records in `adr/` and `spec/`.

## Current Project Principles

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and should use a unified panel-query model.
7. Extensions must be manifest-, version-, and capability-driven.
8. Huge datasets should be represented as virtual data sources, not ordinary buffers.
9. Datoviz v0.4-dev is the flagship GPU backend.
10. Matplotlib is the reference/conformance/publication backend.
11. VisPy2 is the high-level Python producer of GSP scenes.
12. Existing code is implementation material, not automatically protocol authority.
13. ChatGPT Pro consultation prompts must be self-contained unified text prompts.

## Completed Foundation

Mission Control currently reports all planned stages through `S011` completed:

| Stage | Title | State |
|---|---|---|
| S001 | Agentic control plane and legacy map | completed |
| S002 | Protocol spine | completed |
| S003 | Matplotlib reference slice | completed |
| S004 | Datoviz v0.4 adapter assessment | completed |
| S005 | Query proof | completed |
| S006 | Protocol hardening and conformance baseline | completed |
| S007 | Datoviz v0.4 point/image adapter slice | completed |
| S008 | VisPy2 producer MVP | completed |
| S009 | Query hardening and Datoviz handoff | completed |
| S010 | Agentic control plane provider hardening | completed |
| S011 | Extensions and virtual data source architecture proof | completed |

There is no current `tools/agentctl next` queue.

## Recently Committed Follow-Up Work

Two recent commits exist after the S011 foundation:

```text
8b71613 Require self-contained ChatGPT Pro prompts
85472df Add semantic axis provider proof
```

The axis-provider proof added:

- `adr/ADR-0005-axis-realization-providers-v04dev.md`
- `src/gsp/protocol/panels.py`
- `src/gsp/protocol/guides.py`
- axis provider capability schema in `src/gsp/protocol/capabilities.py`
- `src/gsp_matplotlib/capabilities.py`
- `src/gsp_datoviz/capabilities.py`
- Datoviz provider-gated axis proof in `src/gsp_datoviz/protocol_renderer.py`
- VisPy2 `View2D` APIs in `src/vispy2/protocol.py`
- tests in `tests/test_axis_provider_capabilities.py`, `tests/test_vispy2_protocol_mvp.py`,
  and `tests/test_datoviz_v04_protocol_renderer.py`

Validation after that work:

```text
PYTHONPATH=. uv run pytest
76 passed, 1 skipped
```

The skipped test is expected because the installed Python `datoviz` package does not expose the
v0.4-dev facade/raw symbols yet.

## Current Concrete Architecture State

### Protocol Spine

Current protocol package includes:

- stable IDs and object refs;
- `CapabilitySnapshot`;
- adaptation decisions;
- contiguous buffer/resource descriptors;
- command batches and in-process transport;
- `PointVisual`;
- `ImageVisual`;
- query request/result/status models;
- extension/data-source/tiled-image proof models;
- new semantic `Panel`;
- new semantic `View2D`;
- new semantic `VisualAttachment`;
- new semantic `AxisGuide`;
- new semantic `TickSpec`;
- new semantic `PanelTextGuide`;
- axis provider capability/request/selection schema.

Current `PointVisual` / `ImageVisual` have `coordinate_space`, including `NDC` and `DATA`.

### VisPy2 MVP

VisPy2 currently supports:

```python
import vispy2 as vp

fig, ax = vp.subplots()
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.imshow(image)
ax.scatter(x, y, color=rgba, size=36)
fig.render_matplotlib()
fig.savefig("out.png")
```

Important invariant:

- `Figure.visuals()` returns user data visuals only.
- `Figure.panels()`, `Figure.views()`, and `Figure.attachments()` expose semantic scene structure.
- Generated axes/guides must not be appended to `Figure.visuals()`.

Current VisPy2 scope:

- `Axes.scatter()` emits `PointVisual`.
- `Axes.imshow()` emits `ImageVisual`.
- `Axes.set_xlim()` / `set_ylim()` update `View2D`.
- Matplotlib rendering honors `View2D` limits.
- Stable public guide/tick/title APIs are not fully implemented yet.

### Axis Provider Decision

Accepted direction:

GSP owns semantic `Panel` / `View2D` / `AxisGuide` / `TickSpec` / `PanelTextGuide` intent and
identity. Backend adapters choose capability-declared axis realization providers.

Initial provider IDs:

```text
gsp.reference.generated_primitives.v0
matplotlib.native.axes.v0
datoviz.v04.panel_axis.wip
```

Provider status may be:

```text
strict | adapted | experimental | unsupported
```

Strict provider examples:

- GSP computes ticks with `auto-linear-nice-v0`, provider renders exactly those values and labels.
- User supplies explicit ticks and labels, provider renders exactly those values and labels.

Adapted provider examples:

- Datoviz native axis uses backend auto ticks because explicit tick values are not supported by the
  exposed binding.
- Matplotlib native locator is left active in non-conformance mode.

Guide contributions must be queryable only when the provider supports guide queries. If a provider
can render guides but not query guide text/ticks, guide-scoped queries must return `unsupported`, not
`miss`.

### Matplotlib State

Matplotlib currently renders formal `PointVisual` and `ImageVisual` and now honors `View2D` limits
in the VisPy2 render path.

Matplotlib capability declaration advertises:

```text
matplotlib.native.axes.v0
```

as a strict native axis provider for the current slice.

Missing Matplotlib guide work:

- deterministic `auto-linear-nice-v0` tick resolver;
- strict explicit tick rendering;
- `AxisGuide` rendering with labels/grid;
- `PanelTextGuide` title rendering;
- optional guide query scope;
- conformance fixtures for rendered guide semantics.

### Datoviz State

Datoviz implementation authority for axes:

- `github.com/datoviz/datoviz` branch `v0.4-dev`;
- local checkout headers under `include/datoviz/`.

Explicitly not authoritative:

- `datoviz.org` v0.3-era pages;
- v0.3 Python plotting examples such as old `panel.axes(...)` usage.

Local Datoviz checkout was verified on branch `v0.4-dev`. Headers expose:

```c
dvz_panel_set_domain(DvzPanel* panel, DvzDim dim, double min, double max)
dvz_panel_view2d(void)
dvz_panel_set_view2d(DvzPanel* panel, const DvzPanelView2D* view)
dvz_panel_view2d_extent(DvzPanel* panel, float out[4])
dvz_panel_visible_domain(DvzPanel* panel, DvzDim dim, double* out_min, double* out_max)
dvz_panel_data_to_visual_positions(DvzPanel* panel, const float* data_positions, float* visual_positions, uint32_t count)
dvz_panel_axis(DvzPanel* panel, DvzDim dim)
dvz_axis_tick_policy(void)
dvz_axis_style(void)
dvz_axis_set_visible(DvzAxis* axis, bool visible)
dvz_axis_set_grid(DvzAxis* axis, bool visible)
dvz_axis_set_label(DvzAxis* axis, const char* label)
dvz_axis_set_tick_policy(DvzAxis* axis, const DvzAxisTickPolicy* policy)
dvz_axis_set_style(DvzAxis* axis, const DvzAxisStyle* style)
dvz_axis_set_plot_margins(DvzAxis* axis, float left, float right, float bottom, float top)
dvz_axis_set_units(DvzAxis* axis, DvzUnits* units)
dvz_axis_set_datetime(DvzAxis* axis, DvzDateTimeFormat* format)
```

Relevant local header constants:

```c
DVZ_DIM_X = 0x0000
DVZ_DIM_Y = 0x0001
```

Installed Python `datoviz` currently does not expose the v0.4-dev facade or `datoviz.raw`:

```text
panel_set_domain False
panel_set_view2d False
panel_axis False
axis_set_label False
axis_set_tick_policy False
DvzPanelView2D False
DvzAxisTickPolicy False
DvzAxisStyle False
raw import failed: No module named 'datoviz.raw'
```

Current GSP Datoviz adapter:

- supports point and uint8 RGB/RGBA image through a bounded v0.4 facade shape;
- still supports only NDC point/image positions in the first adapter slice;
- advertises `datoviz.v04.panel_axis.wip` only when a supplied/imported Python module exposes the
  verified v0.4-dev symbols;
- includes a fake-facade-tested `configure_view2d_axes()` proof that calls only verified symbol
  names;
- rejects explicit strict GSP ticks for Datoviz native axes in this slice.

### Extension/Data Source State

M011 added a minimal static extension and virtual data-source proof:

- `ExtensionManifest` is static metadata, not a dynamic plugin loader.
- Virtual data sources are core protocol objects.
- First built-in reference extension: `gsp.tiled-image@0.1`.
- First executable source model: `TiledImageSource`, backed only by synthetic/in-memory local data.
- Matplotlib reference materializes deterministic viewport mosaics and renders through existing
  image path.
- Tiled-image query returns normal `QueryResult` plus `TiledImageQueryPayload`.

Out of scope remains:

- real HTTP/S3/GCS/Zarr/OME-Zarr/COG/map-tile clients;
- credential exchange;
- async prefetch/cache/retry/progressive refinement;
- production server-side fetch;
- dynamic plugin discovery/loading.

### Query State

Current query model:

Use a unified panel query:

```text
What rendered scene contribution is under this panel coordinate?
```

Current query statuses:

```text
hit
miss
outside-panel
unsupported
stale
dropped
failed
```

Current query modes:

```text
panel-query
point-item
image-texel
```

Need future scopes:

```text
data
guides
all-rendered
```

Datoviz query note:

Earlier work found that local Datoviz `v0.4-dev` exposes `DvzQueryResult` fields in the source tree,
which may unblock a later query decoder/proof mission, but the installed Python package in the GSP
environment does not currently expose the v0.4 facade/raw bindings.

## Existing Task Backlog Hints

Mission Control task list contains these useful task families:

```text
DATOVIZ-V04-CAPABILITY-PARITY
DATOVIZ-V04-IMAGE-FIELD-CONTRACT
DATOVIZ-V04-PARITY-NEXT-PACK
DATOVIZ-V04-PYTHON-FACADE-CONTRACT
DATOVIZ-V04-QUERY-BINDING
DATOVIZ-V04-QUERY-PARITY
DATOVIZ-V04-QUERY-BINDING
QUERY-HANDOFF-001-datoviz-query-binding
QUERY-HARDEN-001-status-capability-semantics
EXT-DATA-001-consultation-packet
VISPY2-MVP-001-scatter-imshow-api
VISPY2-MVP-002-examples-tests
GSP-CAPS-001
```

But there is no queued post-S011 mission sequence.

## Current Constraints For Next Planning

- Do not force-push, merge to main, or modify external repos.
- Do not edit Datoviz repo from GSP_API; create handoff tasks for Datoviz-side API/binding gaps.
- Do not rely on Datoviz v0.3 Python plotting APIs.
- Do not make backend-native tick output the GSP conformance spec.
- Do not append generated axes/guides into `Figure.visuals()`.
- Do not implement real remote fetch, credentials, or plugin loading without a security ADR.
- Keep missions bounded enough for Codex/Claude worker agents.
- Use ChatGPT Pro only for architecture/spec/API decisions, not routine implementation.

## Question

Generate a larger next batch of stages, missions, and tasks for the project. The goal is to give
Mission Control enough upcoming work to run multiple bounded implementation/review cycles without
needing a new architecture consultation every time.

Please decide:

1. What should the next 6-10 stages be after S011?
2. Which stages should be sequential and which can be parallel?
3. Which tracks should be prioritized: Matplotlib strict guide provider, Datoviz v0.4 Python binding
   handoff, Datoviz query/capability parity, VisPy2 API growth, extension/data-source follow-up,
   conformance fixtures, packaging/docs?
4. What should be the exact next mission (`M012`) and the next several missions after it?
5. What work needs ChatGPT Pro again before implementation?
6. What work is safe for local Codex or worker agents without further consultation?

## Expected Output Format

Please respond with these sections.

### 1. Recommendation Summary

5-12 bullets with the strategic sequencing.

### 2. Stage Roadmap

A table with at least 6 and at most 10 stages:

```text
Stage ID | Title | Goal | Depends on | Parallelizable? | Why now
```

Use proposed stage IDs starting at `S012`.

### 3. Mission Batch

A table with at least 12 and at most 25 missions:

```text
Mission ID | Stage | Title | Goal | Agent type | Priority | Dependencies | Stop conditions
```

Use proposed mission IDs starting at `M012`.

Agent type should be one of:

```text
local-main-codex
codex-worker
claude-worker
chatgpt-pro-consultation
human-review
```

### 4. Immediate Next Mission Packet

Write a complete mission packet for `M012`, including:

- title;
- goal;
- required reading;
- expected tasks;
- allowed paths;
- forbidden paths;
- acceptance criteria;
- tests to run;
- stop conditions;
- review checklist.

### 5. Task Files To Create

List concrete `.agent/tasks/*.md` task files to create for the next batch. For each:

```text
Task file | Mission | Summary | Dependencies | Acceptance criteria
```

### 6. Datoviz Handoff Plan

Specific recommendations for Datoviz v0.4-dev binding/API gaps:

- what should remain in GSP_API;
- what should be a handoff to Datoviz;
- what evidence to collect from local headers/bindings;
- what not to implement in GSP_API.

### 7. Conformance Plan

Define the next conformance fixtures and tests:

- protocol model tests;
- Matplotlib reference tests;
- Datoviz skip-clean tests;
- query tests;
- guide/tick tests;
- tiled-source tests.

### 8. Risks And Stop Conditions

List project-level risks and exact stop conditions for worker agents.

### 9. ChatGPT Pro Follow-Up Triggers

List the exact future questions that should come back to ChatGPT Pro before implementation.

### 10. Mission Control Update Suggestions

Suggest what files Mission Control should update after this answer is accepted:

- `.agent/status.json`;
- `.agent/missions/*.md`;
- `.agent/tasks/*.md`;
- `STATUS.md` if applicable;
- specs/ADRs if applicable.

Do not propose implementation details that rely on v0.3 Datoviz plotting APIs or external docs not
confirmed by v0.4-dev headers/bindings.

## Desired Style

Be concrete and operational. Prefer bounded missions that can be executed, tested, reviewed, and
committed independently. Avoid vague roadmap items like "improve API" unless they are split into
specific tasks with acceptance criteria.
