# ADR-002: Semantic Axis Intent With Axis Realization Providers

Status: Proposed

Date: 2026-06-22

## Context

GSP is a semantic visualization session protocol. VisPy2 produces GSP. Matplotlib is the reference/publication backend. Datoviz v0.4-dev is the flagship GPU backend.

The M008 VisPy2 MVP intentionally emits only `PointVisual` and `ImageVisual` protocol objects. It excludes axes, ticks, labels, layout, transforms, navigation, and styling. Legacy VisPy2 axes code expands axes into ordinary line/text visuals, which is useful implementation experience but erases semantic identity.

Datoviz v0.4-dev changes the implementation landscape. Its branch README positions v0.4-dev as the low-level engine surface for GSP/VisPy2, not as a v0.3 Python plotting compatibility layer. Its exported scene header exposes panel domains, `View2D` policy, panel-owned axes, tick policy, labels, style, grid, units, and datetime hooks.

Therefore, GSP should support native Datoviz axes when possible without making Datoviz native behavior the protocol specification.

## Decision

GSP will define semantic axis intent and stable identities. Backend adapters will realize that intent through declared axis realization providers.

Provider examples:

- `gsp.reference.generated_primitives.v0`
- `matplotlib.native.axes.v0`
- `datoviz.v04.panel_axis.wip`
- future extension providers

A provider may be strict or adapted:

- **Strict provider:** rendered limits/ticks/labels/query identity match GSP-resolved semantics.
- **Adapted provider:** backend-native machinery is used where exact GSP semantics cannot be represented; diagnostics describe the adaptation.

Generated line/text primitives are implementation artifacts, not user data visuals and not the primary GSP protocol representation of axes.

## In scope

- 2D Cartesian panels.
- Linear X/Y `View2D` ranges.
- Bottom X and left Y axes.
- Axis labels and panel title.
- Explicit tick specs.
- One GSP reference automatic linear tick policy.
- Capability-driven provider selection.
- Matplotlib native artist conformance mode.
- Datoviz v0.4-dev native provider proof.
- Query scopes separating data and guide contributions.

## Out of scope

- v0.3 Datoviz Python plotting API compatibility.
- Full Matplotlib API compatibility.
- Log/date/category/polar/3D/twin/secondary axes in the first mission.
- Pixel-perfect layout/text parity.
- General layout engine.
- Stable pan/zoom public API before controller/session semantics.

## Consequences

Positive:

- GSP remains semantic and backend-independent.
- Matplotlib can use native artists for publication output.
- Datoviz can use native v0.4-dev panel axes for GPU rendering.
- Fallbacks are explicit and testable.
- Query/readback can preserve semantic guide identity when supported.

Negative:

- Adds provider/capability complexity.
- Requires strict/adapted conformance distinctions.
- Requires Datoviz local checkout verification because v0.4-dev is active.
- Requires diagnostics whenever provider output diverges from GSP-resolved semantics.

## Implementation notes

For Datoviz, start with the local `v0.4-dev` checkout and verify these symbols before coding:

```bash
rg -n "dvz_panel_set_domain|dvz_panel_set_view2d|dvz_panel_axis|dvz_axis_set_label|dvz_axis_set_tick_policy|DvzAxisTickPolicy|DvzAxisStyle|DvzPanelView2D" include src spec examples tests datoviz
```

Do not call v0.3-style Python plotting wrappers from old examples unless they are explicitly present and supported in the v0.4-dev branch.

## Open questions

- Does Datoviz v0.4-dev support explicit tick values/labels for native axes?
- Can Datoviz native axis ticks/text be identified in query/probe results?
- Should provider selection be set globally, per figure, per panel, or per axis?
- What is the exact naming for adapted provider diagnostics?
