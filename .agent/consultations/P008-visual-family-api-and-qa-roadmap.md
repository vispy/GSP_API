# P008 - Visual family API and visual QA roadmap

Status: response received in `.agent/consultations/P008-response.md`.

This needs ChatGPT Pro consultation.

## Why This Is Needed

GSP_API has completed the protocol/security groundwork through S022. The next desired direction is
not remote data; it is building a clear, modern visual API and backend implementation path family by
family, with careful manual visual inspection across Matplotlib and Datoviz v0.4.

The hard part is architectural: choosing stable visual-family contracts, property names, dtype/shape
rules, user-facing VisPy2/GSP APIs, backend capability boundaries, and a visual QA harness so
medium-reasoning implementation agents can proceed without drifting back to legacy paths.

Do not implement this until the response is pasted or committed and converted into specs/ADRs/tasks.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

```text
You are an architecture reviewer for GSP_API, a Python research prototype for a backend-independent
Graphics Server Protocol (GSP) for scientific visualization.

Your task is to propose a concrete S023 roadmap and visual-family API plan for the next phase of
GSP_API. This is a pre-implementation architecture review. Do not write implementation code. The
answer must be concrete enough for medium-reasoning Codex worker agents to implement stage/mission
tasks without inventing visual semantics.

The goal is to proceed visual family by visual family, starting with the simplest families, while:

- using Matplotlib as the reference/conformance/publication backend;
- using Datoviz v0.4 as the flagship GPU backend, even though bindings may still be incomplete;
- using the existing legacy GSP visual/rendering implementation only as reference material and
  visual inspiration, not as the foundation for the new implementation;
- making VisPy2 and/or GSP high-level APIs produce formal GSP protocol scenes;
- creating examples that can be manually inspected carefully with both Matplotlib and Datoviz v0.4.

Do not assume repository access. All relevant context is embedded below.

## Project Principles

GSP should allow one semantic visualization description to target:

- fast local GPU rendering through Datoviz v0.4;
- reference/publication rendering through Matplotlib;
- remote renderers;
- future web/browser paths through Datoviz/WebGPU where available;
- extension/data-source systems for huge distributed datasets.

Non-negotiable principles:

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and should use a unified panel-query model.
7. Extensions must be manifest-, version-, and capability-driven.
8. Huge datasets should be represented as virtual data sources, not ordinary buffers.
9. Datoviz v0.4 is the flagship GPU backend.
10. Matplotlib is the reference/conformance/publication backend.
11. VisPy2 is the high-level Python producer of GSP scenes.
12. Existing source code is implementation material, not protocol authority.

Authority order in this project:

1. PROJECT_CHARTER.md
2. ARCHITECTURE.md
3. SPEC_INDEX.md
4. spec/**
5. accepted ADRs and .agent/decisions/**
6. LEGACY_MAP.md
7. existing source code

## Current Project State

All previous stages through S022 are complete. Key completed work:

- Protocol spine exists.
- Matplotlib reference point/image rendering exists.
- Datoviz v0.4 adapter slice exists but is narrow.
- VisPy2 producer MVP exists for scatter/imshow/guides.
- Query/capability groundwork exists.
- Conformance fixture/replay harness exists.
- Remote data/security groundwork exists, but remote data is not the next priority.

Mission Control now has no next mission queued. The desired next direction is visual families,
examples, and manual visual QA.

## Current New Protocol Visual Model

The current protocol visual model is deliberately small:

```python
class CoordinateSpace(str, Enum):
    NDC = "ndc"
    DATA = "data"

class ImageInterpolation(str, Enum):
    NEAREST = "nearest"
    LINEAR = "linear"

class ImageOrigin(str, Enum):
    UPPER = "upper"
    LOWER = "lower"

FloatArray = NDArray[float32] | NDArray[float64]
ColorArray = NDArray[uint8] | NDArray[float32] | NDArray[float64]
ImageArray = NDArray[uint8] | NDArray[float32] | NDArray[float64]

@dataclass(frozen=True, slots=True)
class PointVisual:
    id: str
    positions: FloatArray             # shape (N, 2) or (N, 3)
    colors: ColorArray                # shape (N, 4), rgba8 or float [0, 1]
    sizes: FloatArray | float         # scalar or shape (N,), non-negative
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC

@dataclass(frozen=True, slots=True)
class ImageVisual:
    id: str
    image: ImageArray                 # shape (H, W), (H, W, 3), or (H, W, 4)
    extent: tuple[float, float, float, float]
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
    interpolation: ImageInterpolation = ImageInterpolation.NEAREST
    origin: ImageOrigin = ImageOrigin.UPPER
```

Current validation:

- IDs are validated.
- Point positions must be float32/float64 and shape (N, 2) or (N, 3).
- Point colors must be shape (N, 4), either uint8 or float32/float64 in [0, 1].
- Point sizes must be scalar or shape (N,), float32/float64, non-negative.
- Images must be 2D scalar or 3/4-channel, uint8 or float32/float64 in [0, 1].

## Current VisPy2 Producer MVP

VisPy2 currently provides:

- `vispy2.subplots() -> (Figure, Axes)`
- `Axes.scatter(...) -> PointVisual`
- `Axes.imshow(...) -> ImageVisual`
- `Figure.visuals()`
- `Figure.panels()`
- `Figure.views()`
- `Figure.attachments()`
- axis guides and panel title/label/tick/grid semantic guide APIs
- `Figure.render_matplotlib()`
- `Figure.savefig(...)`

Current high-level scatter accepts:

- `x`, `y` or an `(N, 2|3)` array;
- `color`/`c` as RGBA;
- `size`/`s` as scalar or per-point array.

Current high-level imshow accepts:

- image array;
- extent;
- origin;
- interpolation.

Current examples:

- `examples/vispy2_protocol_scatter.py`
- `examples/vispy2_protocol_imshow.py`
- `examples/vispy2_protocol_point_over_image.py`
- `examples/vispy2_protocol_guides.py`

These render through Matplotlib only today.

## Current Backend State

### Matplotlib new protocol path

Matplotlib reference functions exist:

```python
def render_point_visual(axes, visual: PointVisual):
    offsets = visual.positions[:, :2]
    sizes = visual.sizes if scalar else visual.sizes.reshape(-1)
    axes.scatter(offsets[:, 0], offsets[:, 1], s=sizes, c=rgba_for_matplotlib(visual.colors))

def render_image_visual(axes, visual: ImageVisual):
    axes.imshow(
        visual.image,
        extent=visual.extent,
        interpolation="nearest" or "bilinear",
        origin=visual.origin.value,
    )
```

Matplotlib also has guide rendering for axis labels, ticks, grid, and title.

### Datoviz v0.4 new protocol path

There is a new Datoviz v0.4 protocol adapter slice, not to be confused with legacy Datoviz support.
It currently has a narrow implementation:

- `DatovizV04ProtocolRenderer`
- `add_point_visual(PointVisual)`
- `add_image_visual(ImageVisual)`
- capability translation;
- optional offscreen PNG capture when the binding exposes capture symbols;
- optional sampled-field image path when the binding exposes sampled-field symbols;
- query/capture capability gates.

Important constraints:

- The adapter currently supports only NDC point positions.
- It supports image only for NDC extents and nearest interpolation.
- It currently targets top-level `dvz_*` Datoviz v0.4 facade functions.
- The local installed Python package in the GSP venv may not expose the complete expected v0.4
  facade. However, a sibling repository `../datoviz/` contains usable Datoviz v0.4 source,
  examples, tests, and Python binding work. The plan should assume agents can inspect and use
  `../datoviz/` locally during implementation.

Observed Datoviz v0.4 source examples in `../datoviz/` include C examples for:

- point;
- marker;
- segment;
- path;
- pixel;
- image;
- text/glyph;
- mesh;
- sphere;
- volume;
- vector;
- splat;
- labels.

Observed Datoviz v0.4 API patterns include:

- `dvz_point(scene, flags)`
- `dvz_marker(scene, flags)`
- `dvz_segment(scene, flags)`
- `dvz_path(scene, flags)`
- `dvz_image(scene, flags)`
- `dvz_text(panel, flags)` or text/glyph-related APIs
- `dvz_visual_set_data(...)`
- `dvz_visual_set_data_many(...)`
- `dvz_visual_set_data_range(...)`
- marker/segment/path style helpers such as cap/join/style setters
- sampled-field APIs for images/volumes where available

Agents must verify exact Datoviz calls against `../datoviz/` before implementation.

### Legacy GSP visual path

The legacy GSP object/rendering path has broad visual coverage and examples:

- Points
- Pixels
- Markers
- Segments
- Paths
- Image
- Texts
- Mesh and material variants

Legacy Matplotlib and legacy Datoviz renderer modules exist for many of these. These are useful for
understanding existing behavior and example intent, but the new implementation should be based on
formal protocol visual-family contracts, not direct reuse of the old object graph.

## What The User Wants

The user wants to move toward examples based on VisPy2 and/or GSP that can be manually tested with
Matplotlib and Datoviz v0.4, checking visuals carefully.

The user specifically said:

- There is still quite some work on the GSP visual side, especially for Matplotlib and Datoviz v0.4.
- Datoviz v0.4 needs to be used even if not final right now.
- Datoviz v0.4 is usable already in `../datoviz/`.
- Legacy is good as illustrative example, but for the new implementation we want to redo clearly
  from nice solid foundations, not based off the legacy Datoviz path.
- Proceed visual family per visual family, starting with the simplest ones.
- Look at what was done in legacy, and see how to progress on the new API.

## Design Question

Propose the S023 roadmap and contracts for the visual-family phase.

You should decide/propose:

1. Stage definition for S023.
2. Visual-family implementation order.
3. The visual QA harness architecture.
4. The minimal v1 protocol contract for each early visual family.
5. The VisPy2/GSP user-facing API shape for each early visual family.
6. Matplotlib reference semantics for each early family.
7. Datoviz v0.4 implementation strategy and capability boundaries for each early family.
8. Manual visual QA examples and expected artifacts.
9. Mission breakdown suitable for medium-reasoning implementation agents.
10. Explicit “do not do yet” boundaries.

Do not make decisions depend on unspecified attachments or repo paths. Include enough detail in your
answer that it can be converted into ADR/spec/task files.

## Candidate Visual Family Order

The current local recommendation is:

1. Point
2. Marker
3. Segment
4. Path
5. Image
6. Text/Glyph
7. Mesh

You may revise this order, but explain why.

The intended reasoning is:

- Point already exists and can harden the QA harness and Datoviz v0.4 setup.
- Marker is a natural next step: shape, fill/stroke, size.
- Segment is simple line geometry and important for overlays.
- Path builds on segment with joins/caps/subpaths.
- Image exists but needs stronger contract around dtype/origin/extent/interpolation/colormap.
- Text/Glyph is important but tricky due to fonts, alignment, DPI, and anchors.
- Mesh has larger scope and should come later.

## Expected Output Format

Return a concise but concrete plan with the following sections.

### 1. Executive Recommendation

State the recommended next stage direction in 5-10 bullets.

### 2. S023 Stage Definition

Provide:

- stage id/title;
- goal;
- non-goals;
- completion criteria;
- major risks.

### 3. Visual QA Harness Contract

Specify:

- command-line shape;
- Python module/script layout;
- artifact directory layout;
- required output files;
- JSON report schema;
- how to represent backend unsupported/capability-gated cases;
- whether and how to produce side-by-side contact sheets;
- how manual inspection notes should be recorded;
- what should be tested automatically vs inspected manually.

### 4. Visual Family Order

Provide a table:

| Order | Family | Why now | Main protocol fields | Main backend risks | Deferred fields |

### 5. Cross-Cutting Protocol Rules

Specify stable rules for:

- `id`;
- coordinate spaces;
- transforms/views/attachments;
- z-order/draw order;
- colors;
- alpha/compositing;
- dtype/shape validation;
- scalar vs per-item properties;
- units for sizes, widths, marker sizes;
- clipping;
- antialiasing;
- picking/query metadata;
- capability/adaptation diagnostics;
- serialization vs in-process array handling.

### 6. Early Family Contracts

For each of Point, Marker, Segment, Path, and Image, provide:

- semantic purpose;
- minimal v1 protocol dataclass fields;
- validation rules;
- VisPy2/GSP producer API shape;
- Matplotlib reference mapping;
- Datoviz v0.4 mapping and required API symbols to verify;
- manual QA example design;
- automatic tests;
- deferred features.

If you believe Text/Glyph should also be included in S023, include the same details; otherwise state
why it should be deferred to S024.

### 7. Datoviz v0.4 Integration Plan

Specify:

- how agents should use `../datoviz/`;
- how to verify the top-level Python facade or binding symbols;
- how to handle incomplete bindings without blocking Matplotlib work;
- what the minimum usable Datoviz v0.4 visual QA path should be;
- how to avoid legacy `gsp_datoviz.renderer` dependency;
- what capability diagnostics should look like.

### 8. Mission Breakdown

Provide mission-sized tasks, starting at M064, with:

| Mission | Title | Goal | Deliverables | Acceptance | Stop Conditions |

Make the first 3 missions especially detailed. They should be implementable by medium-reasoning
agents.

### 9. ADR/Spec Changes

List the ADR/spec files that should be created or updated and summarize what each should contain.

### 10. Open Questions

List questions that truly require human decision, and separate them from questions agents can answer
by inspecting code or Datoviz examples.

### 11. Do-Not-Do Boundaries

List explicit boundaries, including:

- do not use legacy Datoviz renderer as the new backend;
- do not over-design all visual families before one family is visually validated;
- do not require JSON/base64 for local rendering;
- do not make Datoviz-specific draw calls part of the protocol;
- do not block all work on perfect Datoviz binding completeness;
- do not add remote data/network work in this stage.

Be concrete. Prefer implementable contracts and mission acceptance criteria over abstract guidance.
```
