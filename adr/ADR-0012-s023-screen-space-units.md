# ADR-0012 - S023 screen-space size and width units

## Status

Accepted

## Context

Backends expose incompatible native size units: Matplotlib scatter uses area in points squared,
Matplotlib linewidths use points, and Datoviz v0.4 exposes pixel-oriented attributes such as
`diameter_px` and `stroke_width_px`.

## Decision

Protocol visual size/width fields use rendered screen-pixel units:

- `PointVisual.sizes`: rendered screen-pixel diameter.
- `MarkerVisual.sizes`: rendered screen-pixel diameter.
- `MarkerVisual.stroke_width`: rendered screen-pixel width.
- `SegmentVisual.widths`: rendered screen-pixel width.
- `PathVisual.widths`: rendered screen-pixel width.

## Consequences

Backends must convert from protocol pixels to native units internally. Backend-native units are not
part of the protocol surface.
