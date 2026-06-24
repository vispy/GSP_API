# S023 Visual Family Contracts Decision Record

Status: accepted and closed by M072.

## Accepted families

S023 accepted protocol v1 contracts for:

- PointVisual
- MarkerVisual
- SegmentVisual
- PathVisual
- ImageVisual

The authoritative specs are indexed in `SPEC_INDEX.md` and summarized in
`spec/visual_families_v1.md`.

## Proved backend state

The latest local visual QA pack at `artifacts/visual_qa/s023/latest-local/` rendered all 13 S023
cases in both Matplotlib and Datoviz v0.4 with the local generated Datoviz binding active.

## Deferred scope

Text/Glyph and Mesh are not S023 families. They should be scoped explicitly in the next stage rather
than inferred from legacy source code. Other deferred topics include filled polygons, closed path
fields, dashes, arrows, colorbars, broad colormap registries, remote/tiled images, volumes, and
scientific readback.

## Follow-ups

- S024 should choose Text/Glyph or Mesh as the next visual-family stage.
- Datoviz follow-ups should target backend-native colormap expansion, text/glyph/mesh parity,
  scientific readback, and non-S023 query scopes only after a stage explicitly approves them.
