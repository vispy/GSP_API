## 1. `Executive Recommendation`

S029 should be **“Backend Capability Matrix and Visual Review Pack”**, not a release/API consolidation stage and not a broad Datoviz promotion stage. The immediate bottleneck is not the absence of feature-specific code, but the lack of a rigorous, auditable distinction between **strict**, **adapted**, **experimental**, and **unsupported** Datoviz behavior across the S023–S028 visual families. The stage should produce useful Matplotlib-left / Datoviz-right artifacts quickly, while refusing to relabel unverified semantics as strict. 

The right policy is: **render first for review, promote later by contract**. Datoviz text, mesh, and colorbar support may be surfaced as **adapted/experimental review artifacts** once the adapter can render them without process instability and emit precise diagnostics, but they should become **strict** only after semantic parity is proven against the GSP spec and Matplotlib reference behavior where applicable.

S029 should also formalize the visual QA output: every case should show whether Datoviz is strict, adapted, experimental, unsupported, or crashed/disabled. Unsupported tiles are not failures if the capability matrix says they are unsupported. Silent fallback is the failure mode to avoid.

For 3D, GSP should not yet create public camera/projection/controller semantics inside S029. It should review **2D MeshVisual strict cases** now, and may add **Datoviz-native fixed-camera 3D preview sheets** as non-protocol, non-strict artifacts. A real 3D protocol stage should require a separate ADR because it affects coordinates, transforms, camera semantics, picking/query, depth ordering, and backend conformance.

The single best immediate next action is to build the **capability matrix + review-pack generator**, because it creates the evidence base needed to promote Datoviz features safely.

---

## 2. `S029 Scope`

### Stage title

**S029 — Backend Capability Matrix and Visual Review Pack**

### Goal

Create an auditable post-S028 system that maps each GSP visual family, guide, transform, query, and review case to an explicit backend capability status:

* `strict`
* `adapted`
* `experimental`
* `unsupported`
* `disabled`
* `crashed`
* `not_run`

The stage should generate Matplotlib-left / Datoviz-right contact sheets and a machine-readable + human-readable capability report for all S023–S028 cases.

### Why this should be S029

S029 should establish **review infrastructure and promotion discipline** before broadening the Datoviz adapter. Otherwise GSP risks confusing three different things:

1. Datoviz engine capability.
2. Datoviz Python facade/API exposure.
3. GSP adapter-verified protocol conformance.

The user’s intuition that Datoviz already supports text, mesh, and colorbars is likely correct at the engine level, but GSP should not infer protocol support from engine support. S029 should make those distinctions visible.

### Non-goals

S029 should **not**:

* declare text, mesh, colorbars, or axes strict merely because Datoviz can render something similar;
* introduce public 3D camera/projection/controller semantics;
* require guide picking/query for Datoviz v0.4 RC;
* make Datoviz offscreen QA mandatory if it can abort the Python process;
* change the GSP public protocol except for metadata/reporting schemas needed for capability review;
* perform a release/API freeze before the capability evidence is available.

### Expected result

After S029, every visual QA case should answer:

* Does Matplotlib strict reference render?
* Does Datoviz render?
* Is Datoviz strict, adapted, experimental, unsupported, disabled, or failed?
* What exact semantic deltas exist?
* What evidence is missing before promotion?

---

## 3. `Mission Plan`

### `M029.1 — Capability Matrix Schema`

**Deliverables**

* A canonical backend capability matrix schema, preferably JSON plus Markdown rendering.
* Rows keyed by:

  * visual family;
  * guide family;
  * transform feature;
  * query scope;
  * visual QA case ID.
* Columns such as:

  * `backend`;
  * `status`;
  * `protocol_scope`;
  * `rendering_supported`;
  * `query_supported`;
  * `known_adaptations`;
  * `known_missing_semantics`;
  * `evidence_artifacts`;
  * `promotion_blockers`;
  * `last_verified`.

**Acceptance criteria**

* All existing S023–S028 cases are represented.
* Matplotlib cases are marked strict where they are the reference path.
* Datoviz cases are conservatively marked using current adapter evidence, not presumed engine support.
* Existing unsupported JSON is absorbed into the matrix rather than duplicated in a separate reporting layer.
* The matrix distinguishes:

  * unsupported by GSP adapter;
  * unsupported by Datoviz facade/API;
  * disabled because offscreen is unsafe;
  * unverified semantics despite renderability.

**Stop conditions**

* Stop promotion work if a feature has no explicit row in the matrix.
* Stop promotion work if a feature can render but has no diagnostic path for unsupported/adapted semantics.
* Stop promotion work if the status taxonomy cannot represent “Datoviz renders this, but GSP semantics are not verified.”

---

### `M029.2 — Review-Pack Generator`

**Deliverables**

* A deterministic review-pack command that produces:

  * per-case Matplotlib PNG;
  * per-case Datoviz PNG or diagnostic tile;
  * side-by-side contact sheets;
  * summary Markdown;
  * machine-readable JSON summary;
  * capability matrix snapshot.
* Tile labels containing:

  * case ID;
  * backend;
  * status;
  * visual family;
  * major semantic adaptations;
  * error/unsupported reason if applicable.

**Acceptance criteria**

* It works when Datoviz offscreen is disabled.
* Disabled Datoviz cases produce explicit diagnostic tiles, not missing files.
* It can generate a complete S023–S028 pack with Matplotlib-left / Datoviz-right layout.
* It has a stable directory layout suitable for manual review and CI artifact upload.
* It can run in at least three modes:

  * `matplotlib-only`;
  * `datoviz-diagnostic`;
  * `datoviz-offscreen-opt-in`.

**Stop conditions**

* Stop if Datoviz native offscreen creation can abort the Python process without isolation.
* Stop if a missing Datoviz image is indistinguishable from an unsupported feature.
* Stop if the report cannot tell whether a failure is adapter unsupported, backend unavailable, process-disabled, or runtime crash.

---

### `M029.3 — Datoviz Adapter Promotion Audit`

**Deliverables**

* A per-family audit of implemented-but-not-advertised Datoviz support:

  * point;
  * marker;
  * segment;
  * path;
  * image;
  * transform-pretransformed 2D affine cases.
* A proposed update to Datoviz advertised `visual_families`, but only for families that meet adapted or strict criteria.
* Structured diagnostics for each missing semantic.

**Acceptance criteria**

* Point remains strict or adapted only for the exact proven scope: NDC positions, RGBA, pixel diameter.
* Marker/segment/path/image are promoted only if their current adapter paths are verified enough for their declared status.
* Scalar marker fill remains unsupported unless actual scalar-to-color mapping semantics are implemented and verified.
* Image support distinguishes scalar gray, RGB/RGBA, interpolation, origin, extent, and sampled-field adaptation.
* Every promotion has at least one visual QA artifact and one capability matrix entry.

**Stop conditions**

* Stop if promotion would require silent CPU conversion, visual approximation, or ignored fields without diagnostics.
* Stop if adapter behavior depends on optional Datoviz facade symbols but does not record symbol availability.
* Stop if advertised capability is broader than tested scope.

---

### `M029.4 — Text / 2D Mesh / Colorbar Experimental Surfacing`

**Deliverables**

* Optional Datoviz rendering paths for:

  * `TextVisual`;
  * strict-scope 2D `MeshVisual`;
  * `ColorbarGuide`.
* Initial status should be `experimental` or `adapted`, not `strict`, unless full parity evidence exists.
* New visual QA cases or promoted existing cases showing Datoviz output side-by-side with Matplotlib.

**Acceptance criteria**

For text:

* position mapping verified;
* anchor behavior documented;
* font-size mapping documented;
* rotation behavior documented;
* RGBA and alpha behavior verified;
* multiline/Unicode status explicitly reported.

For 2D mesh:

* indexed triangles render with topology preserved;
* z=0 / 2D mapping is explicit;
* uniform RGBA verified;
* per-face RGBA either verified or marked adapted/unsupported;
* deterministic visual order documented.

For colorbar:

* colormap binding verified;
* normalization/range verified;
* tick value/label status reported;
* layout differences marked adapted;
* query explicitly unsupported for Datoviz v0.4 RC.

**Stop conditions**

* Stop before strict promotion if Matplotlib-left and Datoviz-right cannot be visually reviewed for the same case.
* Stop before strict promotion if query payload parity is required by the GSP feature but unavailable.
* Stop before strict promotion if the Datoviz path ignores anchors, labels, ticks, normalization, or face colors without diagnostics.

---

### `M029.5 — Axes / Guides Datoviz Status Normalization`

**Deliverables**

* Capability rows for:

  * `AxisGuide`;
  * `PanelTextGuide`;
  * backend auto ticks;
  * explicit ticks/labels;
  * reversed finite domains;
  * grid lines;
  * guide query.
* Visual review sheets for:

  * `guide/view2d_auto_grid`;
  * `guide/view2d_reversed_explicit`.

**Acceptance criteria**

* Datoviz axes can be marked `adapted` if backend auto ticks render against the same `View2D` domain.
* Explicit GSP ticks/labels remain unsupported unless preserved exactly.
* Reversed domains remain adapted/experimental until proof exists.
* Guide query remains unsupported and does not block rendering status.
* The report distinguishes guide rendering from guide picking/query.

**Stop conditions**

* Stop if guide rendering and guide query are represented as a single capability.
* Stop if explicit ticks are silently replaced by backend auto ticks.
* Stop if reversed-domain behavior is assumed from ordinary-domain behavior.

---

### `M029.6 — Query Payload Evidence Pass`

**Deliverables**

* Query capability matrix entries for:

  * point;
  * image;
  * marker;
  * mesh face;
  * scalar payload;
  * transform inverse payload;
  * guide scope;
  * all-rendered-with-guides.
* Review cases or tests proving frontmost item selection and payload contents where supported.

**Acceptance criteria**

* Datoviz point/image query is marked supported only for the exact runtime scope where bindings exist.
* Payloads include enough information to verify GSP semantics: family, item index or texel, value, displayed RGBA where applicable.
* Guide-scope and all-rendered-with-guides remain unsupported without penalty.
* Transform inverse payload remains unsupported unless implemented and verified.

**Stop conditions**

* Stop promotion to strict if rendering is correct but query is part of the strict contract and is missing.
* Stop if query success depends on panel-coordinate conventions not recorded in the diagnostic output.
* Stop if scalar query payloads cannot distinguish raw scalar value from displayed color.

---

### `M029.7 — Non-Strict 3D Preview Pack`

**Deliverables**

* A clearly separated `experimental_3d/` review-pack section.
* Datoviz-native fixed-camera previews for selected 3D mesh examples.
* No public GSP 3D camera/projection/controller API.
* No strict Matplotlib conformance claim.

**Acceptance criteria**

* The 3D preview pack is visibly labeled:

  * `experimental`;
  * `non-strict`;
  * `Datoviz-native`;
  * `not protocol-conformant evidence`.
* The examples are useful for manual review of Datoviz capacity without implying GSP 3D semantics.
* Any `(N,3)` `MeshVisual` protocol data remains unsupported for strict rendering unless a 3D view/camera/projection capability is explicitly accepted.

**Stop conditions**

* Stop immediately if preview code begins to define public camera/projection semantics.
* Stop if 3D examples are mixed into strict S023–S028 sheets without labels.
* Stop if users could reasonably interpret the 3D pack as GSP conformance.

---

## 4. `Capability Promotion Rules`

### Global promotion taxonomy

#### `strict`

Use only when:

* all required GSP fields are honored;
* behavior is deterministic;
* unsupported fields are rejected with structured diagnostics;
* Matplotlib reference parity exists where Matplotlib is the reference backend;
* visual QA artifacts exist;
* query semantics are verified where query is part of the feature contract;
* no silent adaptation occurs.

#### `adapted`

Use when:

* Datoviz renders a useful equivalent;
* the adaptation is deterministic and documented;
* unsupported semantic differences are explicit;
* review artifacts exist;
* the result is acceptable for high-performance GPU use but not identical to strict reference behavior.

Examples: backend auto ticks instead of exact explicit ticks, CPU pre-transform before upload, approximate font metric differences.

#### `experimental`

Use when:

* Datoviz can render something useful;
* adapter contracts are incomplete;
* visual review is desired;
* semantics may change;
* the feature must not appear in stable advertised capabilities.

Experimental is appropriate for early text, colorbar, and 3D preview artifacts.

#### `unsupported`

Use when:

* the GSP adapter cannot implement or verify required semantics;
* Datoviz facade/API exposure is missing;
* the feature is explicitly deferred;
* process safety prevents execution.

Unsupported must produce structured diagnostics.

---

### Datoviz `TextVisual`

#### Promote to `adapted` when:

* text strings render at the intended positions;
* RGBA and alpha work;
* font-size mapping is documented, even if not pixel-perfect;
* anchors are implemented or explicitly approximated;
* rotation is either implemented or rejected per case;
* multiline/Unicode support is tested and status-labeled.

#### Promote to `strict` only when:

* position, anchors, logical pixel font size, RGBA, alpha, rotation, multiline behavior, and Unicode smoke behavior match the GSP contract closely enough for the reference cases;
* any font-family/font-role limitations are reflected in the protocol/diagnostics;
* text extents or anchor interpretation are stable enough to make visual QA meaningful.

#### Keep `unsupported` when:

* text placement works but anchors/size/rotation are unknown;
* Datoviz symbols are unstable or absent;
* the adapter cannot prevent silent semantic loss.

---

### Datoviz `MeshVisual` — 2D strict-scope mesh

#### Promote to `adapted` when:

* inline indexed triangles render;
* NDC/DATA 2D positions are mapped deterministically;
* uniform RGBA works;
* per-face RGBA is either implemented or explicitly adapted;
* face ordering/topology is preserved enough for visual review.

#### Promote to `strict` only when:

* indexed topology is preserved;
* uniform and per-face RGBA match the GSP v1 semantics;
* 2D z handling is explicit and deterministic;
* visual ordering is deterministic;
* 2D face query payloads are supported if required by the strict case.

#### Keep `unsupported` when:

* mesh rendering exists only through a Datoviz-native material path whose mapping to flat GSP RGBA is unknown;
* per-face color is silently converted or dropped;
* face query payloads are claimed but not verified.

---

### Datoviz `ColorbarGuide`

#### Promote to `adapted` when:

* a visible colorbar is rendered;
* it is bound to the intended `ColorScale`;
* colormap and normalization are correct;
* layout is stable enough for review;
* tick/label limitations are explicit;
* query remains explicitly unsupported.

#### Promote to `strict` only when:

* canonical colormap, linear normalization, scalar range, tick values, tick labels, orientation, and layout contract are verified against GSP semantics;
* Matplotlib reference cases are matched within accepted visual tolerances;
* ramp-query behavior is either supported where required or excluded from the strict contract.

#### Keep `unsupported` when:

* Datoviz can draw a colorbar but the adapter cannot prove scale binding;
* explicit ticks/labels are ignored;
* colorbar is manually approximated without contract.

---

### Datoviz axes/guides

#### Promote to `adapted` when:

* Datoviz axes render from the same `View2D` domain as data visuals;
* backend auto ticks are used and declared;
* grid lines align to backend ticks;
* guide query is explicitly unsupported.

#### Promote to `strict` only when:

* explicit GSP ticks and labels are preserved exactly;
* reversed finite domains are verified;
* grid lines align to the intended ticks;
* axis labels and panel text/title semantics are stable;
* the same `View2D` snapshot is used for guide and data rendering.

#### Keep parts `unsupported` when:

* explicit ticks are not supported;
* guide picking/query is unavailable;
* reversed-domain proof is missing.

---

### Datoviz query payloads

#### Promote to `adapted` when:

* frontmost panel-coordinate query works for a constrained family;
* payload includes visual family, item identity, and basic value;
* limitations are explicit.

#### Promote to `strict` only when:

* payload matches GSP query semantics for the family;
* scalar values and displayed RGBA are distinguishable;
* image texel queries return correct texel/value/color metadata;
* transform inverse payloads are correct where transforms are involved;
* deterministic frontmost selection is verified.

#### Keep `unsupported` when:

* guide query or all-rendered-with-guides is requested for Datoviz v0.4 RC;
* bindings are absent;
* payloads are too thin to prove semantic parity.

---

### Datoviz 3D mesh

#### Promote to `experimental` only for now when:

* Datoviz renders fixed-camera 3D examples;
* artifacts are clearly outside strict GSP conformance;
* no public camera/projection/controller semantics are introduced.

#### Do not promote to `adapted` or `strict` until:

* GSP defines public 3D view/camera/projection semantics;
* transform composition is specified;
* depth ordering and clipping are specified;
* 3D query/picking expectations are specified or explicitly excluded;
* Matplotlib’s role for 3D is clarified;
* a separate ADR accepts the 3D model.

---

## 5. `Visual Review Artifact Plan`

### Artifact structure

Recommended output layout:

```text
visual_qa_review_pack/
  index.md
  capability_matrix.json
  capability_matrix.md
  summary.json
  summary.md

  sheets/
    s023_visual_families.png
    s024_text.png
    s025_mesh_2d.png
    s026_color_mapping_colorbars.png
    s027_transform_view2d.png
    s028_guides_view2d.png
    experimental_3d_datoviz_native.png

  cases/
    point/basic_ndc/
      matplotlib.png
      datoviz.png
      side_by_side.png
      status.json
      notes.md

    text/basic_ndc/
      matplotlib.png
      datoviz.png
      side_by_side.png
      status.json
      notes.md
```

### Side-by-side convention

Each case should render:

```text
┌───────────────────────────────┬───────────────────────────────┐
│ Matplotlib reference           │ Datoviz                       │
│ status: strict                 │ status: adapted/unsupported   │
│ case: text/basic_ndc           │ case: text/basic_ndc           │
└───────────────────────────────┴───────────────────────────────┘
```

Matplotlib should remain the left tile for S023–S028 2D semantics. Datoviz should remain the right tile even when unsupported, disabled, or experimental.

### Datoviz tile states

Datoviz tiles should never be blank without explanation. Use visible diagnostic tiles:

* `UNSUPPORTED`
* `ADAPTED`
* `EXPERIMENTAL`
* `OFFSCREEN DISABLED`
* `BACKEND SYMBOL MISSING`
* `PROCESS ISOLATION REQUIRED`
* `CRASHED`
* `NOT RUN`

Each diagnostic tile should include the structured reason code, not just prose.

Example:

```json
{
  "backend": "datoviz",
  "case_id": "color/scalar_image_viridis_colorbar",
  "status": "unsupported",
  "reason_code": "datoviz_colorbar_contract_unverified",
  "missing_semantics": [
    "scale binding",
    "explicit tick labels",
    "ramp query"
  ],
  "guide_query_status": "deferred"
}
```

### Review categories

The summary matrix should group cases by decision status:

| Category                 | Meaning                                      | Action                                     |
| ------------------------ | -------------------------------------------- | ------------------------------------------ |
| `strict-pass`            | Datoviz matches GSP semantics                | Candidate for advertised strict capability |
| `adapted-review`         | Useful rendering with documented differences | Keep visible, do not claim strict          |
| `experimental-review`    | Useful preview, semantics incomplete         | Keep out of stable capability snapshot     |
| `unsupported-expected`   | Known unsupported feature                    | Not a regression                           |
| `unsupported-unexpected` | Should have worked per matrix                | Regression                                 |
| `disabled`               | Offscreen or environment disabled            | Infrastructure issue                       |
| `crashed`                | Runtime/process failure                      | Must isolate before retry                  |

### Review-pack modes

Recommended commands:

```bash
gsp-visual-qa review-pack --backend matplotlib --suite s023-s028
gsp-visual-qa review-pack --backend datoviz --suite s023-s028 --diagnostic-only
GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1 gsp-visual-qa review-pack --backend datoviz --suite s023-s028
gsp-visual-qa review-pack --suite s023-s028 --side-by-side
```

For process safety, Datoviz offscreen rendering should ideally run in subprocess isolation. A native abort should mark only that case as `crashed`, not kill the entire review pack.

---

## 6. `3D Policy`

### What to review now

GSP should review **2D strict-scope mesh cases now**:

* `mesh/single_triangle_uniform_ndc_2d`
* `mesh/indexed_square_uniform_ndc_2d`
* `mesh/indexed_square_per_face_ndc_2d`

These belong in the S025/S029 strict or adapted matrix because they are already within the v1 mesh scope.

GSP may also add **Datoviz-native 3D preview artifacts** for manual inspection, but they must be isolated from conformance artifacts.

### What to defer

Defer public protocol semantics for:

* 3D camera;
* projection;
* clipping;
* navigation controllers;
* lighting;
* materials;
* depth testing contract;
* 3D picking/query;
* Matplotlib 3D reference behavior;
* model resources;
* instancing;
* textures/PBR.

### What requires a separate ADR

A future 3D stage should begin only after an ADR decides:

1. Coordinate spaces: DATA, NDC, world, view, clip.
2. Camera model: orthographic, perspective, or both.
3. Projection parameters and units.
4. Transform stack semantics.
5. Depth ordering and blending rules.
6. Query/picking scope.
7. Whether Matplotlib is a reference, smoke backend, or non-conforming backend for 3D.
8. Whether Datoviz-native GPU semantics define the initial 3D reference behavior.
9. How 2D overlays, guides, and colorbars interact with 3D views.

### Recommended current 3D status

For S029:

```text
2D MeshVisual strict cases: in scope
(N,3) mesh protocol data: valid data, strict rendering unsupported without accepted 3D view
Datoviz-native 3D examples: experimental review artifacts only
Public GSP 3D camera/projection/controller API: deferred
```

---

## 7. `Datoviz vs GSP Work Split`

### Belongs in Datoviz

Datoviz should provide or confirm stable Python facade contracts for:

* panel `View2D` / domain API shared by axes and data visuals;
* explicit axis tick values and labels;
* reversed finite domains;
* grid lines aligned to ticks;
* axis labels and panel text/title;
* text placement, anchors, rotation, size, and font behavior;
* mesh flat RGBA and per-face color behavior;
* colorbar scale binding, ticks, labels, orientation, and layout;
* data query payloads for points, images, markers, mesh faces, and scalar values;
* safe offscreen rendering behavior or a documented subprocess-safe strategy.

Datoviz does **not** need to provide guide picking/query for the v0.4 RC if GSP marks that scope unsupported/deferred.

### Belongs in GSP adapter

GSP should implement:

* protocol-to-Datoviz mapping;
* capability-gated dispatch;
* structured unsupported/adapted diagnostics;
* symbol and version detection;
* visual QA case registration;
* review-pack generation;
* promotion status management;
* scalar normalization and colormap mapping checks;
* CPU pre-transform diagnostics where used;
* Matplotlib-left / Datoviz-right artifact generation;
* strict/adapted/experimental capability matrix.

GSP must also prevent silent fallback. If GSP adapts a semantic, the artifact and JSON report must say so.

### Can happen in parallel

These can proceed independently once the matrix schema exists:

* Datoviz confirms facade contracts for text, mesh, colorbar, axes.
* GSP adds experimental rendering paths for text/mesh/colorbar.
* GSP improves review-pack generation.
* GSP isolates Datoviz offscreen rendering in subprocesses.
* GSP audits marker/segment/path/image promotion.
* GSP adds non-strict 3D preview sheets.

The dependency is not linear implementation; it is **evidence discipline**. The matrix must exist first so that parallel work has somewhere to record status and blockers.

---

## 8. `Immediate Next Action`

Implement **`M029.1 + minimal `M029.2` together**:

> Build the capability matrix schema and generate the first complete S023–S028 Matplotlib-left / Datoviz-right review pack, with diagnostic Datoviz tiles for unsupported, disabled, adapted, and experimental cases.

This is the highest-leverage first mission because it immediately gives the user the images they want to review, while protecting GSP from overclaiming Datoviz support. Once that pack exists, promotion of marker/segment/path/image, then text/2D mesh/colorbar, becomes a controlled evidence-based process rather than an argument about whether Datoviz “supports” a feature in general.

