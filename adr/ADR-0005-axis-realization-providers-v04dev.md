# ADR-0005 - Semantic axis intent with axis realization providers

## Status

Accepted

## Context

GSP is a semantic visualization session protocol. VisPy2 produces GSP. Matplotlib is
the reference/publication backend. Datoviz v0.4-dev is the flagship GPU backend.

The M008 VisPy2 MVP intentionally emits only `PointVisual` and `ImageVisual`
protocol objects. It excludes axes, ticks, labels, layout, transforms, navigation,
and styling. Legacy VisPy2 axes code expands axes into ordinary line/text visuals,
which is useful implementation experience but erases semantic identity.

Datoviz v0.4-dev changes the implementation landscape. Its local checkout on branch
`v0.4-dev` exposes panel domains, `View2D` policy, panel-owned axes, tick policy,
labels, style, grid, units, and datetime hooks in `include/datoviz/scene.h`.

## Decision

GSP defines semantic axis intent and stable identities. Backend adapters realize that
intent through declared axis realization providers.

Initial provider IDs:

- `gsp.reference.generated_primitives.v0`
- `matplotlib.native.axes.v0`
- `datoviz.v04.panel_axis.wip`

A provider may be strict or adapted:

- strict providers render limits/ticks/labels/query identity from GSP-resolved semantics;
- adapted providers use backend-native behavior where exact GSP semantics cannot be represented,
  with diagnostics describing the adaptation.

Generated line/text primitives are backend realization artifacts. They must not be
appended to VisPy2 `Figure.visuals()` as user data visuals.

## In Scope

- 2D Cartesian panels.
- Linear X/Y `View2D` ranges.
- Bottom X and left Y axes.
- Capability-driven provider selection.
- Matplotlib native artist conformance for `View2D` limits.
- Datoviz v0.4-dev native provider discovery based on verified local headers/bindings.

## Out of Scope

- v0.3 Datoviz Python plotting API compatibility.
- Full Matplotlib API compatibility.
- Log/date/category/polar/3D/twin/secondary axes.
- Pixel-perfect layout/text parity.
- Stable pan/zoom public API before controller/session semantics.

## Consequences

GSP remains semantic and backend-independent while Matplotlib and Datoviz can use
native axis machinery. Provider capability declarations must distinguish strict from
adapted behavior, especially for native auto ticks and guide query support.

Datoviz implementation must use `github.com/datoviz/datoviz` branch `v0.4-dev` and
local `include/datoviz/` headers as source of truth. `datoviz.org` and v0.3-era
`panel.axes(...)` examples are not authoritative for this mission.
