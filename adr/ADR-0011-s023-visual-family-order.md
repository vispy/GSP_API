# ADR-0011 - S023 visual family order and scope

## Status

Accepted

## Context

S023 needed a practical order for introducing visual families while keeping manual visual QA small
and capability-gated across Matplotlib and Datoviz v0.4.

## Decision

S023 implements visual families in this order:

1. Point
2. Marker
3. Segment
4. Path
5. Image hardening

Text/Glyph and Mesh are deferred to later stages. Filled polygons, closed path fields, holes,
Beziers, dashes, colorbars, legends, volumes, and tiled/remote images are also deferred.

## Consequences

Each family gets protocol validation, Matplotlib reference mapping, Datoviz v0.4 mapping or explicit
unsupported diagnostics, VisPy2 producer coverage where appropriate, and visual QA cases before the
next family begins.
