# ADR-0014 - S023 coordinate-space mapping

## Status

Accepted

## Context

S023 visual QA cases are authored in normalized coordinates while high-level VisPy2 examples expose
semantic data coordinates and views.

## Decision

`CoordinateSpace.NDC` and `CoordinateSpace.DATA` are explicit protocol fields. S023 QA fixtures use
NDC coordinates in `[-1, +1]`. The Datoviz v0.4 adapter realizes those fixtures by configuring the
panel data domain to `[-1, +1]` with equal aspect when possible and attaching visuals in Datoviz data
coordinates. VisPy2 examples emit data-coordinate visuals with semantic `View2D` limits and render
through the Matplotlib reference path.

## Consequences

Backends must not infer coordinate semantics from array values alone. Future work may refine view,
attachment, and transform semantics, but S023 does not add general transform chains to visual-family
contracts.
