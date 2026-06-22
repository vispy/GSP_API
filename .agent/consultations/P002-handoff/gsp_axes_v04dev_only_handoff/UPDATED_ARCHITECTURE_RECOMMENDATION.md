# Updated Architecture Recommendation — P002 Axes With Datoviz v0.4-dev Native Provider

## 1. Recommendation Summary

- Keep GSP v0.1 point/image-only; do not retrofit axes into the current MVP visual stream.
- Add semantic `Panel` and `View2D` first in v0.2; data visuals attach to a view, not to backend-local axes state.
- Add semantic guide objects next: `AxisGuide`, `TickSpec`, and `PanelTextGuide`.
- Add an **AxisRealizationProvider** layer so GSP can use Matplotlib native axes, Datoviz v0.4-dev native panel axes, GSP reference generated primitives, or future providers.
- Treat Datoviz v0.4-dev native axes as a first-class provider candidate, not merely a fallback-to-primitives backend.
- Treat Datoviz native auto ticks as an adaptation mode unless Datoviz can accept GSP-resolved explicit ticks or an equivalent declared tick policy.
- Keep query semantics semantic: guide contributions must be queryable when the provider supports guide queries, and explicitly `unsupported` when it does not.
- Preserve `Figure.visuals()` as user data visuals only. Generated axis visuals are provider artifacts, not user visuals.
- Use Matplotlib native artists for publication rendering, but drive them from GSP-resolved semantics in conformance mode.
- Use Datoviz v0.4-dev headers/bindings as source of truth; do not use v0.3-era Python plotting docs as implementation authority.

## 2. ADR Draft

### Title

Semantic Axis Intent With Capability-Resolved Axis Realization Providers

### Status

Proposed

### Context

GSP is a session protocol for semantic scientific visualization. VisPy2 produces GSP. Matplotlib is the reference/publication backend. Datoviz v0.4-dev is the flagship GPU backend.

The current VisPy2 MVP emits formal v0.1 `PointVisual` and `ImageVisual` objects and intentionally excludes axes, ticks, labels, transforms, layout, and navigation. Legacy axes code proves axes can be expanded into ordinary line/text visuals, but that erases semantic identity.

The Datoviz assumption has changed: the v0.4-dev branch exposes native panel/view/axis APIs. Therefore, the architecture must support multiple axis realization providers rather than a single primitive-expansion path.

### Decision

GSP will define semantic axis/view/guide intent. Backends will advertise one or more axis realization providers.

Core semantic objects:

- `Panel` / `PlotPanel`;
- `View2D`;
- `AxisGuide`;
- `TickSpec`;
- `PanelTextGuide`;
- `ResolvedGuideContribution` for query/readback.

Provider examples:

- `gsp.reference.generated_primitives.v0`;
- `matplotlib.native.axes.v0`;
- `datoviz.v04.panel_axis.wip`;
- future web/custom/extension providers.

The provider may render using native backend axes, generated primitives, retained composite objects, or other machinery. The provider does not own protocol truth; it owns realization.

### In scope

- 2D Cartesian axes.
- Linear X/Y domains.
- Explicit x/y limits.
- Optional autoscale resolved into explicit limits.
- Bottom X and left Y axes initially.
- Axis labels and panel title.
- Explicit ticks and one GSP reference automatic linear tick policy.
- Provider capabilities and diagnostics.
- Matplotlib strict conformance path.
- Datoviz v0.4-dev native-provider proof.
- Query scopes: `data`, `guides`, and `all-rendered`.

### Out of scope

- Broad Matplotlib API compatibility.
- v0.3 Datoviz Python plotting compatibility.
- Log/date/category/polar/3D/twin/secondary axes in the first mission.
- Pixel-perfect text/layout parity across backends.
- General layout engine.
- Legends, colorbars, annotations, grids beyond basic axis grid toggles.
- Stable pan/zoom public API before controller/session semantics are defined.

### Consequences

Positive:

- Preserves GSP semantic identity.
- Lets Matplotlib produce publication-quality output.
- Lets Datoviz use its native v0.4-dev panel-axis machinery.
- Provides clean fallbacks and diagnostics.
- Avoids making either Matplotlib or Datoviz the protocol spec.

Negative:

- Adds a provider/capability layer.
- Requires strict/adapted conformance modes.
- Requires careful query scoping for native guide contributions.
- Requires local Datoviz checkout verification because v0.4-dev is active/WIP.

### Open questions

- Can Datoviz v0.4-dev native axes accept explicit tick values/labels, or only policy-driven ticks?
- Can native Datoviz guide text/tick contributions be queried with semantic identity, or only rendered?
- Should provider selection be per-axis, per-panel, per-figure, or per-render request?
- Should GSP expose `backend-resolved` tick authority as a separate non-strict conformance mode?

## 3. Protocol Model

### Minimal panel/view state

```text
Panel
- id
- figure_id
- viewport_rect
- plot_rect
- reserved_adornment_bands
- background
- clip_policy

View2D
- id
- panel_id
- x_range: [xmin, xmax]
- y_range: [ymin, ymax]
- x_scale: linear
- y_scale: linear
- aspect_policy: auto | equal | numeric
- controller_id: optional
- data_to_view_transform_id: optional/future

VisualAttachment
- visual_id
- panel_id
- view_id
- coordinate_space: data | view | panel
- z_order
```

Rule: data visuals do not own axis limits. A visual attaches to a `View2D`; the `View2D` owns data-to-panel mapping.

### Ticks, labels, and title

```text
AxisGuide
- id
- view_id
- dimension: x | y
- side: bottom | top | left | right
- visible
- label_text
- spine_visible
- grid_visible
- tick_spec
- style_ref
- query_policy

TickSpec
- kind: none | explicit | auto-linear-nice-v0 | backend-adapted
- explicit_values: list[float]
- explicit_labels: list[str] | null
- target_count: int | null
- backend_policy_ref: optional

PanelTextGuide
- id
- panel_id
- role: title | subtitle | future
- text
- placement_policy
- query_policy
```

### Provider realization request

```text
AxisRealizationRequest
- panel_id
- view_id
- guide_ids
- provider_policy: auto | require_strict_gsp | prefer_native | require_native | disabled
- tick_authority: gsp_resolved | backend_resolved | explicit_only
- query_requirement: none | data_only | guides | all_rendered
- diagnostics_mode: error | warn | collect
```

### Queryability and identity

GSP low-level panel query asks: “what rendered contribution is under this panel coordinate?”

Use scopes:

- `data` — only user data visuals;
- `guides` — axes/ticks/tick labels/title/frame contributions;
- `all-rendered` — frontmost rendered contribution.

Native-provider query result must return at least:

```text
QueryResult
- status
- contribution_class: data | guide | overlay
- source_object_id
- source_object_type
- generated_contribution_id: optional
- role: spine | tick | tick-label | axis-label | title | data-item | texel
- axis_dimension: optional
- tick_value: optional
- text_value: optional
- displayed_rgba: optional
```

If Datoviz can render native axes but cannot query guide text/ticks, return `unsupported` for guide-scoped queries, not `miss`.

## 4. Producer API Guidance

### VisPy2 should expose now

Once `View2D` exists:

```python
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.get_xlim()
ax.get_ylim()
ax.autoscale()
```

These APIs map cleanly to `View2D` and should not be Matplotlib-only state.

### What should wait

Delay stable public APIs for:

```python
ax.set_title(...)
ax.set_xlabel(...)
ax.set_ylabel(...)
ax.set_xticks(...)
ax.set_yticks(...)
ax.tick_params(...)
ax.grid(...)
ax.twinx(...)
ax.secondary_xaxis(...)
```

Title/labels/ticks can be experimental only after semantic guide objects and provider rendering exist.

### Legacy reuse

Reuse legacy tick locator/formatter ideas, transform math, viewport mapping, and tests. Do not reuse legacy line/text axes as protocol truth.

## 5. Backend Guidance

### Matplotlib

Use native Matplotlib artists for output quality, but configure them from GSP state:

- set limits from `View2D`;
- set aspect from `View2D`;
- set ticks/labels from GSP-resolved `TickSpec` in strict mode;
- set title/xlabel/ylabel from semantic guide objects;
- emit diagnostics if Matplotlib native behavior overrides requested semantics.

### Datoviz v0.4-dev

Use Datoviz native panel-axis provider when possible:

- `dvz_panel_set_domain()` for X/Y data domains;
- `dvz_panel_set_view2d()` for 2D view policy;
- `dvz_panel_visible_domain()` for readback of controller-visible data domain;
- `dvz_panel_data_to_visual_positions()` or verified data-coordinate attachment for data mapping;
- `dvz_panel_axis()` for panel-owned X/Y axes;
- `dvz_axis_set_visible()`, `dvz_axis_set_grid()`, `dvz_axis_set_label()`, `dvz_axis_set_tick_policy()`, `dvz_axis_set_style()`, and `dvz_axis_set_plot_margins()` as supported.

Use Datoviz native ticks only in strict conformance if explicit GSP ticks or equivalent GSP-declared policy can be passed. Otherwise mark native ticks as backend-adapted.

## 6. Conformance Tests

- `Figure.visuals()` remains data-only.
- `View2D` serializes explicit x/y ranges.
- Matplotlib limits match `View2D` exactly.
- Strict Matplotlib ticks equal GSP-resolved ticks.
- Provider selection chooses Matplotlib native provider when requested.
- Provider selection chooses Datoviz v0.4-dev provider when capabilities match.
- Datoviz provider emits diagnostics if explicit ticks are requested but unsupported.
- Guide queries are included/excluded by scope.
- Datoviz guide-query unsupported returns `unsupported`, not `miss`.

## 7. Smallest next mission

Implement semantic `Panel` + `View2D` and provider capability declarations before implementing full ticks/labels. Then add a Datoviz v0.4-dev native provider proof with labels/tick policy only after local header/binding verification.

## 8. Risk Review

Main risk: accidentally turning GSP into “whatever native backend axes do.” Mitigation: semantic GSP objects remain authoritative; providers must declare strict versus adapted realization.

Second risk: relying on obsolete Datoviz v0.3 docs. Mitigation: only use `v0.4-dev` local headers/spec/examples for Datoviz implementation.
