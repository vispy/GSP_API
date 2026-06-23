# ADR-0010 - PointVisual screen-pixel diameter units

## Status

Accepted

## Context

S023 makes PointVisual the first complete visual-family proof across protocol semantics,
Matplotlib reference rendering, Datoviz v0.4 retained-scene rendering, and manual visual QA.

The prior point spec inherited Matplotlib `scatter(s=...)` semantics, where marker size is an area
in points squared. Datoviz v0.4 point visuals expose a `diameter` attribute instead. Letting either
backend define the protocol field would make cross-backend QA ambiguous.

## Decision

`PointVisual.sizes` means rendered screen-pixel diameter, either scalar or per-point.

The Matplotlib backend converts protocol diameters to `scatter(s=...)` area values using the active
figure DPI. The Datoviz v0.4 backend uploads protocol diameters directly to the point visual
`diameter` attribute.

The first Datoviz point proof uses explicit visual attachment descriptors. S023 NDC point fixtures
attach with `coord_space=DVZ_COORD_DATA` and rely on the default Datoviz `[-1, +1]` panel domain,
which matches the NDC fixture coordinates.

## Consequences

Backends must keep native marker-size units internal. Point and Marker can share screen-pixel
diameter semantics later without overloading PointVisual with marker shape, stroke, or colormap
scope.

Implementations must stop for review if a future backend cannot preserve rendered diameter semantics
or if coordinate-space mapping requires a non-default transform not represented in the protocol.
