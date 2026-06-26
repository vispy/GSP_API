# P013 - Post-S028 Visual QA and Datoviz Capability Promotion

## Prompt for ChatGPT Pro

You are advising on GSP_API, a backend-agnostic scene-description and visualization protocol for
Python scientific visualization. The project has completed stages S001-S028. We need a rigorous
post-S028 plan for visual-family coverage, Datoviz capability promotion, and manual visual review
artifacts.

This prompt is self-contained. Do not assume access to local files.

## Project Context

GSP_API has these completed visual/interaction stages:

- S023 Visual Families v1 and Manual Visual QA Foundation.
- S024 Text/Glyph Visuals v1.
- S025 Mesh and 3D Geometry Visuals v1.
- S026 Color Mapping, Colorbars, and Scalar Data Semantics.
- S027 Transform, View, Camera, and Navigation Semantics.
- S028 Guide and View2D Integration.

Current design principles:

1. GSP protocol must stay backend-agnostic. It must not expose Datoviz slot names, Matplotlib
   artist internals, GPU shader handles, or backend material structs.
2. Matplotlib is the strict publication/reference backend for 2D behavior.
3. Datoviz v0.4 is the intended high-performance GPU backend.
4. Datoviz support must be capability-gated: missing or unverified semantics produce structured
   unsupported/adapted diagnostics, not silent fallbacks.
5. Existing source code is implementation material, but specs/ADRs are higher authority.
6. Guide picking/query is explicitly deferrable for Datoviz v0.4 RC. Guide rendering matters more
   than guide picking for the current scope.

## Current GSP Visual Families

S023 families:

- `PointVisual`: NDC/DATA positions, RGBA, pixel diameters.
- `MarkerVisual`: marker shapes, RGBA, angle, size/stroke semantics.
- `SegmentVisual`: independent line segments, stroke widths, caps.
- `PathVisual`: ordered vertices/subpaths, stroke width/caps/joins.
- `ImageVisual`: bounded eager image, RGBA/scalar gray, origin/interpolation/extent.
- Overlay cases such as point over image.

S024:

- `TextVisual`: printable text, position, anchors, font-size in logical pixels, RGBA, rotation,
  multiline/Unicode smoke. Public glyph resources are intentionally deferred.

S025:

- `MeshVisual`: inline indexed triangle mesh.
- Strict v1 path is 2D filled triangles in NDC/DATA, uniform RGBA or per-face RGBA, flat colors,
  deterministic visual order, and 2D face query payloads.
- `(N,3)` positions are valid protocol data but require accepted 3D view/camera/projection
  capability for strict rendering/query.
- Public geometry resources, materials, textures, instancing, PBR, public lights, external model
  files, and guaranteed 3D Matplotlib conformance are deferred.

S026:

- `ColorScale`, canonical named colormaps, explicit linear normalization, scalar encodings for
  image/point/marker where supported, semantic `ColorbarGuide`, and scalar query payloads.

S027:

- finite invertible 2D affine transforms, transform resources/bindings, deterministic `View2D`,
  transform query inverse payloads where supported.
- Public 3D camera/projection/controller semantics are deferred.

S028:

- semantic `AxisGuide` and `PanelTextGuide` consume the same `View2D` snapshot as data rendering.
- reversed finite x/y `View2D` limits are valid.
- explicit ticks/labels are preserved exactly in strict reference paths.
- guide query/all-rendered query uses same `View2D` snapshot where supported.
- Datoviz guide query is explicitly deferred.

## Current Visual QA Harness

GSP has a visual QA harness with suites S023-S028. It can produce per-case contact sheets with
Matplotlib on the left and Datoviz on the right. It writes:

- per-case PNGs by backend;
- contact sheets;
- summary markdown;
- structured unsupported JSON for unsupported backend cases.

Current registered S028 visual QA cases:

- `point/basic_ndc`
- `point/diameter_ramp_ndc`
- `point/alpha_overlap_ndc`
- `marker/shapes_ndc`
- `marker/angle_size_stroke_ndc`
- `segment/width_cap_ndc`
- `segment/alpha_order_ndc`
- `path/subpaths_width_join_ndc`
- `image/checker_nearest_ndc`
- `image/origin_lower_ndc`
- `image/scalar_gray_clim_ndc`
- `image/rgba_alpha_ndc`
- `overlay/point_over_image_ndc`
- `text/basic_ndc`
- `text/anchor_grid_ndc`
- `text/rotation_alpha_ndc`
- `text/data_vs_ndc`
- `text/multiline_unicode_smoke`
- `mesh/single_triangle_uniform_ndc_2d`
- `mesh/indexed_square_uniform_ndc_2d`
- `mesh/indexed_square_per_face_ndc_2d`
- `color/scalar_image_viridis_colorbar`
- `color/point_scalar_gray_range`
- `color/marker_scalar_fill_alpha`
- `transform/inline_named_equivalence`
- `transform/view2d_data_ndc_overlay`
- `transform/family_affine_view2d`
- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

Current artifact status:

- Existing local contact sheets are mostly Matplotlib-only.
- Datoviz offscreen QA is disabled by default because native offscreen view creation can abort the
  Python process. It is opt-in via `GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1`.
- The harness can show unsupported tiles on the Datoviz side.

## Current GSP Datoviz Adapter Status

GSP targets Datoviz v0.4 through the top-level C-shaped Python facade, `import datoviz as dvz`, with
`dvz_*` function names and generated raw ctypes under `datoviz.raw`.

Current GSP adapter behavior:

- Advertised `visual_families` in conservative capability snapshot are currently `("point",
  "image")`, even though implementation methods exist for marker, segment, path, and image when
  Datoviz facade symbols are present.
- Point: implemented for NDC positions, RGBA, pixel diameter.
- Marker: implemented for NDC positions, RGBA, diameter, angle, shape when required symbols exist;
  scalar marker fill is currently gated/unsupported.
- Segment: implemented for NDC positions, RGBA, stroke width/caps when symbols exist.
- Path: implemented for NDC positions, RGBA, stroke width/caps/joins/subpaths when symbols exist.
- Image: implemented for scalar gray and RGB/RGBA bounded eager images, preferring sampled fields
  when symbols exist.
- Text: GSP adapter currently raises structured unsupported because Datoviz text placement, anchors,
  font-size mapping, rotation, and font-role semantics are not verified in the adapter.
- Mesh: GSP adapter currently raises structured unsupported because Datoviz mesh flat RGBA,
  per-face color adaptation, 2D z=0 mapping, topology preservation, and face query semantics are
  not verified in the adapter.
- Colorbar: GSP adapter currently raises structured unsupported for `ColorbarGuide` because native
  colorbar layout, scale binding, tick-label, and ramp-query contracts are not verified.
- Axes/guides: Datoviz v0.4 panel axis provider is modeled as `datoviz.v04.panel_axis.wip`,
  provider status `adapted`, supports backend auto ticks, does not support explicit GSP ticks,
  does not support guide query, and has strict reversed-domain proof unverified.
- Query: Datoviz data-scope point/image runtime query wrapper exists for frontmost panel-coordinate
  requests when query bindings are available. Guide scope and all-rendered-with-guides return
  structured unsupported. Live query payload parity still needs richer visual family/item/texel/
  displayed RGBA/value proof.
- Transform: finite eager NDC Point/Marker/Segment/Path inline 2D affine transforms may be CPU
  pre-transformed before upload. Named resources, DATA-space adaptation, transform query inverse,
  image affine, mesh/text transforms, 3D camera/projection/controller semantics, and virtual-source
  materialization are unsupported.

The user reports that Datoviz v0.4-dev itself already supports text, mesh, and colorbars. Therefore
the main issue is likely GSP adapter verification/promotion and exact semantic contracts, not
necessarily missing Datoviz engine functionality.

## Datoviz-Side Plan Already Created

A Datoviz repo implementation plan has been written for a separate coding agent. Its main requested
Datoviz-side confirmations/additions are:

1. Stable panel `View2D`/domain API shared by axes and data visuals.
2. Explicit axis tick values and labels.
3. Reversed finite domains.
4. Grid lines aligned to ticks.
5. Axis labels and panel text/title.
6. Complete data query payloads.
7. Colorbar, text, and mesh contracts documented and exposed through Python facade calls.
8. Guide picking/query explicitly deferred for RC.

## Decision Problem

We need to decide what GSP should do next after S028.

The user wants to review images with Matplotlib on the left and Datoviz on the right for the various
examples, especially visual families and 3D. The user also believes Datoviz should already support
text, mesh, colorbars, and many visual features. We need a staged plan that:

- avoids pretending unverified Datoviz semantics are strict;
- does not block on guide picking;
- gets useful visual review artifacts quickly;
- distinguishes 2D strict parity from Datoviz-native/experimental 3D;
- makes it clear which gaps are GSP adapter work vs Datoviz engine/API work;
- keeps public 3D camera/projection/controller semantics under control.

## Questions

1. What should S029 be? Should it be a release/API consolidation stage, a visual QA review pack
   stage, a Datoviz promotion stage, or something else?
2. What is the correct policy for promoting Datoviz text, mesh, and colorbar support from
   unsupported/unverified to adapted or strict?
3. How should GSP structure Matplotlib-left / Datoviz-right visual review artifacts when Datoviz
   supports a feature but GSP has not yet verified exact semantics?
4. For 3D specifically, what should GSP review now?
   - 2D `MeshVisual` triangle cases only?
   - fixed-camera 3D visual QA as non-strict artifact?
   - a new 3D protocol stage requiring a separate ADR/consultation?
5. Should GSP’s Datoviz adapter first broaden family rendering support (text/mesh/colorbar) or first
   build a formal backend capability matrix and review-pack generator?
6. What exact stop conditions should prevent broadening into an unstable 3D design?

## Expected Output Format

Return a concrete recommendation with these sections:

1. `Executive Recommendation`: 5-10 sentences.
2. `S029 Scope`: stage title, goal, non-goals, and why.
3. `Mission Plan`: 4-8 missions with IDs/titles, deliverables, acceptance criteria, and stop
   conditions.
4. `Capability Promotion Rules`: strict/adapted/unsupported criteria for Datoviz text, 2D mesh,
   colorbar, axes/guides, query payloads, and 3D mesh.
5. `Visual Review Artifact Plan`: how to produce Matplotlib-left / Datoviz-right sheets, how to
   represent unsupported/adapted cases, and what summary matrix to generate.
6. `3D Policy`: what to do now, what to defer, and what requires a separate architecture decision.
7. `Datoviz vs GSP Work Split`: what belongs in Datoviz, what belongs in GSP adapter, and what can
   be done in parallel.
8. `Immediate Next Action`: the single best next mission to implement in GSP.

