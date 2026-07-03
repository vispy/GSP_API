# M214 - Datoviz v0.4-dev Latest Generated-Binding Alignment

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Align GSP's Datoviz adapter with the current Datoviz v0.4-dev C API and generated Python binding.
Replace stale coordinate, image upload, texture, and View3D camera API usage with current generated
binding symbols only. Do not add aliases, compatibility shims, or fake acceptance gates.

## Required Context

- `.agent/S050_DATOVIZ_OFFSCREEN_CRASH_ISOLATION.md`
- `.agent/S050_DATOVIZ_COLORBAR_EXPLICIT_TICK_PROOF.md`
- `.agent/S050_DATOVIZ_RETAINED_VIEW3D_DEPTH_PROOF.md`
- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp_datoviz/latest_api_contract.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `tests/test_visual_qa_harness.py`
- `ANSWER`

## Deliverables

- Define a single latest Datoviz generated-binding contract in GSP.
- Use `DvzVisualCoordSpace` plus `DVZ_VISUAL_COORD_VIEW`, `DVZ_VISUAL_COORD_DATA`, and
  `DVZ_VISUAL_COORD_PANEL`.
- Use sampled-field APIs for scalar/mapped images and `dvz_visual_set_texture_rgba8` for already
  packed RGBA8 images.
- Use retained View3D descriptors: `dvz_panel_view3d_desc`, `dvz_panel_set_view3d_desc`, and
  `dvz_panel_camera`.
- Rerun S028 colorbar and S050 retained-depth review-pack cases against real Datoviz.

## Stop Conditions

- Stop before editing `/Users/cyrille/GIT/Viz/datoviz` without explicit approval.
- Stop if a required current Datoviz v0.4-dev generated binding symbol is missing.
- Stop if retained View3D descriptor setup cannot be driven from Python.
- Stop if real rendering/camera/depth behavior fails after stale symbol blockers are removed; record
  runtime evidence instead of inventing a compatibility path.
- Stop before promoting colorbar strictness or strict opaque depth without completed runtime evidence.

## Acceptance

- No GSP implementation, tests, docs, or specs reference stale Datoviz coordinate, generic texture,
  or detached-camera symbols.
- GSP uses the current Datoviz v0.4-dev generated binding symbols listed in this mission.
- Real generated-binding smoke passes with `PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz`.
- S028 and S050 review-pack runs execute against real Datoviz.
- S050 no longer stops at stale coordinate imports or detached-camera symbol gates.
- Any remaining S050 failure is classified as runtime evidence.
- Fake/mock tests are not the acceptance gate.

## Evidence

- Real binding smoke imported `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py` and verified
  35 current required symbols, including coordinate values `0`, `1`, and `2`.
- `artifacts/visual_qa/s050/m214-latest-colorbar/` rendered S028
  `color/scalar_image_viridis_colorbar` in Matplotlib and Datoviz; Datoviz status is `strict`.
- `artifacts/visual_qa/s050/m214-latest-depth/` rendered S050
  `mesh3d/opaque_depth_intersecting_triangles_view3d` in Matplotlib and Datoviz; Datoviz status
  remains `adapted` pending promotion audit, not stale-symbol failure.
