# P014 - Datoviz Colorbar Explicit Ticks API Consultation

Status: awaiting ChatGPT Pro response.

This needs ChatGPT Pro consultation.

## Exact Prompt For ChatGPT Pro

You are reviewing a Datoviz v0.4 public C API design decision. This prompt is self-contained; do not
assume repository access or file attachments.

We maintain two related projects:

- Datoviz v0.4: a retained-scene GPU visualization engine with a public C API and generated Python
  ctypes facade.
- GSP_API: a semantic visualization protocol that targets Matplotlib as the reference backend and
  Datoviz v0.4 as the flagship GPU backend. GSP must not expose Datoviz-specific handles, shader
  names, visual slot names, or private structs.

The current issue: GSP has semantic `ColorbarGuide` objects with explicit scalar-domain tick values
and optional explicit tick labels. Matplotlib can render these exactly. Datoviz v0.4 currently
renders native colorbars with automatic numeric ticks, but there is no public API for explicit
colorbar tick values/labels. We need to add a Datoviz API that is consistent with the rest of the
Datoviz v0.4 scene API.

## GSP colorbar semantics that Datoviz should support

GSP `ColorbarGuide` fields:

- `id`: protocol id.
- `panel_id`: panel id.
- `color_scale_id`: associated semantic color scale id.
- `linked_visual_ids`: visual ids using the same scale.
- `orientation`: `"vertical"` or `"horizontal"`, default vertical.
- `placement`: `"right"`, `"left"`, `"bottom"`, or `"top"`.
- `label`: colorbar title/label string.
- `ticks`: finite scalar-domain tick values, optional.
- `tick_labels`: optional explicit strings, same length as `ticks`; when present, labels must pass
  through exactly.

Important semantics:

- Tick values are scalar-domain values, not normalized [0, 1] positions.
- Explicit tick labels must pass through exactly.
- If explicit tick values are supplied without labels, Datoviz may use its numeric formatter.
- If explicit ticks are absent, Datoviz may use automatic native tick generation.
- Colorbars are semantic guides, not data visuals.
- Query/readback can remain separately capability-gated; this consultation is only about rendering
  explicit ticks/labels and public API consistency.

## Current Datoviz public API surface

Datoviz already has these public types/functions:

```c
typedef struct DvzColorbar DvzColorbar;
typedef struct DvzScale DvzScale;

typedef enum
{
    DVZ_COLORBAR_ORIENTATION_VERTICAL = 0,
    DVZ_COLORBAR_ORIENTATION_HORIZONTAL,
} DvzColorbarOrientation;

typedef enum
{
    DVZ_COLORBAR_PLACEMENT_ATTACHED = 0,
    DVZ_COLORBAR_PLACEMENT_DETACHED,
} DvzColorbarPlacementMode;

struct DvzColorbarDesc
{
    uint32_t struct_size;
    uint32_t flags;
    DvzColorbarPlacementMode placement_mode;
    DvzColorbarOrientation orientation;
    DvzSceneAnchor anchor;
    const char* title;
    float reserve_px;
    float ramp_width_px;
    float edge_offset_px;
    float plot_gap_px;
    float tick_length_px;
    float label_gap_px;
    DvzTextRenderer text_renderer;
    DvzPlacement placement;
    uint32_t colorbar_flags;
};
typedef struct DvzColorbarDesc DvzColorbarDesc;

DVZ_EXPORT DvzColorbarDesc dvz_colorbar_desc(void);
DVZ_EXPORT DvzColorbar* dvz_colorbar(
    DvzPanel* panel, DvzScale* scale, const DvzColorbarDesc* desc);
DVZ_EXPORT DvzId dvz_colorbar_id(const DvzColorbar* colorbar);
DVZ_EXPORT void dvz_colorbar_destroy(DvzColorbar* colorbar);
DVZ_EXPORT void dvz_colorbar_set_format(
    DvzColorbar* colorbar, const DvzFormatDesc* format);
DVZ_EXPORT void dvz_colorbar_set_orientation(
    DvzColorbar* colorbar, DvzColorbarOrientation orientation);
DVZ_EXPORT bool dvz_colorbar_set_anchor(DvzColorbar* colorbar, DvzSceneAnchor anchor);
DVZ_EXPORT bool dvz_colorbar_set_layout(DvzColorbar* colorbar, const DvzColorbarDesc* desc);
DVZ_EXPORT void dvz_colorbar_set_title(DvzColorbar* colorbar, const char* title);
```

Datoviz also already has this public axis tick API:

```c
struct DvzAxisTicks
{
    uint32_t struct_size;
    uint32_t flags;
    uint32_t count;
    const double* values;
    const char* const* labels;
};
typedef struct DvzAxisTicks DvzAxisTicks;

DVZ_EXPORT bool dvz_axis_set_ticks(DvzAxis* axis, const DvzAxisTicks* ticks);
DVZ_EXPORT bool dvz_axis_clear_ticks(DvzAxis* axis);
```

For axes, explicit tick values are in panel data coordinates and labels are optional copied strings.

## Current Datoviz internal colorbar implementation

The internal colorbar implementation already has:

- automatic tick generation into `colorbar->tick_count` and `colorbar->ticks[]`;
- tick segment rendering;
- text label rendering through a batched text visual;
- numeric formatting via `DvzFormatDesc`;
- title rendering.

Relevant simplified internal behavior:

```c
static void _colorbar_compute_ticks(DvzColorbar* colorbar, double min, double max)
{
    colorbar->tick_count = 0;
    if (!isfinite(min) || !isfinite(max) || !(max > min))
        return;
    double step = _colorbar_nice_number((max - min) / 4.0, true);
    if (!(step > 0.0) || !isfinite(step))
        return;
    colorbar->ticks[colorbar->tick_count++] = min;
    double first = ceil(min / step) * step;
    for (double value = first; value < max - 0.5 * COLORBAR_EPS; value += step)
    {
        if (value <= min + 0.5 * COLORBAR_EPS)
            continue;
        if (colorbar->tick_count + 1 >= DVZ_SCENE_MAX_COLORBAR_TICKS)
            break;
        colorbar->ticks[colorbar->tick_count++] = value;
    }
    if (colorbar->tick_count < DVZ_SCENE_MAX_COLORBAR_TICKS)
        colorbar->ticks[colorbar->tick_count++] = max;
}

static void _colorbar_format_tick(
    const DvzColorbar* colorbar, double value, char* out, uint32_t out_size)
{
    const DvzSceneFormatState* format =
        colorbar->has_format ? &colorbar->format : &colorbar->scale->format;
    // formats value into out using precision/scientific/trim/unit/prefix/suffix
}

static void _colorbar_update_ticks_and_text(...)
{
    for (uint32_t i = 0; i < colorbar->tick_count; i++)
    {
        double value = colorbar->ticks[i];
        // draw tick mark at normalized position for value in scale min/max
        char label[DVZ_SCENE_LABEL_SIZE] = {0};
        _colorbar_format_tick(colorbar, value, label, sizeof(label));
        _colorbar_append_text(colorbar, label, ...);
    }
}
```

Current Datoviz C tests already verify automatic colorbar ticks, colorbar layout, colorbar title,
format updates, emitted ramp/tick/glyph work, and invalid layout requests. They do not verify
explicit colorbar tick values/labels because no public API exists.

## Candidate API choices

We need advice on the best Datoviz API design. Options include:

Option A: reuse `DvzAxisTicks`:

```c
DVZ_EXPORT bool dvz_colorbar_set_ticks(DvzColorbar* colorbar, const DvzAxisTicks* ticks);
DVZ_EXPORT bool dvz_colorbar_clear_ticks(DvzColorbar* colorbar);
```

Pros: consistent shape with axes; generated Python binding already knows `DvzAxisTicks`.
Cons: type name says “Axis” even though colorbar ticks are scalar scale-domain values, not panel data
coordinates.

Option B: add a dedicated alias/struct:

```c
struct DvzColorbarTicks
{
    uint32_t struct_size;
    uint32_t flags;
    uint32_t count;
    const double* values;
    const char* const* labels;
};
typedef struct DvzColorbarTicks DvzColorbarTicks;

DVZ_EXPORT bool dvz_colorbar_set_ticks(DvzColorbar* colorbar, const DvzColorbarTicks* ticks);
DVZ_EXPORT bool dvz_colorbar_clear_ticks(DvzColorbar* colorbar);
```

Pros: semantically precise and future-proof. Cons: duplicate struct shape, new binding type.

Option C: put optional tick pointer fields into `DvzColorbarDesc`.

Pros: one-call creation. Cons: descriptor becomes mixed layout + dynamic state; less consistent with
existing `dvz_colorbar_set_title`, `dvz_colorbar_set_format`, `dvz_colorbar_set_layout` mutators.

## Proposed internal behavior

Likely implementation:

- Add internal fields to `DvzColorbar`:
  - `bool explicit_ticks_enabled;`
  - `bool explicit_tick_labels_set;`
  - `uint32_t explicit_tick_count;`
  - `double explicit_ticks[DVZ_SCENE_MAX_COLORBAR_TICKS];`
  - `char explicit_tick_labels[DVZ_SCENE_MAX_COLORBAR_TICKS][DVZ_SCENE_LABEL_SIZE];`
- Validate:
  - `ticks != NULL` for set;
  - ABI prologue valid;
  - `count <= DVZ_SCENE_MAX_COLORBAR_TICKS`;
  - if `count > 0`, `values != NULL`;
  - all values finite;
  - if labels pointer is non-null, copy each non-null label into fixed storage;
  - empty count is valid and renders no ticks/labels until cleared.
- On set:
  - copy values/labels;
  - mark dirty and request frame.
- On clear:
  - disable explicit ticks;
  - restore automatic tick generation.
- In `_colorbar_compute_ticks` or a new resolver:
  - use explicit ticks when enabled;
  - otherwise compute automatic ticks.
- In `_colorbar_update_ticks_and_text`:
  - if explicit labels are set, use copied label exactly;
  - otherwise use numeric formatter.
- Tick positions outside the current scale domain should probably be clipped to endpoints by the
  existing `_colorbar_value_t()` behavior, unless Datoviz should reject out-of-domain ticks. GSP
  permits explicit tick values outside range to render at clipped endpoints unless the backend
  rejects with diagnostic.

## Questions for ChatGPT Pro

Please evaluate this API addition in the context of a coherent Datoviz v0.4 public C API.

1. Should Datoviz reuse `DvzAxisTicks` for colorbars, define `DvzColorbarTicks`, or use a different
   design?
2. Should explicit colorbar ticks be dynamic mutator state (`dvz_colorbar_set_ticks`) or part of
   `DvzColorbarDesc`?
3. What exact C API should be added, including function names, return types, validation behavior,
   and documentation comments?
4. What internal state and algorithm changes should be made?
5. Should out-of-domain explicit ticks be accepted and clipped, accepted but hidden, or rejected?
6. How should explicit labels interact with `DvzFormatDesc`?
7. What Python ctypes/generator implications should be considered?
8. What Datoviz tests should be added before GSP relies on this for strict colorbar parity?
9. Are there naming or semantic consistency risks with axis ticks, scale units, datetime formatting,
   categorical scales, legends, or future colorbar features?

## Expected Output Format

Return a concise design review with these sections:

1. **Recommendation**
   - Choose one API design and state why.

2. **Exact Public API**
   - Provide C typedef/function prototypes and Doxygen-style comments.

3. **Semantics**
   - Validation rules, label formatting rules, out-of-domain behavior, clearing behavior, and dynamic
     update behavior.

4. **Internal Implementation Plan**
   - Specific fields and functions to add/change.

5. **Test Plan**
   - Specific C tests and Python binding smoke tests.

6. **GSP Integration Notes**
   - What GSP may claim as strict after this lands, and what remains adapted/unsupported.

7. **Risks/Open Questions**
   - Any unresolved tradeoffs or compatibility concerns.

Please be direct and specific. Prefer a small stable v0.4 API over a broad generic abstraction.

