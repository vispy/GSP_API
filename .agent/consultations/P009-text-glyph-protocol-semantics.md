# P009 - Text/Glyph protocol semantics

Status: awaiting ChatGPT Pro response.

This needs ChatGPT Pro consultation.

## Why This Is Needed

S023 completed protocol visual-family v1 for Point, Marker, Segment, Path, and Image plus a manual
visual QA harness. The next requested direction is Text/Glyph. Text is deceptively architectural:
font discovery, fallback, shaping, glyph atlas ownership, anchors, baselines, DPI, rotation, query
payloads, and backend capability variance can leak into the public protocol if not decided up front.

Do not commit public Text/Glyph semantics or implement renderer behavior until the response is pasted
or committed and converted into an ADR/spec baseline. Evidence gathering and backend API probing are
allowed if they do not freeze protocol fields.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

```text
You are an architecture reviewer for GSP_API, a Python research prototype for a backend-independent
Graphics Server Protocol (GSP) for scientific visualization.

Your task is to recommend a narrow, durable Text/Glyph visual-family protocol for the next stage
(S024). This is a pre-implementation architecture review. Do not write implementation code. The
answer must be concrete enough for worker agents to create ADRs, specs, validation tests, Matplotlib
reference rendering, Datoviz capability gates, VisPy2 producer APIs, and visual QA cases without
inventing protocol semantics.

## Project principles

GSP should allow one semantic visualization description to target:

- fast local GPU rendering through Datoviz v0.4;
- reference/publication rendering through Matplotlib;
- remote renderers;
- future web/browser paths where available;
- extension/data-source systems for huge distributed datasets.

Non-negotiable principles:

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and uses a unified panel-query model.
7. Extensions are manifest-, version-, and capability-driven.
8. Huge datasets are virtual data sources, not ordinary buffers.
9. Datoviz v0.4 is the flagship GPU backend.
10. Matplotlib is the reference/conformance/publication backend.
11. VisPy2 is the high-level Python producer of GSP scenes.
12. High-reasoning design work is captured in specs, ADRs, and task files.
13. Existing source code is implementation material, not protocol authority.

Authority order in this project:

1. PROJECT_CHARTER
2. ARCHITECTURE
3. SPEC_INDEX
4. accepted specs
5. accepted ADRs and decision records
6. legacy map
7. existing source code

If code and intended specs conflict, the design should stop and report instead of inventing a third
semantics.

## Current accepted visual baseline

S023 accepted these protocol visual families:

| Family | Protocol model | Important accepted semantics |
|---|---|---|
| Point | PointVisual | positions are finite 2D/3D arrays; RGBA colors; sizes are rendered screen-pixel diameters; coordinate_space is NDC or DATA. |
| Marker | MarkerVisual | shaped markers; fill RGBA; scalar/per-marker pixel diameters; angles are radians; stroke width is screen pixels. |
| Segment | SegmentVisual | independent line segments; RGBA colors; widths are screen-pixel stroke widths; conservative cap enum. |
| Path | PathVisual | open polyline/subpath visual; path_lengths partition vertices; per-subpath RGBA and width; conservative cap/join/miter fields. |
| Image | ImageVisual | 2D scalar/RGB/RGBA arrays; extent; origin upper/lower; nearest/linear interpolation; scalar gray colormap and clim only. |

Cross-cutting accepted rules:

- Every visual has a stable protocol id.
- Numeric arrays are finite; positions are float32/float64 shape (N, 2) or (N, 3).
- RGBA arrays are uint8 [0,255] or float [0,1].
- Point/marker sizes and stroke widths are screen pixels, not backend-native units.
- CoordinateSpace values are NDC and DATA.
- S023 visual QA uses NDC fixtures over [-1,+1].
- Backend-native names and units stay internal.
- Text/Glyph, Mesh, legends, colorbars, tiled/remote images, and interactive editing were explicitly deferred.

Current protocol code style uses frozen dataclasses with validation, small enums, NumPy arrays for
in-process paths, and sidecar NPZ arrays only for debug/replay fixtures.

## Existing guide/text-adjacent baseline

GSP already has semantic guide models for axes and panel title-like text, but these are not accepted
as a general TextVisual contract:

- AxisGuide can carry label_text and tick labels.
- PanelTextGuide can carry a title string.
- Matplotlib can render guide labels/titles using Matplotlib axis/title APIs.
- Guide query payloads may include text values.
- Generated axis/guide primitives are backend realization artifacts and are not the public visual
family contract.

The next Text/Glyph stage must decide whether general text labels are ordinary visuals, separate
from guides, and how guide text realization should relate to TextVisual/GlyphVisual later.

## Legacy implementation facts, not authoritative

The legacy code has a Texts visual with these fields:

- positions;
- strings;
- colors;
- font_sizes;
- textAligns using a 3x3-style alignment vocabulary such as top/center/bottom and left/center/right;
- angles in degrees;
- font_name as a string.

Legacy Matplotlib rendering maps each string to a Matplotlib Text artist. Legacy Datoviz rendering
uses older/private Datoviz APIs and is not reliable for v0.4 protocol semantics. Prior notes said
Datoviz text anchor and rotation were problematic. Legacy behavior must be mined only as reference
material.

## Datoviz v0.4 context

S023 established that Datoviz v0.4 should be treated as a C-first retained scene API, not a v0.3
Python plotting compatibility layer. Implementations use retained visual constructors plus generic
attribute uploads such as dvz_visual_set_data*, explicit panel attachment descriptors, and capability
reports. No worker should plan against v0.3-style alloc/setter APIs.

A prior architecture review said Datoviz v0.4 exposes text/glyph/mesh concepts, but Text/Glyph was
out of S023 scope because fonts, atlases, anchors, DPI, shaping, multiline text, fallback fonts, and
backend limitations need a dedicated design.

## Desired S024 scope

The user wants to continue with glyph/text because it unlocks plot annotation, labels, titles, axis
polish, and publication-style output.

Please recommend a stage that is narrow enough to implement safely. Assume the first practical goal
is a useful v1 text protocol and visual QA suite, not a complete typography engine.

## Design questions to answer

1. Should S024 define TextVisual only, GlyphVisual only, or both? If both, define their relationship
   and which one is public v1.
2. What fields should the v1 protocol expose? Please decide names and semantics for:
   - text/string storage;
   - positions and coordinate_space;
   - color/alpha;
   - font family/name or font role;
   - font size units;
   - horizontal/vertical alignment or anchor;
   - baseline handling;
   - rotation units and pivot;
   - per-item vs scalar style values;
   - z/layer/order;
   - multiline text;
   - Unicode/shaping/fallback limitations.
3. Should font sizes be screen pixels, typographic points, data units, or another protocol unit?
   Explain how Matplotlib and Datoviz should adapt.
4. Should angles be radians, degrees, or an enum-limited stage? Existing MarkerVisual uses radians;
   legacy text used degrees.
5. What font policy is safe and portable? Should v1 use a small generic family enum, a font role, an
   explicit family string, or server-resolved font handles? How should missing fonts report
   diagnostics?
6. Should glyph atlas generation be protocol-visible, a renderer-internal resource, or a future
   advanced resource? What if Datoviz requires explicit glyph/atlas data?
7. What text shaping scope is acceptable for v1? ASCII/Latin-1 only? Full Unicode strings with
   renderer-dependent fallback? Explicitly reject complex shaping? Diagnostic levels?
8. How should query/readback represent text hits or labels? Is text query support a capability bit?
9. How should guides (axis labels, tick labels, titles) relate to TextVisual? Should guides continue
   as semantic guides and optionally realize into internal text primitives, or should they emit public
   TextVisuals?
10. What visual QA cases are sufficient for v1: basic label, anchor grid, rotation, alpha/overlap,
    size/DPI, DATA vs NDC, multiline, Unicode smoke, guide-title integration?
11. What should be explicitly deferred: rich text, TeX/mathtext, bidirectional text, kerning control,
    font embedding, outline/stroke, text along path, SDF glyph cache, editing, layout engine, etc.?
12. What should Datoviz capability gates report if v0.4 text/glyph support is incomplete?

## Constraints

- Keep the v1 protocol backend-independent.
- Do not expose Datoviz attribute names as GSP fields unless they are semantically appropriate.
- Prefer a minimal accepted contract with explicit deferrals over an ambitious typography system.
- Preserve S023 style: deterministic validation, clear capability gates, Matplotlib reference first,
  Datoviz support or structured unsupported reports, visual QA contact sheets, manual review notes.
- Do not require network access, dynamic plugins, arbitrary font downloads, or executable font code.
- Avoid requiring JSON/base64 for normal in-process arrays or text lists.

## Expected output format

Please produce exactly this markdown structure:

# Consultation Result: S024 Text/Glyph Protocol Semantics

## Executive recommendation

A concise decision: TextVisual only, GlyphVisual only, or both; and the first implementable slice.

## Protocol contract draft

A concrete table of fields with names, types, scalar/per-item rules, validation, units, defaults,
and whether each field is required or optional.

## Enums and units

List accepted enum values and units for anchors/alignment, font family/role, rotation, size, and
coordinate behavior.

## Font and glyph atlas policy

Decide what is protocol-visible vs renderer-internal, plus diagnostics for missing fonts or
unsupported glyphs.

## Unicode, shaping, and multiline policy

State what v1 accepts, simplifies, rejects, or reports as unsupported.

## Guide relationship

Explain how AxisGuide/PanelTextGuide should interact with TextVisual/GlyphVisual.

## Backend mapping guidance

Separate subsections for Matplotlib and Datoviz v0.4, including capability gates and structured
unsupported diagnostics.

## Query/readback guidance

Recommended text query payloads and capability flags.

## Visual QA plan

List cases with expected purpose and manual review criteria.

## Deferred features

Explicit non-goals.

## ADR draft

Bullet-point ADR content suitable for an accepted decision record.

## Spec/task changes

List proposed new or updated spec files and mission-sized tasks.

## Risks and stop conditions

Risks, blockers, and conditions under which workers must stop rather than invent semantics.
```
