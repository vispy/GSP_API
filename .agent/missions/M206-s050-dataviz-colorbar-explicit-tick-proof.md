# M206 - S050 Datoviz colorbar explicit tick proof

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Validate whether the current local Datoviz v0.4 checkout is ready for strict GSP colorbar explicit
tick/label evidence. This is a bounded runtime/review proof, not a public API redesign.

## Required Context

- `.agent/S050_DATOVIZ_GUIDE_TEXT_COLORBAR_SCOPING.md`
- `.agent/S029_DATOVIZ_COLORBAR_HANDOFF.md`
- `.agent/S029_DATOVIZ_COLOR_COLORBAR_AUDIT.md`
- `spec/color_mapping.md`
- `spec/backends/datoviz.md`
- `src/gsp_datoviz/protocol_renderer.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `tests/test_visual_qa_harness.py`

## Deliverables

- Verify current Datoviz colorbar explicit tick/label symbols and source tests.
- Run or refresh a bounded GSP Datoviz colorbar review artifact.
- Decide whether stale S029 colorbar handoff blockers still apply.
- Update capability/release wording only if evidence passes.

## Acceptance

- Explicit tick values and labels are proven through the GSP Datoviz adapter path.
- No public `ColorbarGuide` contract changes are made.
- Colorbar query remains unsupported unless native guide-hit payload evidence covers colorbar parts.
- No sibling Datoviz files are edited.

## Stop Conditions

- Stop if local Datoviz runtime validation requires manual build-system or credential intervention.
- Stop before editing `/home/cyrille/GIT/Viz/datoviz`.
- Stop before promoting colorbar query without native colorbar guide-hit evidence.

## Result

Completed. See `.agent/S050_DATOVIZ_COLORBAR_EXPLICIT_TICK_PROOF.md`.

Focused adapter and visual-QA policy tests pass, and the local Datoviz facade exposes
`dvz_colorbar_set_ticks()`. The initial Datoviz offscreen review-pack run for
`color/scalar_image_viridis_colorbar` exited with code `139`, so no S050 colorbar promotion or
stale-blocker cleanup was made in M206.

M214 aligned GSP with the latest Datoviz v0.4-dev generated binding. The same colorbar case now
renders through real Datoviz offscreen review-pack evidence at
`artifacts/visual_qa/s050/m214-latest-colorbar/`.

Result: Datoviz rendered `color/scalar_image_viridis_colorbar` with review status `strict` and
reason code `datoviz_rendered_strict_s029_family_audit`. No `ColorbarGuide` contract changes were
made, and colorbar query remains unsupported pending native guide-hit payload evidence.
