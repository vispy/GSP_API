# M067-S023-MARKERVISUAL-V1 - MarkerVisual v1

## Mission

M067

## Goal

Introduce markers as a distinct protocol visual family rather than overloading PointVisual.

## Contract Starting Point

Use P008 as authority. Suggested v1 fields:

```text
id
positions
shape
fill_colors
sizes
angle
stroke_color
stroke_width
coordinate_space
```

Recommended shape vocabulary should favor Datoviz-supported built-ins that Matplotlib can
approximate. Start conservative, for example disc/circle, square, triangle, diamond, cross if
Datoviz and Matplotlib both support acceptable mappings. Capability-gate anything uncertain.

## Backend Mapping

- Matplotlib: use scatter markers or PathCollection equivalents; convert protocol diameter pixels
  to Matplotlib area.
- Datoviz v0.4: use `dvz_marker(scene, flags)` plus dense uploads for position/color/diameter/angle
  and symbol/shape. Verify exact enum names through M064 probe and `../datoviz/`.

## Acceptance

- Marker validation tests cover scalar/per-item shape decisions, colors, sizes, angle, stroke.
- Matplotlib QA outputs exist.
- Datoviz outputs or structured unsupported diagnostics exist.
- No custom symbols or font/SDF marker systems are introduced.

## Stop Conditions

- Stop if marker shape vocabulary becomes broader than verified v0.4/Matplotlib support.
- Stop if stroke semantics require a new rendering model beyond simple v1 fill/stroke.
