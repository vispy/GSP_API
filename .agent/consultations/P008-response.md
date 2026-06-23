# S023 — Visual Families v1 and Manual Visual QA Foundation

**Corrected Datoviz v0.4-dev architecture review**  
Generated: 2026-06-23  
Requested correction: remove v0.3-style visual API drift such as `dvz_path_alloc`; base Datoviz guidance on the actual `datoviz/datoviz` `v0.4-dev` branch.

## Source Audit Summary

This revised plan was checked against the public `datoviz/datoviz` GitHub repository on branch `v0.4-dev`.

Important audited facts:

- Datoviz `v0.4-dev` is a **C-first retained scene API** around scene/figure/panel/visual objects, DRP2 frame artifacts, and native Vulkan/vklite/canvas runtime. It is **not** a compatibility layer for the v0.3 Python plotting API.
- The branch’s README says the release-facing surfaces include the C scene/app API under `include/datoviz/`, generated `datoviz.raw` ctypes bindings, and a top-level `import datoviz as dvz` array-aware direct-engine facade.
- The v0.4 README minimal Python example uses `dvz_scene()`, `dvz_figure()`, `dvz_panel_full()`, `dvz_point(scene, flags)`, `dvz_visual_set_data(visual, "position" | "color" | "diameter", array)`, `dvz_panel_add_visual(...)`, and `dvz.run(...)`.
- The package entry point exposes `run(scene, figure, ...)`, `capture(scene, figure, path, ...)`, and delegates `dvz_*`/`Dvz*` names to the generated array-aware facade. `datoviz.raw` imports generated ctypes bindings.
- The v0.4 C API uses **visual constructors plus generic dense attribute upload**:
  - `dvz_point(scene, flags)`
  - `dvz_marker(scene, flags)`
  - `dvz_segment(scene, flags)`
  - `dvz_path(scene, flags)`
  - `dvz_image(scene, flags)`
  - `dvz_visual_set_data(...)`
  - `dvz_visual_set_data_many(...)`
  - `dvz_visual_set_data_range(...)`
- The v0.4 branch does **not** expose or expect v0.3-style functions such as `dvz_path_alloc`, `dvz_point_alloc`, `dvz_point_position`, `dvz_marker_color`, or `dvz_segment_linewidth`.
- The v0.4 examples in `examples/c/visuals/` confirm the actual retained attribute names:
  - Point: `"position"`, `"color"`, `"diameter"`.
  - Marker: `"position"`, `"color"`, `"diameter"`, `"angle"`, `"symbol"`; the header also documents `"shape"`/`"symbol"` for built-in symbol IDs.
  - Segment: `"position_start"`, `"position_end"`, `"color"`, `"stroke_width"`.
  - Path: `"position"`, `"color"`, optional `"stroke_width"`, plus `dvz_path_set_subpaths(...)`, `dvz_path_set_caps(...)`, and `dvz_path_set_join(...)`.
  - Image: `dvz_image(...)`, corner `"position"` + `"texcoords"` in the example, scalar `DvzSampledField`, `dvz_visual_set_field(image, "field", field)`, and `dvz_visual_set_scale(image, "color", scale)`.
- The branch defines `DvzVisualAttachDesc` with `z_layer`, `controller_mode`, and `coord_space`. The documented default for `dvz_panel_add_visual(..., NULL)` is `coord_space=DATA`, so GSP’s Datoviz adapter must not assume a NULL attach descriptor means GSP NDC semantics.

Sources inspected are listed at the end of this file.

---

## 1. Executive Recommendation

1. **S023 should still be “Visual Families v1 and Manual Visual QA Foundation,” but the Datoviz mission must start with a v0.4 API probe.** No implementation task should mention `_alloc` or family-specific v0.3 setter functions except in a banned-symbol test.

2. **Datoviz v0.4 adapter code should target retained scene objects and generic data uploads.** The implementation pattern is: create `scene/figure/panel`, create a visual with `dvz_<family>(scene, flags)`, upload dense attributes with `dvz_visual_set_data*`, configure style helpers where available, add the visual to a panel with an explicit `DvzVisualAttachDesc`, then run/capture.

3. **Matplotlib remains the semantic reference backend.** Every S023 family must first have a Matplotlib reference mapping and manual visual QA artifacts.

4. **Datoviz v0.4 remains the flagship GPU backend, but capability-gated.** The adapter must emit a structured report when a Python facade symbol, C raw symbol, capture function, image sampler control, coordinate-space mapping, or style helper is missing.

5. **Point → Marker → Segment → Path → Image hardening remains the right implementation order, with one correction: Image should be exercised early as a QA smoke family but hardened after Point/Marker/Segment/Path.**

6. **GSP protocol fields remain backend-independent.** Datoviz attribute names such as `"diameter"`, `"symbol"`, and `"stroke_width"` are adapter implementation details, not protocol field names unless they also make semantic sense.

7. **Use pixel units for sizes and stroke widths.** This now aligns cleanly with Datoviz v0.4’s `"diameter"` and `"stroke_width"` attributes and fixes the earlier ambiguity around Matplotlib scatter’s `s` area parameter.

8. **The QA harness should create side-by-side contact sheets and a machine-readable report.** Automatic checks should validate scene construction, schema, artifact existence, backend capability reporting, and non-empty images. Human review should judge semantic visual equivalence.

9. **Text/Glyph and Mesh remain out of S023 implementation scope.** The v0.4 API exposes text/glyph/mesh families, but they require font, atlas, 3D, lighting, material, and query decisions that should not destabilize the first visual-family pass.

10. **Every Datoviz mission must include an “actual v0.4 API evidence” artifact.** This should be a JSON matrix generated from the local installed package and the sibling `../datoviz/` source, including the exact callable names used.

---

## 2. S023 Stage Definition

**Stage id/title:**  
`S023 — Visual Families v1 and Manual Visual QA Foundation`

**Goal:**  
Define and implement stable v1 protocol contracts, VisPy2/GSP producer APIs, Matplotlib reference renderers, Datoviz v0.4 retained-scene adapters, and a manual visual QA harness for the early visual families: Point, Marker, Segment, Path, and Image.

**Non-goals:**

- No remote data, networking, security, extension-host, or virtual data-source work.
- No broad legacy renderer migration.
- No dependence on the legacy `gsp_datoviz.renderer` path.
- No v0.3 Datoviz API names in implementation plans or probes, except in explicit banned-symbol regression tests.
- No Text/Glyph implementation.
- No Mesh implementation.
- No pixel-perfect cross-backend image diffing.
- No requirement to serialize local rendering arrays through JSON/base64.
- No attempt to expose Datoviz-specific draw calls as GSP protocol concepts.

**Completion criteria:**

1. `spec/` documents cross-cutting visual rules and v1 contracts for Point, Marker, Segment, Path, and Image.
2. The visual QA CLI renders an S023 suite through Matplotlib and Datoviz v0.4.
3. Every QA case emits:
   - formal protocol scene fixture;
   - NumPy sidecar arrays where needed;
   - Matplotlib PNG;
   - Datoviz PNG or structured unsupported report;
   - JSON run report;
   - contact sheet;
   - manual notes template.
4. Datoviz adapter capability reports list actual v0.4 retained-scene symbols and never list `_alloc` functions as expected symbols.
5. Point, Marker, Segment, Path, and Image all have VisPy2/GSP producer APIs.
6. Matplotlib reference rendering exists for all five families.
7. Datoviz v0.4 support is implemented or capability-gated for all five families.
8. At least the Point NDC case should produce a Datoviz PNG unless a documented local v0.4 build/capture blocker is accepted by a human reviewer.
9. Manual visual QA notes exist for the final S023 artifact pack.
10. Tests prevent new S023 code from importing or wrapping the legacy Datoviz renderer.

**Major risks:**

- The generated top-level `datoviz` array-aware facade may not be present in the installed venv.
- The raw ctypes module may exist while array-aware NumPy conversion is missing.
- Datoviz image interpolation/sampler controls may not yet be surfaced in the retained scene API.
- GSP `NDC`/`DATA` coordinate semantics can drift if Datoviz’s `DvzVisualAttachDesc.coord_space` is not set explicitly.
- Matplotlib and Datoviz antialiasing/stroke behavior will differ.
- Path v0.4 expects per-point color/width arrays while GSP v1 should probably expose per-path color/width semantics.
- Manual QA can become informal unless the harness produces repeatable contact sheets and notes.

---

## 3. Visual QA Harness Contract

### CLI shape

Required commands:

```bash
python -m gsp.qa.visual list --suite s023

python -m gsp.qa.visual probe-datoviz-v04 \
  --source ../datoviz \
  --out artifacts/visual_qa/s023/datoviz_v04_probe

python -m gsp.qa.visual run \
  --suite s023 \
  --backends matplotlib,datoviz-v04 \
  --out artifacts/visual_qa/s023/<run_id> \
  --contact-sheet

python -m gsp.qa.visual run \
  --suite s023 \
  --case point/basic_ndc \
  --case marker/shapes_ndc \
  --backends matplotlib \
  --out artifacts/visual_qa/s023/dev

python -m gsp.qa.visual merge-notes \
  --run artifacts/visual_qa/s023/<run_id> \
  --notes artifacts/visual_qa/s023/<run_id>/manual_notes.yaml
```

Useful optional flags:

```bash
--strict
--allow-unsupported datoviz-v04
--resolution 800x600
--seed 1234
--write-scene-json
--write-scene-npz
--no-contact-sheet
--datoviz-backend facade
--datoviz-backend raw
```

`--strict` should fail on schema errors, renderer exceptions, missing Matplotlib artifacts, or malformed unsupported diagnostics. It should not fail just because Datoviz reports an unsupported capability, unless a mission declares that capability mandatory.

### Python module/script layout

```text
gsp/qa/visual/
  __init__.py
  cli.py
  registry.py
  case_spec.py
  cases.py
  runner.py
  artifacts.py
  report_schema.py
  contact_sheet.py
  manual_notes.py
  datoviz_probe.py
  capability_report.py

gsp/qa/visual/cases/
  s023_point.py
  s023_marker.py
  s023_segment.py
  s023_path.py
  s023_image.py
  s023_overlay.py

gsp/backends/matplotlib/
  visual_renderers.py

gsp/backends/datoviz_v04/
  renderer.py
  facade.py
  raw.py
  capabilities.py
  upload.py
  styles.py
  coordinate_space.py
```

### Artifact directory layout

```text
artifacts/visual_qa/s023/<run_id>/
  run_manifest.json
  environment.json
  report.json
  summary.md
  manual_notes.yaml

  datoviz_v04_probe/
    probe_report.json
    facade_symbols.json
    raw_symbols.json
    capability_matrix.json
    banned_symbol_check.json

  scenes/
    point_basic_ndc.scene.json
    point_basic_ndc.arrays.npz
    marker_shapes_ndc.scene.json
    ...

  backends/
    matplotlib/
      point_basic_ndc.png
      point_basic_ndc.log.txt
      ...
    datoviz-v04/
      point_basic_ndc.png
      point_basic_ndc.unsupported.json
      point_basic_ndc.log.txt
      ...

  contact_sheets/
    point_basic_ndc.png
    family_point.png
    s023_all_cases.png

  notes/
    point_basic_ndc.md
    marker_shapes_ndc.md
    ...
```

### Required output files

Each complete run must produce:

- `run_manifest.json`
- `environment.json`
- `report.json`
- `summary.md`
- `manual_notes.yaml`
- one scene fixture per case
- one Matplotlib PNG per case
- one Datoviz PNG or one Datoviz unsupported JSON per case
- contact sheets when two or more backends are requested
- Datoviz v0.4 probe output

### JSON report schema

```json
{
  "schema_version": "gsp.visual_qa.report.v1",
  "stage": "S023",
  "run_id": "2026-06-23T12-00-00Z-dev",
  "created_at": "ISO-8601",
  "environment": {
    "python": "...",
    "platform": "...",
    "gsp_revision": "...",
    "matplotlib_version": "...",
    "datoviz_import_status": "available|unavailable",
    "datoviz_import_path": "...",
    "datoviz_source_path": "../datoviz",
    "datoviz_source_revision": "..."
  },
  "datoviz_v04_probe": {
    "facade_available": true,
    "raw_available": true,
    "array_facade_available": true,
    "capture_available": true,
    "banned_v03_symbols_found": [],
    "required_v04_symbols": {
      "dvz_scene": "found",
      "dvz_figure": "found",
      "dvz_panel_full": "found",
      "dvz_panel_add_visual": "found",
      "dvz_visual_set_data": "found",
      "dvz_visual_set_data_many": "found",
      "dvz_point": "found",
      "dvz_marker": "found",
      "dvz_segment": "found",
      "dvz_path": "found",
      "dvz_image": "found"
    }
  },
  "cases": [
    {
      "case_id": "point/basic_ndc",
      "family": "point",
      "scene": {
        "json": "scenes/point_basic_ndc.scene.json",
        "arrays": "scenes/point_basic_ndc.arrays.npz"
      },
      "required_features": [
        "visual.point",
        "coordinate_space.ndc",
        "color.rgba8",
        "size.diameter_px"
      ],
      "backend_results": {
        "matplotlib": {
          "status": "rendered",
          "artifact": "backends/matplotlib/point_basic_ndc.png",
          "warnings": [],
          "errors": []
        },
        "datoviz-v04": {
          "status": "rendered|unsupported|error",
          "artifact": "backends/datoviz-v04/point_basic_ndc.png",
          "unsupported": null,
          "warnings": [],
          "errors": []
        }
      },
      "manual": {
        "status": "unreviewed",
        "reviewer": null,
        "reviewed_at": null,
        "notes_file": "notes/point_basic_ndc.md"
      }
    }
  ],
  "summary": {
    "case_count": 0,
    "matplotlib_rendered_count": 0,
    "datoviz_rendered_count": 0,
    "unsupported_count": 0,
    "error_count": 0,
    "manual_unreviewed_count": 0
  }
}
```

### Unsupported/capability-gated cases

Unsupported cases must be explicit data, not missing files:

```json
{
  "status": "unsupported",
  "backend": "datoviz-v04",
  "reason_code": "missing_symbol|facade_missing|raw_missing|capture_missing|unsupported_coordinate_space|unsupported_property|unsupported_interpolation|backend_unavailable",
  "capability": "visual.image.interpolation.linear",
  "message": "Datoviz v0.4 retained scene API did not expose an image sampler/interpolation control in the probed facade.",
  "expected_v04_api": [
    "dvz_image",
    "dvz_visual_set_field",
    "dvz_visual_set_data",
    "dvz_panel_add_visual"
  ],
  "missing_symbols": [],
  "banned_v03_symbols_considered": false,
  "fallback_used": false,
  "adaptation": null
}
```

Rules:

- Never generate a Matplotlib image under a Datoviz filename.
- Never mark a Datoviz case “rendered” if capture failed.
- Never call a v0.3-style symbol “missing” unless the check is explicitly a banned-symbol check.
- Unsupported Datoviz cases should still appear in contact sheets as labeled placeholder tiles.

### Contact sheets

A contact sheet should contain:

```text
case_id: point/basic_ndc
family: point

┌──────────────────────────┬──────────────────────────┐
│ Matplotlib reference     │ Datoviz v0.4 candidate   │
│ rendered image           │ rendered/unsupported tile │
└──────────────────────────┴──────────────────────────┘

manual checklist:
- positions / coordinate-space mapping
- colors / alpha
- size or width units
- clipping
- antialiasing differences
- origin / colormap / interpolation for image
```

### Manual inspection notes

`manual_notes.yaml`:

```yaml
point/basic_ndc:
  status: unreviewed
  reviewer:
  reviewed_at:
  verdict:
  observations:
    placement:
    coordinate_space:
    colors_alpha:
    size_width_units:
    backend_differences:
    acceptable_differences:
    followup_issue:
```

Manual notes should be merged into `report.json` by the harness.

### Automatic vs manual checks

Automatic checks:

- protocol dataclass validation
- scene fixture serialization
- `.npz` sidecar creation
- Matplotlib render success
- Datoviz probe and capability matrix creation
- Datoviz render or structured unsupported report
- PNG existence, dimensions, and nonzero byte size
- report schema validation
- no banned v0.3 symbols in new Datoviz adapter code
- no import of legacy Datoviz renderer

Manual checks:

- semantic visual equivalence
- position and coordinate-space meaning
- size/diameter/stroke-width perception
- marker shape fidelity
- line cap and join appearance
- image origin and colormap/clim behavior
- alpha/source-over blending
- clipping
- acceptable backend differences

---

## 4. Visual Family Order

| Order | Family | Why now | Main protocol fields | Main backend risks | Deferred fields |
|---:|---|---|---|---|---|
| 1 | Point | Already exists; Datoviz v0.4 point path is the simplest actual API: `dvz_point` + `"position"`, `"color"`, `"diameter"`. | `positions`, `colors`, `sizes`, `coordinate_space` | Coordinate-space mapping; Matplotlib scatter `s` area vs protocol diameter; scalar-color scale optionality. | stroke/edge styling, scalar color scales, item state, picking |
| 2 | Marker | Natural extension with v0.4 retained `"symbol"`/`"shape"`, `"angle"`, style descriptor, fill/stroke. | `positions`, `shape`, `fill_colors`, `sizes`, `angle`, `stroke_color`, `stroke_width`, `coordinate_space` | Datoviz symbol vocabulary vs Matplotlib markers; stroke aspect semantics; per-item vs scalar shape. | custom symbols, SVG/SDF/MSDF markers, per-item stroke, mixed symbol-set encodings |
| 3 | Segment | Independent line geometry maps directly to `dvz_segment` and attributes `"position_start"`, `"position_end"`, `"color"`, `"stroke_width"`. | `starts`, `ends`, `colors`, `widths`, `cap`, `coordinate_space` | Cap style equivalence; zero-length behavior; draw order/alpha. | arrows, dashes, gradients, per-end cap, vector family |
| 4 | Path | Continuous line semantics maps to `dvz_path`, subpath lengths, caps, joins. | `positions`, `path_lengths`, `colors`, `widths`, `cap`, `join`, `miter_limit`, `coordinate_space` | Datoviz expects per-point color/width; Matplotlib path joins with per-path colors; closed subpaths are deferred in v0.4 docs. | closed paths, fills, holes, Beziers, dashes, per-vertex public API |
| 5 | Image hardening | Existing GSP image needs v1 semantics; Datoviz v0.4 uses sampled fields, scale/colormap, and image placement attributes. | `image`, `extent`, `origin`, `interpolation`, `colormap`, `clim`, `coordinate_space` | Image sampler/interpolation control may be missing; scalar/RGBA upload paths; origin via texcoords; DATA extent mapping. | tiled/virtual images, colorbars, NaN colors, log norms, volumes |
| 6 | Text/Glyph scoping only | v0.4 has text/glyph APIs, but fonts/atlases/anchors/DPI are a separate stage. | S024 proposal only | Font discovery, glyph atlas, shaping, DPI, anchors. | implementation deferred |
| 7 | Mesh later | Larger 3D/material/depth/lights scope. | later | topology, materials, normals, camera/depth. | implementation deferred |

---

## 5. Cross-Cutting Protocol Rules

### IDs

- Required for every protocol visual.
- Unique within a scene.
- Stable across serialization/replay.
- Recommended regex: `^[A-Za-z_][A-Za-z0-9_.:-]*$`.
- IDs are GSP semantic identifiers, not Datoviz `DvzId`s or backend handles.
- Query results must return the GSP visual `id`.

### Coordinate spaces

GSP keeps:

```python
class CoordinateSpace(str, Enum):
    NDC = "ndc"
    DATA = "data"
```

S023 Datoviz mapping rules:

- GSP `NDC` means coordinates already in normalized visual space `[-1, +1]`.
- Datoviz v0.4 has `DvzVisualAttachDesc.coord_space` values `DVZ_COORD_VIEW`, `DVZ_COORD_DATA`, and `DVZ_COORD_PANEL`.
- The adapter must pass an explicit `DvzVisualAttachDesc` to `dvz_panel_add_visual(...)`; do not rely on the default because v0.4 documents `coord_space=DATA` for NULL attach descriptors.
- Candidate mapping for GSP `NDC`: `coord_space=DVZ_COORD_VIEW` with a no-controller or fixed-controller QA setup. The probe mission must verify this against a known placement fixture. If local behavior shows `DVZ_COORD_PANEL` is required for exact fixed panel-normalized behavior, update the adapter note and capability matrix.
- Candidate mapping for GSP `DATA`: `coord_space=DVZ_COORD_DATA`, with `dvz_panel_set_domain(...)` and optionally `dvz_panel_set_view2d(...)`. DATA support should be capability-gated until a fixture proves Matplotlib and Datoviz agree semantically.

VisPy2/GSP producer defaults:

- Low-level `gsp.visuals.*(...)` constructors default to `NDC`.
- `Axes.*(...)` methods default to `DATA`.

### Transforms, views, and attachments

- Visual dataclasses describe semantic geometry and styling.
- View and panel transforms remain outside individual visual families.
- No arbitrary per-visual transform matrix is part of the S023 protocol.
- Datoviz `dvz_visual_set_transform(...)` exists, but S023 should not expose it as a GSP visual field.
- In-process arrays remain first-class attachments.
- JSON fixtures may reference `.npz` sidecars.

### Draw order

- Protocol draw order is scene visual list order.
- Later visuals draw over earlier visuals.
- Matplotlib renders in list order.
- Datoviz adapter should set `DvzVisualAttachDesc.z_layer` monotonically by visual index to avoid relying on same-layer insertion order.
- No protocol `z_index` field in S023 v1.

### Colors

- Protocol color semantic is straight RGBA.
- Accepted protocol color arrays:
  - `uint8` in `[0, 255]`;
  - `float32`/`float64` in `[0.0, 1.0]`.
- Datoviz v0.4 dense color attributes generally expect `DvzColor`/RGBA8 for early visuals.
- The Datoviz adapter should normalize GSP float colors to RGBA8 unless the visual explicitly uses a scalar color scale path.
- Matplotlib may use normalized float RGBA internally.

### Alpha/compositing

- Protocol alpha is straight alpha, source-over, in draw order.
- Datoviz v0.4 adapter should set `DVZ_ALPHA_BLENDED` for 2D QA visuals when any alpha is below 255, and disable depth testing for 2D visual QA cases unless the case explicitly tests depth.
- Backend premultiplication is an implementation detail.

### Dtype/shape validation

Common geometry rules:

- Positions must be `float32` or `float64`.
- Position shape is `(N, 2)` or `(N, 3)` at protocol level.
- Datoviz adapter expands `(N, 2)` to `(N, 3)` with `z=0`.
- Coordinates must be finite.
- Widths/sizes must be finite and non-negative.
- Color item counts must match geometry item counts unless a scalar/per-visual field is explicitly specified.
- Empty visuals may be valid if shape-consistent but should not be used in S023 QA examples.

### Scalar vs per-item properties

S023 protocol should be explicit:

- Point:
  - colors are per point;
  - sizes are scalar or per point.
- Marker:
  - fill colors are per marker;
  - shape is scalar per visual in v1, but adapter may repeat it as per-item `"symbol"` for Datoviz;
  - angle is scalar or per marker;
  - stroke color/width are scalar per visual in v1.
- Segment:
  - colors are per segment;
  - widths are scalar or per segment;
  - cap is scalar per visual.
- Path:
  - colors are scalar or per path in the GSP protocol;
  - widths are scalar or per path in the GSP protocol;
  - Datoviz adapter expands per-path values to per-point arrays because v0.4’s path attributes are per point.
- Image:
  - one image visual has one raster in v1.

### Units

Protocol semantic units:

- Point `sizes`: rendered diameter in screen pixels.
- Marker `sizes`: rendered diameter in screen pixels.
- Segment/Path `widths`: stroke width in screen pixels.
- Marker/Point stroke widths: screen pixels.

Matplotlib reference conversion:

- Convert pixels to typographic points using figure DPI.
- For scatter-like area parameters, convert protocol diameter to Matplotlib area.
- Do not let Matplotlib’s `s` area semantics leak into the protocol.

Datoviz v0.4 alignment:

- Point and Marker use `"diameter"` in pixels.
- Segment and Path use `"stroke_width"` in pixels.

### Clipping

- Default: visuals are clipped to their panel/view.
- No per-visual `clip` field in S023.
- Custom clip paths and clip disabling are deferred.

### Antialiasing

- Renderer-dependent in S023.
- No protocol `antialias` field.
- Manual QA records antialiasing differences as acceptable or follow-up-worthy.

### Picking/query metadata

S023 defines item identity semantics even if GPU picking is not fully implemented:

- Point item index: point index.
- Marker item index: marker index.
- Segment item index: segment index.
- Path item index: path/subpath index; optional vertex index when available.
- Image item index: pixel row/column or sample/texel.

Query result shape should include:

```text
visual_id
family
item_index or path_index/pixel_index
coordinate_space
backend
capability_status
```

Datoviz v0.4 exposes richer `DvzQueryResult` concepts; S023 should map them into GSP query results but not expose raw Datoviz fields directly.

### Capability/adaptation diagnostics

Capability vocabulary examples:

```text
visual.point
visual.point.datoviz_v04.constructor
visual.point.datoviz_v04.attr.position
visual.point.datoviz_v04.attr.color_rgba8
visual.point.datoviz_v04.attr.diameter
visual.marker.datoviz_v04.attr.symbol
visual.segment.datoviz_v04.set_caps
visual.path.datoviz_v04.set_subpaths
visual.path.datoviz_v04.set_join
visual.image.datoviz_v04.sampled_field
visual.image.datoviz_v04.texture_rgba8
visual.capture.offscreen_png
coordinate_space.ndc.datoviz_v04
coordinate_space.data.datoviz_v04
```

Unsupported diagnostics must specify the exact capability, expected v0.4 call pattern, and whether a fallback or adaptation was used.

### Serialization vs in-process arrays

- Local desktop rendering must support direct NumPy arrays.
- JSON/base64 is allowed for fixtures, debugging, replay, and transport.
- QA fixtures should use JSON plus `.npz` sidecars for nontrivial arrays.
- Large arrays must not be embedded in JSON.

---

## 6. Early Family Contracts

### 6.1 Point

#### Semantic purpose

Many simple circular point sprites/dots for scatter-like data where marker shape and stroke are not semantically important.

#### Minimal v1 protocol fields

```python
@dataclass(frozen=True, slots=True)
class PointVisual:
    id: str
    positions: FloatArray             # shape (N, 2) or (N, 3)
    colors: ColorArray                # shape (N, 4), RGBA
    sizes: FloatArray | float         # scalar or shape (N,), diameter_px
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
```

#### Validation

- `positions.shape` is `(N, 2)` or `(N, 3)`.
- `positions.dtype` is `float32` or `float64`.
- `positions` finite.
- `colors.shape == (N, 4)`.
- `colors.dtype` is `uint8`, `float32`, or `float64`.
- Float colors are in `[0, 1]`.
- `sizes` scalar or shape `(N,)`.
- `sizes` finite and `>= 0`.

#### VisPy2/GSP producer API

```python
Axes.scatter(
    x,
    y=None,
    *,
    color=None,
    c=None,
    size=None,
    s=None,
    coordinate_space=None,
    id=None,
) -> PointVisual

gsp.visuals.point(
    id,
    positions,
    colors,
    sizes,
    coordinate_space=CoordinateSpace.NDC,
) -> PointVisual
```

Producer rules:

- `Axes.scatter` defaults to DATA.
- Low-level `gsp.visuals.point` defaults to NDC.
- `size`/`s` mean protocol diameter in pixels.
- Shape/stroke arguments route to Marker or raise a clear error.

#### Matplotlib reference mapping

- Use `axes.scatter`.
- Convert diameter pixels to points, then to scatter area.
- Use circular marker with no stroke.
- Use normalized RGBA colors.
- Respect draw order and clipping.

#### Datoviz v0.4 mapping

Actual v0.4 retained-scene pattern:

```text
visual = dvz_point(scene, flags)
dvz_visual_set_data_many(visual, [
  ("position", vec3 positions, N),
  ("color", rgba8 colors, N),
  ("diameter", float diameters_px, N),
])
dvz_point_style_desc()
dvz_point_set_style(visual, &style)      # optional; filled/no-stroke by default
dvz_visual_set_alpha_mode(visual, DVZ_ALPHA_BLENDED)  # when needed
dvz_visual_set_depth_test(visual, false)               # 2D QA default
dvz_panel_add_visual(panel, visual, explicit_attach_desc)
```

Python array-aware facade pattern may omit the explicit C `item_count`; raw ctypes requires it.

Capability gates:

- `dvz_point`
- `dvz_visual_set_data` or `dvz_visual_set_data_many`
- `dvz_panel_add_visual`
- `dvz_point_style_desc` and `dvz_point_set_style` only if stroke tests are enabled
- `datoviz.capture` or equivalent offscreen path for PNG output

Initial Datoviz support:

- Required: RGBA8 point color and pixel diameter.
- Optional: scalar color scale via `dvz_visual_set_attr_format(point, "color", DVZ_VISUAL_ATTR_FORMAT_SCALAR_F32)` + `dvz_visual_set_scale(point, "color", scale)`.
- Stroke/edge point style deferred or capability-gated.

#### Manual QA cases

```text
point/basic_ndc
point/diameter_ramp_ndc
point/rgba_uint8_and_float_equivalence
point/alpha_over_background_ndc
point/data_space_matplotlib_reference
```

#### Automatic tests

- validation accepts correct shapes/dtypes;
- validation rejects bad sizes/colors;
- Matplotlib emits nonempty PNG;
- Datoviz emits PNG or structured unsupported;
- Datoviz report confirms no `_alloc` symbol expectation.

#### Deferred

- per-point metadata;
- GPU picking implementation;
- scalar color scale as public GSP point color field;
- point stroke/halo;
- density aggregation;
- 3D camera semantics.

---

### 6.2 Marker

#### Semantic purpose

Screen-space shaped symbols with fill and optional stroke. Marker is for shape/stroke semantics; Point remains the minimal fast circular dot family.

#### Minimal v1 protocol fields

```python
class MarkerShape(str, Enum):
    DISC = "disc"          # Matplotlib circle; Datoviz DVZ_SYMBOL_DISC
    SQUARE = "square"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    CROSS = "cross"
    RING = "ring"
    TARGET = "target"

@dataclass(frozen=True, slots=True)
class MarkerVisual:
    id: str
    positions: FloatArray              # shape (N, 2) or (N, 3)
    shape: MarkerShape                 # scalar per visual in v1
    fill_colors: ColorArray            # shape (N, 4)
    sizes: FloatArray | float          # scalar or shape (N,), diameter_px
    angle: FloatArray | float = 0.0    # scalar or shape (N,), radians
    stroke_color: Color4 | None = None # scalar RGBA
    stroke_width: float = 0.0          # px
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
```

#### Validation

- Same position/color rules as Point.
- `shape` must be in the enum.
- `fill_colors.shape == (N, 4)`.
- `sizes` scalar or `(N,)`, finite, non-negative.
- `angle` scalar or `(N,)`, finite.
- `stroke_color is None` or RGBA.
- `stroke_width` finite and non-negative.
- Shape is scalar per visual in v1; producers may split grouped shapes into multiple visuals.

#### VisPy2/GSP producer API

```python
Axes.markers(
    x,
    y=None,
    *,
    marker="disc",
    fill_color=None,
    color=None,
    edge_color=None,
    stroke_color=None,
    stroke_width=0,
    size=8,
    angle=0,
    coordinate_space=None,
    id=None,
) -> MarkerVisual

gsp.visuals.marker(
    id,
    positions,
    shape,
    fill_colors,
    sizes,
    *,
    angle=0,
    stroke_color=None,
    stroke_width=0,
    coordinate_space=CoordinateSpace.NDC,
) -> MarkerVisual
```

Producer rules:

- `color` aliases `fill_color`.
- `edge_color` aliases `stroke_color`.
- `Axes.scatter(..., marker=...)` may delegate to `Axes.markers(...)`, but the protocol family should be Marker.
- Unsupported Matplotlib-only markers such as `"+"` or `"x"` should not silently become Datoviz shapes; they require a documented capability decision.

#### Matplotlib reference mapping

Suggested mapping:

```text
disc      -> "o"
square    -> "s"
triangle  -> "^"
diamond   -> "D"
cross     -> "x" or "X" depending desired filled/stroke semantics
ring      -> "o" with facecolors='none'
target    -> custom reference marker or two-pass circle+center
```

- Convert diameter pixels to scatter area.
- Convert stroke width pixels to points.
- Draw target/ring as a reference composition if needed.
- Clip to panel.

#### Datoviz v0.4 mapping

Actual v0.4 retained-scene pattern:

```text
visual = dvz_marker(scene, flags)
dvz_visual_set_data_many(visual, [
  ("position", vec3 positions, N),
  ("color", rgba8 fill_colors, N),
  ("diameter", float diameters_px, N),
  ("angle", float radians, N),
  ("symbol", uint32 symbol_ids, N),     # example uses "symbol"
])
style = dvz_marker_style()
style.aspect = DVZ_SHAPE_ASPECT_FILLED | STROKE | OUTLINE
style.edge_color = rgba8
style.stroke_width = px
dvz_marker_set_style(visual, &style)
dvz_panel_add_visual(panel, visual, explicit_attach_desc)
```

Header notes:

- Marker accepts `"shape"`/`"symbol"` as built-in symbol IDs.
- `dvz_marker_set_symbol(visual, builtin)` can set every existing marker item after dense item count exists.
- `dvz_marker_set_symbols(visual, symbol_set)` exists for reusable symbol sets, but custom symbol sets are not part of S023 v1.

Capability gates:

- `dvz_marker`
- `dvz_marker_style`
- `dvz_marker_set_style`
- `dvz_visual_set_data_many`
- supported `DvzSymbolBuiltin` values

Initial Datoviz mapping:

```text
GSP DISC      -> DVZ_SYMBOL_DISC
GSP SQUARE    -> DVZ_SYMBOL_SQUARE
GSP TRIANGLE  -> DVZ_SYMBOL_TRIANGLE
GSP DIAMOND   -> DVZ_SYMBOL_DIAMOND
GSP CROSS     -> DVZ_SYMBOL_CROSS
GSP RING      -> DVZ_SYMBOL_RING
GSP TARGET    -> DVZ_SYMBOL_TARGET
```

#### Manual QA cases

```text
marker/disc_fill_stroke_ndc
marker/supported_symbols_ndc
marker/diameter_ramp_ndc
marker/angle_ndc
marker/transparent_fill_outline_ndc
marker/data_space_matplotlib_reference
```

#### Automatic tests

- enum validation;
- scalar shape expansion;
- angle scalar/per-item handling;
- Matplotlib marker mapping smoke tests;
- Datoviz symbol capability report;
- style helper unavailable -> structured unsupported.

#### Deferred

- custom symbols;
- SVG/SDF/MSDF user markers;
- per-item stroke;
- mixed symbol sets beyond built-ins;
- hatching/patterns;
- marker aspect correction policy.

---

### 6.3 Segment

#### Semantic purpose

Independent straight line segments for overlays, vectors, graph edges, rulers, guides, error bars, and annotations.

#### Minimal v1 protocol fields

```python
class StrokeCap(str, Enum):
    BUTT = "butt"
    ROUND = "round"
    SQUARE = "square"

@dataclass(frozen=True, slots=True)
class SegmentVisual:
    id: str
    starts: FloatArray              # shape (M, 2) or (M, 3)
    ends: FloatArray                # shape (M, 2) or (M, 3)
    colors: ColorArray              # shape (M, 4)
    widths: FloatArray | float      # scalar or shape (M,), px
    cap: StrokeCap = StrokeCap.BUTT
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
```

#### Validation

- `starts.shape == ends.shape`.
- Shape is `(M, 2)` or `(M, 3)`.
- Coordinates finite.
- `colors.shape == (M, 4)`.
- `widths` scalar or `(M,)`, finite, non-negative.
- `cap` in enum.
- Zero-length segments are rejected in v1 unless a future ADR defines cap-only dot behavior.

#### VisPy2/GSP producer API

```python
Axes.segment(
    x0,
    y0,
    x1,
    y1,
    *,
    color=None,
    linewidth=1,
    cap="butt",
    coordinate_space=None,
    id=None,
) -> SegmentVisual

Axes.segments(
    starts,
    ends,
    *,
    color=None,
    linewidth=1,
    cap="butt",
    coordinate_space=None,
    id=None,
) -> SegmentVisual

gsp.visuals.segment(
    id,
    starts,
    ends,
    colors,
    widths,
    *,
    cap="butt",
    coordinate_space=CoordinateSpace.NDC,
) -> SegmentVisual
```

#### Matplotlib reference mapping

- Use `matplotlib.collections.LineCollection`.
- Convert protocol pixel widths to Matplotlib points.
- Use independent segment geometry.
- Apply cap style where supported; if collection cap style is unavailable, emit a renderer warning for non-default cap tests.
- Clip to panel.

#### Datoviz v0.4 mapping

Actual retained-scene pattern:

```text
visual = dvz_segment(scene, flags)
dvz_visual_set_data_many(visual, [
  ("position_start", vec3 starts, M),
  ("position_end", vec3 ends, M),
  ("color", rgba8 colors, M),
  ("stroke_width", float widths_px, M),
])
dvz_segment_set_caps(visual, cap, cap)
dvz_panel_add_visual(panel, visual, explicit_attach_desc)
```

Cap mapping:

```text
GSP BUTT   -> DVZ_SEGMENT_CAP_BUTT
GSP ROUND  -> DVZ_SEGMENT_CAP_ROUND
GSP SQUARE -> DVZ_SEGMENT_CAP_SQUARE
```

Datoviz also exposes `NONE`, `TRIANGLE_IN`, and `TRIANGLE_OUT`; these are deferred for GSP Segment v1.

#### Manual QA cases

```text
segment/basic_ndc
segment/width_ramp_ndc
segment/cap_styles_ndc
segment/alpha_over_image_ndc
segment/data_space_matplotlib_reference
```

#### Automatic tests

- starts/ends shape validation;
- zero-length rejection;
- scalar/per-item widths;
- Matplotlib smoke render;
- Datoviz render or structured unsupported;
- cap capability mapping.

#### Deferred

- arrows;
- dashes;
- gradients;
- per-end cap in public GSP API;
- endpoint offsets;
- vector visual family;
- picking tolerance.

---

### 6.4 Path

#### Semantic purpose

Continuous polylines and multi-subpath line collections where joins/caps matter. Path is for connected line geometry, not independent segments.

#### Minimal v1 protocol fields

```python
class StrokeJoin(str, Enum):
    MITER = "miter"
    ROUND = "round"
    BEVEL = "bevel"

@dataclass(frozen=True, slots=True)
class PathVisual:
    id: str
    positions: FloatArray              # shape (N, 2) or (N, 3)
    path_lengths: IntArray             # shape (P,), positive, sum == N
    colors: ColorArray | Color4        # scalar or shape (P, 4), per path
    widths: FloatArray | float         # scalar or shape (P,), px
    cap: StrokeCap = StrokeCap.BUTT
    join: StrokeJoin = StrokeJoin.MITER
    miter_limit: float = 4.0
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
```

Important v1 decision: **closed paths are deferred.** Datoviz v0.4 path docs say closed subpaths are deferred, and fills/holes belong to a later Polygon/PathFill contract. A producer may create an explicitly closed polyline by duplicating the first vertex, but there is no `closed` protocol field in S023.

#### Validation

- `positions.shape` is `(N, 2)` or `(N, 3)`.
- `positions` finite.
- `path_lengths.shape == (P,)`.
- `path_lengths` positive integers.
- `sum(path_lengths) == N`.
- Each subpath length `>= 2`.
- `colors` scalar RGBA or `(P, 4)`.
- `widths` scalar or `(P,)`, finite, non-negative.
- `cap`, `join` in enum.
- `miter_limit` finite and positive.

#### VisPy2/GSP producer API

```python
Axes.plot(
    x,
    y=None,
    *,
    color=None,
    linewidth=1,
    cap="butt",
    join="miter",
    miter_limit=4.0,
    coordinate_space=None,
    id=None,
) -> PathVisual

Axes.path(
    vertices,
    *,
    path_lengths=None,
    color=None,
    linewidth=1,
    cap="butt",
    join="miter",
    miter_limit=4.0,
    coordinate_space=None,
    id=None,
) -> PathVisual

Axes.paths(
    list_of_vertices,
    *,
    color=None,
    linewidth=1,
    cap="butt",
    join="miter",
    miter_limit=4.0,
    coordinate_space=None,
    id=None,
) -> PathVisual
```

#### Matplotlib reference mapping

- Use one Line2D/path patch per subpath where cap/join fidelity matters.
- Convert widths from pixels to points.
- Per-path colors/widths map naturally.
- No fill.
- Clip to panel.

#### Datoviz v0.4 mapping

Actual retained-scene pattern:

```text
visual = dvz_path(scene, flags)
dvz_visual_set_data_many(visual, [
  ("position", vec3 positions, N),
  ("color", rgba8 per_point_colors, N),
  ("stroke_width", float per_point_widths_px, N),  # optional but required for screen-space stroke
])
dvz_path_set_subpaths(visual, P, path_lengths)
dvz_path_set_caps(visual, start_cap, end_cap)
dvz_path_set_join(visual, join, miter_limit)
dvz_panel_add_visual(panel, visual, explicit_attach_desc)
```

Adapter rule:

- Expand GSP per-path colors/widths to Datoviz per-point arrays using `path_lengths`.
- Always upload `"stroke_width"` in S023 so Datoviz uses the screen-space stroke pipeline, not the primitive line-strip fallback.
- If a user explicitly duplicates vertices to close a path, treat it as an ordinary open subpath with repeated endpoints.
- Do not implement a `closed` flag in S023.

Join mapping:

```text
GSP MITER -> DVZ_PATH_JOIN_MITER
GSP ROUND -> DVZ_PATH_JOIN_ROUND
GSP BEVEL -> DVZ_PATH_JOIN_BEVEL
```

Cap mapping uses `DvzSegmentCap` as for Segment.

#### Manual QA cases

```text
path/single_polyline_ndc
path/multiple_subpaths_ndc
path/widths_per_path_ndc
path/join_styles_ndc
path/cap_styles_ndc
path/data_space_matplotlib_reference
```

#### Automatic tests

- path length validation;
- per-path expansion to per-point arrays;
- Matplotlib smoke render;
- Datoviz render or structured unsupported;
- cap/join capability mapping;
- no `closed` field accepted in v1 dataclass.

#### Deferred

- closed subpaths;
- polygon fills;
- holes;
- Beziers;
- dashes;
- per-vertex public color/width;
- miter limit tuning beyond scalar field;
- path simplification;
- hit testing.

---

### 6.5 Image

#### Semantic purpose

Raster images placed in a panel extent. Supports scalar scientific images and RGB/RGBA images with explicit origin, extent, colormap, and clim semantics.

#### Minimal v1 protocol fields

```python
class ImageInterpolation(str, Enum):
    NEAREST = "nearest"
    LINEAR = "linear"

class ImageOrigin(str, Enum):
    UPPER = "upper"
    LOWER = "lower"

@dataclass(frozen=True, slots=True)
class ImageVisual:
    id: str
    image: ImageArray                   # (H, W), (H, W, 3), or (H, W, 4)
    extent: tuple[float, float, float, float]  # x0, x1, y0, y1
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
    interpolation: ImageInterpolation = ImageInterpolation.NEAREST
    origin: ImageOrigin = ImageOrigin.UPPER
    colormap: str | None = None
    clim: tuple[float, float] | None = None
```

#### Validation

- `image.ndim in {2, 3}`.
- If 3D, channels are 3 or 4.
- `H > 0`, `W > 0`.
- RGB/RGBA image:
  - dtype `uint8`, `float32`, or `float64`;
  - float values in `[0, 1]`;
  - `colormap is None`;
  - `clim is None`.
- Scalar image:
  - dtype `uint8`, `float32`, or `float64`;
  - finite values;
  - fixtures must set explicit `clim`;
  - default `colormap="gray"` if omitted by the high-level producer.
- `extent` finite with nonzero width/height.
- `origin` and `interpolation` in enum.

#### VisPy2/GSP producer API

```python
Axes.imshow(
    image,
    *,
    extent=None,
    origin="upper",
    interpolation="nearest",
    cmap="gray",
    clim=None,
    coordinate_space=None,
    id=None,
) -> ImageVisual

gsp.visuals.image(
    id,
    image,
    extent,
    *,
    coordinate_space=CoordinateSpace.NDC,
    interpolation="nearest",
    origin="upper",
    colormap=None,
    clim=None,
) -> ImageVisual
```

Producer rules:

- `Axes.imshow` defaults to DATA.
- Low-level image defaults to NDC.
- Scalar fixtures must store resolved `colormap` and `clim` in the protocol scene.
- RGB/RGBA images bypass colormap.

#### Matplotlib reference mapping

- Use `axes.imshow`.
- Map `nearest -> interpolation="nearest"`.
- Map `linear -> interpolation="bilinear"`.
- Pass `origin`.
- Pass `extent`.
- For scalar image, pass `cmap`, `vmin`, `vmax`.
- For RGB/RGBA, pass array directly.
- Clip to panel.

#### Datoviz v0.4 mapping

Preferred actual retained-scene path:

```text
visual = dvz_image(scene, flags)

# Placement option A, used by current C example:
dvz_visual_set_data(visual, "position", vec3 corner_positions, 4)
dvz_visual_set_data(visual, "texcoords", vec2 texcoords, 4)

# Sampled field:
field = dvz_sampled_field(scene, &DvzSampledFieldDesc{...})
dvz_sampled_field_set_data(field, &DvzFieldDataView{...})
dvz_visual_set_field(visual, "field", field)

# Scalar image:
scale = dvz_scale(scene, &DvzScaleDesc{kind=DVZ_SCALE_CONTINUOUS})
dvz_scale_set_domain(scale, clim_min, clim_max)
colormap = dvz_colormap_builtin(scene, builtin)
dvz_scale_set_colormap(scale, colormap)
dvz_visual_set_scale(visual, "color", scale)

dvz_panel_add_visual(panel, visual, explicit_attach_desc)
```

Transitional convenience wrappers exist:

```text
dvz_visual_set_texture(visual, rgba8, width, height)
dvz_visual_set_texture_f32(visual, values, width, height)
```

But new S023 code should prefer `dvz_sampled_field(...)` + `dvz_visual_set_field(...)` when the facade exposes it.

Placement details:

- For NDC extent `(x0, x1, y0, y1)`, build four corner positions.
- Implement `origin` by texcoord mapping, not by mutating protocol data.
- For `origin="upper"`, map the first image row to the visual top edge.
- For `origin="lower"`, flip the V texcoords.

Interpolation:

- The audited scene header did not show an image-specific sampler/interpolation setter.
- S023 Datoviz v0.4 support should initially require `interpolation="nearest"` only if the local renderer’s default is verified as nearest, or mark interpolation control as unsupported in the report.
- `linear` is capability-gated until a real v0.4 sampler API is found.

Scalar image:

- Prefer a scalar `DvzSampledField` with `DVZ_FIELD_FORMAT_R32_FLOAT` and `DVZ_FIELD_SEMANTIC_SCALAR`.
- Bind a continuous scale on `"color"`.
- If the Python facade lacks sampled-field functions, CPU-map scalar to RGBA8 as an explicit adaptation: `adaptation="scalar_colormap_to_rgba8"`.

RGB/RGBA image:

- Prefer RGBA8 sampled field with `DVZ_FIELD_FORMAT_RGBA8_UNORM` and `DVZ_FIELD_SEMANTIC_COLOR`.
- RGB arrays should be expanded to RGBA8 with alpha=255 by the adapter.

#### Manual QA cases

```text
image/checker_nearest_ndc
image/origin_upper_lower_ndc
image/scalar_colormap_clim_ndc
image/rgba_alpha_overlay_ndc
image/linear_interpolation_matplotlib_reference
image/data_space_matplotlib_reference
```

#### Automatic tests

- scalar/RGB/RGBA validation;
- invalid shape rejection;
- explicit clim validation for scalar QA fixtures;
- Matplotlib render;
- Datoviz field/texture capability report;
- Datoviz unsupported report for interpolation when no sampler control is probed.

#### Deferred

- tiled images;
- virtual/out-of-core images;
- colorbars as protocol visual family;
- NaN/under/over colors;
- log/symlog normalization;
- advanced interpolation kernels;
- image affine transforms;
- volumes/slices.

---

### 6.6 Text/Glyph deferral to S024

Do not implement Text/Glyph in S023.

Reason:

- Datoviz v0.4 exposes text and glyph concepts, but the correct protocol contract must handle font discovery, glyph atlases, DPI, anchors, baseline, shaping, multiline text, fallback fonts, and backend-specific limitations.
- Matplotlib and Datoviz text will not be semantically comparable without a dedicated font/anchor ADR.
- S023 should only inventory v0.4 text/glyph APIs and legacy examples for S024 planning.

---

## 7. Datoviz v0.4 Integration Plan

### Use `../datoviz/`

Agents should inspect the sibling `../datoviz/` repository, expected to be on or compatible with `v0.4-dev`, before implementation. The implementation source of truth is the local checkout plus the installed package, not memory of Datoviz v0.3.

Required local checks:

1. Confirm `../datoviz/` exists.
2. Record its git revision and branch.
3. Confirm `include/datoviz/scene.h`, `include/datoviz/scene/types.h`, and `include/datoviz/scene/enums.h` expose the expected v0.4 API.
4. Inspect `examples/c/visuals/{point,marker,segment,path,image}.c`.
5. Inspect generated Python modules:
   - `datoviz/_array_facade.py`
   - `datoviz/_ctypes.py`
   - `datoviz/raw.py`
6. Compare installed `import datoviz as dvz` with local source.
7. Emit `capability_matrix.json`.

### Probe top-level Python facade and raw ctypes

Probe three layers:

```python
import datoviz as dvz
import datoviz.raw as raw
```

Probe categories:

```text
package:
  datoviz.__file__
  datoviz.__version__ if present
  datoviz.run
  datoviz.capture

scene:
  dvz_scene
  dvz_figure
  dvz_panel_full
  dvz_panel_add_visual
  dvz_visual_attach_desc

visual constructors:
  dvz_point
  dvz_marker
  dvz_segment
  dvz_path
  dvz_image

generic visual data:
  dvz_visual_set_data
  dvz_visual_set_data_many
  dvz_visual_set_data_range
  dvz_visual_set_attr_format
  dvz_visual_set_scale
  dvz_visual_set_field
  dvz_visual_set_texture
  dvz_visual_set_texture_f32

style helpers:
  dvz_point_style_desc
  dvz_point_set_style
  dvz_marker_style
  dvz_marker_set_style
  dvz_marker_set_symbol
  dvz_marker_set_symbols
  dvz_segment_set_caps
  dvz_path_set_caps
  dvz_path_set_join
  dvz_path_set_subpaths

field/scale:
  dvz_sampled_field
  dvz_sampled_field_desc
  dvz_sampled_field_set_data
  dvz_field_data_view
  dvz_scale
  dvz_scale_desc
  dvz_scale_set_domain
  dvz_colormap_builtin
  dvz_colormap_custom
  dvz_scale_set_colormap
```

Banned v0.3 drift check:

```text
dvz_point_alloc
dvz_marker_alloc
dvz_segment_alloc
dvz_path_alloc
dvz_image_alloc
dvz_point_position
dvz_point_color
dvz_point_size
dvz_marker_position
dvz_marker_color
dvz_segment_position
dvz_segment_linewidth
dvz_path_position
dvz_path_color
```

These banned names should **not** be required by S023. If they appear in local bindings for compatibility reasons, the S023 adapter still must not use them.

### Handle incomplete bindings without blocking Matplotlib

- Matplotlib missions can proceed independently.
- Datoviz adapter must still be probed and attempted.
- Missing facade symbols produce `unsupported` reports.
- Raw ctypes may be used as a fallback only if the mission explicitly supports it and records `datoviz_backend="raw"`.
- C example parity can be used to verify semantics even if Python facade generation lags.
- No silent fallback to Matplotlib.

### Minimum usable Datoviz v0.4 visual QA path

Minimum path for a green Datoviz artifact:

1. `dvz_scene()`
2. `dvz_figure(scene, width, height, flags)`
3. `dvz_panel_full(figure)`
4. `dvz_<family>(scene, flags)`
5. `dvz_visual_set_data*`
6. style helpers if needed
7. explicit `DvzVisualAttachDesc`
8. `dvz_panel_add_visual(panel, visual, &attach_desc)`
9. offscreen capture via `datoviz.capture(...)` or raw app/view/capture calls
10. PNG written and nonempty

### Avoid legacy `gsp_datoviz.renderer`

Rules:

- New adapter path lives under `gsp/backends/datoviz_v04/`.
- Add a test that imports the new adapter and asserts it does not import legacy renderer modules.
- Legacy GSP examples may be used only to understand desired visual coverage and appearance.
- Legacy object graph must not be accepted as protocol input for S023.

### Capability diagnostics example

```json
{
  "backend": "datoviz-v04",
  "family": "path",
  "visual_id": "path_join_styles",
  "status": "unsupported",
  "reason_code": "missing_symbol",
  "capability": "visual.path.datoviz_v04.set_join",
  "expected_v04_symbols": [
    "dvz_path",
    "dvz_visual_set_data_many",
    "dvz_path_set_join",
    "dvz_panel_add_visual"
  ],
  "missing_symbols": ["dvz_path_set_join"],
  "banned_v03_symbols_considered": false,
  "message": "The installed Datoviz v0.4 Python facade does not expose dvz_path_set_join. The C header in ../datoviz should be checked and bindings regenerated.",
  "fallback_used": false,
  "adaptation": null
}
```

---

## 8. Mission Breakdown

| Mission | Title | Goal | Deliverables | Acceptance | Stop Conditions |
|---|---|---|---|---|---|
| M064 | Datoviz v0.4 API audit and probe | Replace v0.3-drift assumptions with a generated actual-v0.4 capability matrix. | `gsp/qa/visual/datoviz_probe.py`; `datoviz_v04_probe/probe_report.json`; facade/raw symbol matrix; banned-symbol check; documentation of retained-scene pattern; source references to local `../datoviz/` files. | Probe records installed package path, local source path/revision, facade/raw availability, capture availability, required v0.4 symbols, missing symbols, and banned v0.3 names. No new mission text expects `_alloc` visual functions. | Stop if a worker attempts to implement against `dvz_*_alloc` or v0.3 family setter names. Do not stop Matplotlib work if Datoviz facade is incomplete; report unsupported. |
| M065 | Visual QA harness foundation | Build repeatable artifact production and manual review workflow around Point/Image smoke cases. | CLI; case registry; report schema; artifact writer; contact sheets; manual notes template; Matplotlib backend runner; Datoviz backend runner using M064 probe; cases `point/basic_ndc`, `point/diameter_ramp_ndc`, `image/checker_nearest_ndc`, `overlay/point_over_image_ndc`. | Running the S023 suite produces `report.json`, scene fixtures, `.npz` arrays, Matplotlib PNGs, Datoviz PNGs or unsupported JSON, contact sheets, and manual notes. Schema validation passes. | Stop if Matplotlib artifacts are missing or report schema is unstable. Datoviz unsupported is acceptable only with structured diagnostics. |
| M066 | PointVisual v1 + Datoviz v0.4 retained point path | Freeze point semantics and prove the simplest Datoviz path. | Point spec; size-unit ADR; Matplotlib px-diameter conversion; Datoviz adapter for `dvz_point` + `"position"`/`"color"`/`"diameter"`; explicit attach descriptor; tests; QA cases. | Point cases render in Matplotlib. Datoviz Point NDC renders or reports precise facade/capture blocker. No v0.3 symbols appear in adapter. | Stop if `sizes` semantics are not decided as diameter pixels. Stop if coordinate-space fixture shows Datoviz mapping is ambiguous without documented resolution. |
| M067 | MarkerVisual v1 | Add marker contract, producer API, Matplotlib reference, and Datoviz `dvz_marker` adapter. | `MarkerVisual`; `MarkerShape` enum; validation; `Axes.markers`; Matplotlib renderer; Datoviz mapping to `"symbol"`/`"diameter"`/`"angle"` and style descriptor; QA cases. | Supported symbols render in Matplotlib. Datoviz renders or reports missing `dvz_marker`/style/symbol capabilities. Stroke/fill cases produce contact sheets. | Stop if shape vocabulary expands beyond v0.4-supported built-ins without capability gates. Do not add custom symbols. |
| M068 | SegmentVisual v1 | Add independent line segment contract and backend mappings. | `SegmentVisual`; `StrokeCap`; validation; `Axes.segment(s)`; Matplotlib LineCollection mapping; Datoviz `dvz_segment` adapter; QA cases. | Segment width/cap/alpha cases render in Matplotlib and Datoviz or produce structured unsupported. | Stop if width units diverge from Path/Marker/Point px semantics. Do not add arrows/dashes. |
| M069 | PathVisual v1 | Add continuous open polyline/subpath contract. | `PathVisual`; `StrokeJoin`; validation; `Axes.plot/path/paths`; Matplotlib mapping; Datoviz `dvz_path` adapter with per-path-to-per-point expansion; QA cases. | Multiple-subpath, cap, join, width cases render in Matplotlib. Datoviz renders or reports missing subpath/join/cap helpers. | Stop if closed/fill/Bezier/dash requirements enter scope. |
| M070 | ImageVisual v1 hardening | Stabilize image dtype/origin/extent/interpolation/colormap/clim behavior and Datoviz sampled-field path. | Image spec update; colormap/clim ADR; validation; Matplotlib reference; Datoviz sampled-field/texture adapter; image QA cases. | Checker/origin/scalar/RGBA cases render in Matplotlib. Datoviz nearest/sampled-field cases render or report field/scale/interpolation limitations. | Stop if image work expands into tiled/virtual images, colorbars, volumes, or advanced normalization. |
| M071 | S023 gallery and manual review pack | Produce examples and final review artifacts. | `examples/vispy2_protocol_marker.py`; `segment.py`; `path.py`; updated scatter/imshow examples; combined gallery; final contact sheet; manual notes. | A human can run one command and inspect all S023 cases. Examples use formal protocol scenes. | Stop if examples call backend APIs directly instead of producing GSP scenes. |
| M072 | S023 closure docs/spec index | Convert decisions into accepted docs/tasks and prepare S024. | ADRs accepted; `SPEC_INDEX.md` updated; `LEGACY_MAP.md` updated; `.agent/decisions` summary; S024 Text/Glyph scoping note. | Closure checklist passes. All implemented fields are documented. Datoviz limitations have follow-up tasks. | Stop if any behavior exists only in code and not in spec/ADR. |

### First three missions — additional implementation notes

#### M064 details

The probe must attempt both:

```python
import datoviz as dvz
import datoviz.raw as raw
```

It must record:

- import status and exception traceback;
- package path;
- whether generated `_array_facade.py` is present;
- whether generated `_ctypes.py` is present;
- source repo path/revision;
- exact callable names;
- enum names needed for caps/joins/symbols;
- whether `datoviz.capture` exists;
- whether a minimal Point scene can be constructed without running capture.

The probe should produce a summary table:

```text
capability                                      status
datoviz.facade.import                           found
datoviz.raw.import                              found
scene.create.dvz_scene                          found
visual.point.constructor.dvz_point              found
visual.point.attr.position                      inferred_from_header_and_probe
visual.path.style.dvz_path_set_join             found
visual.image.sampled_field.dvz_sampled_field    found
capture.png.datoviz_capture                     found
banned.v03.dvz_path_alloc_required_by_gsp       false
```

#### M065 details

The harness should not wait for all families. It should initially render existing Point/Image fixtures and immediately prove:

- deterministic output directory structure;
- scene JSON + `.npz` sidecars;
- Matplotlib PNG;
- Datoviz unsupported placeholder;
- contact sheet layout;
- manual notes workflow.

#### M066 details

Point is the Datoviz adapter proving ground. Implement only the direct RGBA8 path first:

```text
PointVisual.colors -> uint8 RGBA8
PointVisual.sizes  -> float32 diameter array
PointVisual.positions -> float32 vec3 positions
```

Scalar color scale and point stroke are follow-up capabilities.

---

## 9. ADR/Spec Changes

Create or update:

1. **`spec/visual_families_v1.md`**  
   Contracts for Point, Marker, Segment, Path, and Image.

2. **`spec/visual_cross_cutting_rules.md`**  
   IDs, coordinate spaces, draw order, colors, alpha, dtype/shape, scalar/per-item semantics, units, clipping, antialiasing, query metadata, serialization.

3. **`spec/visual_qa_harness.md`**  
   CLI, registry, artifact layout, report schema, unsupported representation, contact sheets, manual notes.

4. **`spec/backend_capabilities_visuals.md`**  
   Capability vocabulary and diagnostics, including v0.4 retained-scene symbols.

5. **`spec/datoviz_v04_api_boundary.md`**  
   The corrected Datoviz v0.4 integration contract:
   - no `_alloc` functions;
   - `dvz_<family>(scene, flags)`;
   - `dvz_visual_set_data*`;
   - style helper calls;
   - sampled fields/scales for images;
   - explicit attach descriptors;
   - facade/raw probing.

6. **`spec/vispy2_visual_api.md`**  
   Producer APIs for `scatter`, `markers`, `segment(s)`, `plot/path(s)`, and `imshow`.

7. **`ADR-S023-visual-family-order.md`**  
   Accepts Point → Marker → Segment → Path → Image; defers Text/Glyph and Mesh.

8. **`ADR-S023-screen-space-units.md`**  
   Defines sizes/widths as pixels and Matplotlib conversion rules.

9. **`ADR-S023-datoviz-v04-retained-scene-api.md`**  
   Freezes the v0.4 adapter target and bans v0.3 drift.

10. **`ADR-S023-coordinate-space-v04.md`**  
    Defines GSP NDC/DATA mapping to Datoviz `DvzVisualAttachDesc.coord_space` and panel domain/view APIs.

11. **`ADR-S023-image-sampled-field-colormap-clim.md`**  
    Defines scalar/RGBA image handling, Datoviz sampled-field path, colormap/clim, origin via texcoords, and interpolation capability gating.

12. **`LEGACY_MAP.md` update**  
    Maps legacy visuals to new families as reference material only.

13. **`.agent/decisions/S023_visual_family_contracts.md`**  
    Worker-facing summary with accepted fields, Datoviz v0.4 calls, forbidden symbols, and mission order.

---

## 10. Open Questions

### Human decisions required

1. **Coordinate-space policy:** Should GSP NDC map to Datoviz `DVZ_COORD_VIEW` with an explicit attach descriptor, or should the project rename/clarify GSP `NDC` as Datoviz “visual space” to avoid confusion? Recommendation: map GSP NDC to explicit Datoviz view/visual coordinates after a fixture proves placement.

2. **DATA support threshold:** Should S023 require Datoviz DATA-space rendering via `DVZ_COORD_DATA` and panel domains, or capability-gate DATA to Matplotlib until the transform/view stack is more mature? Recommendation: implement one simple Datoviz DATA smoke case if local v0.4 behavior is clear; otherwise gate it.

3. **Marker shape vocabulary:** Should GSP v1 include only Datoviz built-ins that Matplotlib can approximate, or include Matplotlib-style plus/x and capability-gate them in Datoviz? Recommendation: start with Datoviz-supported built-ins listed in `MarkerShape`.

4. **Path color/width semantics:** Should GSP v1 expose per-path only, or expose Datoviz-style per-point color/width? Recommendation: per-path only in protocol v1; adapter expands to per-point for Datoviz.

5. **Image interpolation:** Should `linear` remain in the protocol if Datoviz v0.4 does not expose a sampler setter yet? Recommendation: keep it for Matplotlib/reference semantics but mark Datoviz `linear` unsupported until an actual v0.4 API is found.

6. **Datoviz closure threshold:** Must S023 produce Datoviz PNGs for Point/Marker/Segment/Path/Image, or is structured unsupported acceptable when Python bindings lag? Recommendation: require Point PNG or explicit human waiver; allow structured unsupported for the others if the probe proves binding gaps.

### Agent-answerable by local inspection

1. Exact generated Python facade signatures for `dvz_visual_set_data` and `dvz_visual_set_data_many`.
2. Whether `dvz_visual_attach_desc()` is exposed in the top-level facade.
3. Whether Datoviz `capture(...)` works in the local environment.
4. Whether `DVZ_COORD_VIEW` or `DVZ_COORD_PANEL` best matches GSP NDC in a fixed QA panel.
5. Whether image sampler/interpolation is controllable in v0.4 source outside `scene.h`.
6. Whether `"shape"` and `"symbol"` are both accepted by the generated Python facade for markers.
7. Whether scalar image sampled fields are fully supported through the Python facade.
8. Whether `dvz_visual_set_texture` and `dvz_visual_set_texture_f32` are easier to use than sampled fields for first Image QA.
9. Exact enum exposure names in Python for `DvzSegmentCap`, `DvzPathJoin`, `DvzSymbolBuiltin`, and `DvzShapeAspect`.

---

## 11. Do-Not-Do Boundaries

- Do **not** use `dvz_path_alloc`, `dvz_point_alloc`, `dvz_marker_alloc`, `dvz_segment_alloc`, or any v0.3-style visual allocation/setter API in S023.
- Do **not** use the legacy Datoviz renderer as the new backend.
- Do **not** treat legacy visual objects as protocol authority.
- Do **not** over-design every visual family before Point is visually validated.
- Do **not** require JSON/base64 for local rendering.
- Do **not** make Datoviz attribute names part of the GSP protocol unless they are also semantic protocol names.
- Do **not** rely on `dvz_panel_add_visual(..., NULL)` for coordinate-space semantics; use an explicit attachment descriptor.
- Do **not** silently fallback from Datoviz to Matplotlib.
- Do **not** block Matplotlib/reference work on incomplete Datoviz Python bindings.
- Do **not** add remote data, network, security, or virtual data-source work in S023.
- Do **not** implement Text/Glyph in S023.
- Do **not** implement Mesh in S023.
- Do **not** add dashes, arrows, closed-path fields, fills, Beziers, tiled images, custom symbols, SVG markers, colorbars, volumes, or advanced normalization.
- Do **not** require pixel-perfect cross-backend diffs.
- Do **not** let unsupported Datoviz cases disappear from reports.
- Do **not** call a family complete until protocol contract, validation, producer API, Matplotlib mapping, Datoviz v0.4 capability boundary, QA cases, and manual checklist are all documented.

---

## Audited Source References

- Datoviz `v0.4-dev` repository README and branch root: `https://github.com/datoviz/datoviz/tree/v0.4-dev`
- Datoviz C scene API header: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/include/datoviz/scene.h`
- Datoviz scene types header: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/include/datoviz/scene/types.h`
- Datoviz scene enums header: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/include/datoviz/scene/enums.h`
- Datoviz sampled-field header: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/include/datoviz/scene/field.h`
- Datoviz scale/colormap header: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/include/datoviz/scene/scale.h`
- Datoviz Python package entry point: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/datoviz/__init__.py`
- Datoviz raw ctypes package entry point: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/datoviz/raw.py`
- Datoviz C visual examples directory: `https://github.com/datoviz/datoviz/tree/v0.4-dev/examples/c/visuals`
- Point example: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/examples/c/visuals/point.c`
- Marker example: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/examples/c/visuals/marker.c`
- Segment example: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/examples/c/visuals/segment.c`
- Path example: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/examples/c/visuals/path.c`
- Image example: `https://raw.githubusercontent.com/datoviz/datoviz/v0.4-dev/examples/c/visuals/image.c`
