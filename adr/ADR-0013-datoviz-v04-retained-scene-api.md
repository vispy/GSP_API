# ADR-0013 - Datoviz v0.4 retained scene API boundary

## Status

Accepted

## Context

GSP inherited legacy Datoviz code targeting v0.3-style Python wrappers. S023 needed a stable target
for Datoviz v0.4 visual-family work.

## Decision

GSP's Datoviz v0.4 adapter targets the retained scene facade: `dvz_scene`, `dvz_figure`,
`dvz_panel_full`, retained visual constructors, `dvz_visual_set_data`, explicit attach descriptors,
sampled-field/texture image binding, and v0.4 query/capture helpers when available.

The adapter must not use Datoviz v0.3 wrapper APIs or `dvz_*_alloc` allocation functions.

## Consequences

Datoviz support is capability-gated on actual facade symbols. Missing helpers produce structured
unsupported diagnostics. Local generated bindings may be needed to exercise the live v0.4 path.
