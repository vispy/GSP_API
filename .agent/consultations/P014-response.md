Design review for the Datoviz v0.4 explicit colorbar ticks API. 

## 1. **Recommendation**

Choose **Option B: add a dedicated `DvzColorbarTicks` struct** and add dynamic mutators:

```c
dvz_colorbar_set_ticks()
dvz_colorbar_clear_ticks()
```

Do **not** reuse `DvzAxisTicks` in the public colorbar API.

Rationale:

* Colorbar tick values are in **scale scalar-domain coordinates**, not panel data coordinates.
* `DvzAxisTicks` is semantically tied to axes. Reusing it would make the C API look accidental rather than intentional.
* The duplicated struct shape is small and stable.
* A dedicated struct leaves room for future colorbar-specific fields without contaminating axis semantics.
* It keeps the GSP-to-Datoviz mapping clean: GSP `ColorbarGuide.ticks` maps to Datoviz `DvzColorbarTicks.values`.
* It avoids putting dynamic rendering state into `DvzColorbarDesc`, which should remain mostly layout/creation configuration.

I would not introduce a generic `DvzTicks` abstraction in v0.4. That is broader than needed and risks becoming an underdesigned cross-guide abstraction.

---

## 2. **Exact Public API**

Add this to the public colorbar header.

```c
typedef struct DvzColorbarTicks DvzColorbarTicks;

/**
 * Explicit tick specification for a colorbar.
 *
 * Tick values are expressed in the scalar domain of the DvzScale associated
 * with the colorbar. They are not normalized [0, 1] positions and are not panel
 * data coordinates.
 *
 * If labels is NULL, labels are generated with the colorbar numeric formatter.
 * If labels is non-NULL, every label string is copied and rendered exactly,
 * subject to Datoviz text-rendering capabilities and maximum label length.
 */
struct DvzColorbarTicks
{
    /**
     * Size of this structure in bytes.
     *
     * Must be initialized to sizeof(DvzColorbarTicks), preferably by using
     * dvz_colorbar_ticks().
     */
    uint32_t struct_size;

    /**
     * Reserved for future use.
     *
     * Must be zero in Datoviz v0.4.
     */
    uint32_t flags;

    /**
     * Number of explicit ticks.
     *
     * May be zero. A zero-count explicit tick specification renders no ticks
     * until dvz_colorbar_clear_ticks() is called.
     */
    uint32_t count;

    /**
     * Scalar-domain tick values.
     *
     * Required when count > 0. All values must be finite.
     */
    const double* values;

    /**
     * Optional explicit tick labels.
     *
     * If NULL, Datoviz formats tick labels numerically. If non-NULL, this must
     * point to count non-NULL C strings. Empty strings are allowed. Labels are
     * copied by dvz_colorbar_set_ticks().
     */
    const char* const* labels;
};

/**
 * Return a default-initialized explicit colorbar tick descriptor.
 *
 * The returned structure has struct_size set correctly, flags set to zero,
 * count set to zero, and values/labels set to NULL.
 */
DVZ_EXPORT DvzColorbarTicks dvz_colorbar_ticks(void);

/**
 * Set explicit ticks on a colorbar.
 *
 * The tick values are copied immediately. If labels is non-NULL, all labels are
 * also copied immediately. The caller may release the input arrays and strings
 * after this function returns.
 *
 * Passing a valid descriptor with count == 0 enables explicit empty ticks:
 * the colorbar renders no tick marks and no tick labels until
 * dvz_colorbar_clear_ticks() is called.
 *
 * Returns true on success. Returns false and leaves the previous colorbar tick
 * state unchanged if validation fails.
 */
DVZ_EXPORT bool dvz_colorbar_set_ticks(
    DvzColorbar* colorbar, const DvzColorbarTicks* ticks);

/**
 * Clear explicit ticks on a colorbar.
 *
 * After this call, the colorbar returns to automatic native tick generation.
 *
 * Returns true on success and false if colorbar is NULL.
 */
DVZ_EXPORT bool dvz_colorbar_clear_ticks(DvzColorbar* colorbar);
```

I recommend adding `dvz_colorbar_ticks()` even if `DvzAxisTicks` currently lacks an equivalent helper. For ABI-prologue structs, an initializer function avoids many Python/C user mistakes.

---

## 3. **Semantics**

### Validation

`dvz_colorbar_set_ticks()` should validate all inputs before mutating the colorbar.

Return `false` and leave the previous state unchanged if any rule fails:

```c
colorbar != NULL
ticks != NULL
ticks->struct_size >= required v0.4 size
ticks->flags == 0
ticks->count <= DVZ_SCENE_MAX_COLORBAR_TICKS
ticks->count == 0 || ticks->values != NULL
all ticks->values[i] are finite
if ticks->labels != NULL, all ticks->labels[i] are non-NULL
if labels are provided, strlen(labels[i]) < DVZ_SCENE_LABEL_SIZE
```

Empty labels should be accepted:

```c
labels[i] = "";
```

Null individual labels should be rejected rather than treated as formatter fallback. This keeps the invariant simple:

* `labels == NULL`: use numeric formatter.
* `labels != NULL`: use exactly the provided labels.

### Copying and lifetime

`dvz_colorbar_set_ticks()` should copy:

* all `double` tick values;
* all label strings, if labels are provided.

The input arrays and strings must not be retained by pointer.

### Empty explicit tick set

This should be valid:

```c
DvzColorbarTicks ticks = dvz_colorbar_ticks();
ticks.count = 0;
ticks.values = NULL;
ticks.labels = NULL;
dvz_colorbar_set_ticks(colorbar, &ticks);
```

Meaning:

* explicit tick mode is enabled;
* no tick marks are rendered;
* no tick labels are rendered;
* automatic ticks remain disabled;
* `dvz_colorbar_clear_ticks(colorbar)` restores automatic ticks.

This distinction is useful for GSP because “explicitly no ticks” and “backend decides ticks automatically” are semantically different.

### Label formatting

Rules:

* If explicit labels are supplied, render them exactly.
* Do not apply `DvzFormatDesc`.
* Do not append units, prefixes, suffixes, scientific notation, or trimming.
* `dvz_colorbar_set_format()` should not alter explicit labels.
* If explicit tick values are supplied without labels, use the current colorbar formatter.
* If no colorbar-specific formatter exists, continue falling back to the scale formatter as today.
* If format changes after explicit tick values were set without labels, tick labels should update.
* If format changes after explicit labels were set, tick labels should remain unchanged.

So:

```c
values + labels     -> positions explicit, labels exact
values + NULL labels -> positions explicit, labels formatted by Datoviz
clear_ticks          -> positions automatic, labels formatted by Datoviz
```

### Out-of-domain ticks

Accept finite out-of-domain explicit ticks and render them with the existing colorbar value normalization behavior, i.e. **clipped to the colorbar endpoints**.

Do not reject them during `dvz_colorbar_set_ticks()`.

Reasons:

* Validation should not depend on the current dynamic scale domain.
* A tick outside the domain today may become in-domain after a scale update.
* It is consistent with the proposed GSP allowance.
* It avoids surprising failures during interactive rescaling.
* It preserves a simple rule: finite scalar-domain values are accepted.

Document the consequence clearly:

* values below the current scale minimum render at the low endpoint;
* values above the current scale maximum render at the high endpoint;
* overlapping ticks/labels are caller responsibility;
* Datoviz does not perform tick collision avoidance in this API.

### Clearing behavior

`dvz_colorbar_clear_ticks()` should:

* disable explicit tick mode;
* clear explicit label state;
* restore automatic tick generation;
* mark the colorbar dirty;
* request a frame/update;
* return `false` only for invalid input, primarily `colorbar == NULL`.

### Dynamic update behavior

After successful `dvz_colorbar_set_ticks()` or `dvz_colorbar_clear_ticks()`:

* mark colorbar tick geometry dirty;
* mark colorbar text dirty;
* request a redraw/frame;
* keep title/layout/format state unchanged.

Scale updates should continue to affect tick positions because explicit values are scalar-domain values normalized against the current scale domain.

---

## 4. **Internal Implementation Plan**

Add fields to `DvzColorbar`:

```c
bool explicit_ticks_enabled;
bool explicit_tick_labels_set;

uint32_t explicit_tick_count;
double explicit_ticks[DVZ_SCENE_MAX_COLORBAR_TICKS];
char explicit_tick_labels[DVZ_SCENE_MAX_COLORBAR_TICKS][DVZ_SCENE_LABEL_SIZE];
```

Keep the existing resolved fields:

```c
uint32_t tick_count;
double ticks[DVZ_SCENE_MAX_COLORBAR_TICKS];
```

Use them as the currently rendered tick values, whether automatic or explicit.

Add a resolver:

```c
static void _colorbar_resolve_ticks(DvzColorbar* colorbar, double min, double max)
{
    colorbar->tick_count = 0;

    if (!isfinite(min) || !isfinite(max) || !(max > min))
        return;

    if (colorbar->explicit_ticks_enabled)
    {
        colorbar->tick_count = colorbar->explicit_tick_count;
        memcpy(
            colorbar->ticks,
            colorbar->explicit_ticks,
            colorbar->tick_count * sizeof(double));
        return;
    }

    _colorbar_compute_ticks(colorbar, min, max);
}
```

Then replace direct calls to `_colorbar_compute_ticks()` with `_colorbar_resolve_ticks()`.

Modify `_colorbar_update_ticks_and_text()`:

```c
const bool use_explicit_labels =
    colorbar->explicit_ticks_enabled && colorbar->explicit_tick_labels_set;

for (uint32_t i = 0; i < colorbar->tick_count; i++)
{
    double value = colorbar->ticks[i];

    // Existing behavior:
    // compute normalized/clipped colorbar position from value and scale min/max.

    char label[DVZ_SCENE_LABEL_SIZE] = {0};

    if (use_explicit_labels)
    {
        snprintf(label, sizeof(label), "%s", colorbar->explicit_tick_labels[i]);
    }
    else
    {
        _colorbar_format_tick(colorbar, value, label, sizeof(label));
    }

    _colorbar_append_text(colorbar, label, ...);
}
```

Add public setters:

```c
DvzColorbarTicks dvz_colorbar_ticks(void)
{
    DvzColorbarTicks ticks = {0};
    ticks.struct_size = sizeof(DvzColorbarTicks);
    return ticks;
}
```

`dvz_colorbar_set_ticks()` should validate into temporaries first:

```c
double values[DVZ_SCENE_MAX_COLORBAR_TICKS];
char labels[DVZ_SCENE_MAX_COLORBAR_TICKS][DVZ_SCENE_LABEL_SIZE];
```

Only after validation succeeds should it mutate `colorbar`.

This avoids partial state updates on failure.

Suggested mutation logic:

```c
colorbar->explicit_ticks_enabled = true;
colorbar->explicit_tick_count = ticks->count;
memcpy(colorbar->explicit_ticks, values, ticks->count * sizeof(double));

colorbar->explicit_tick_labels_set = ticks->labels != NULL;
if (ticks->labels != NULL)
    copy labels;
else
    clear label storage;
```

`dvz_colorbar_clear_ticks()`:

```c
colorbar->explicit_ticks_enabled = false;
colorbar->explicit_tick_labels_set = false;
colorbar->explicit_tick_count = 0;
memset(colorbar->explicit_ticks, 0, sizeof(colorbar->explicit_ticks));
memset(colorbar->explicit_tick_labels, 0, sizeof(colorbar->explicit_tick_labels));
mark dirty;
request frame;
```

Do not sort, deduplicate, or silently drop explicit ticks. Preserve caller order.

---

## 5. **Test Plan**

### C API tests

Add tests covering at least the following.

#### 1. Explicit values, no labels

Create a colorbar with scale domain `[0, 1]`.

Set:

```c
values = {0.0, 0.5, 1.0}
labels = NULL
```

Assert:

* call returns `true`;
* explicit mode is enabled internally;
* resolved `tick_count == 3`;
* resolved tick values are exactly `{0.0, 0.5, 1.0}`;
* tick geometry/text work is emitted;
* labels use the active numeric formatter.

#### 2. Explicit values with explicit labels

Set:

```c
values = {0.0, 0.5, 1.0}
labels = {"low", "mid", "high"}
```

Assert:

* labels are copied;
* rendered text uses `"low"`, `"mid"`, `"high"`;
* numeric formatter is not used for those labels.

#### 3. Format interaction

Set explicit values without labels.

Then call:

```c
dvz_colorbar_set_format(colorbar, &format);
```

Assert labels update according to the new formatter.

Then set explicit values with labels and change the format again.

Assert explicit labels remain unchanged.

#### 4. Clear restores automatic ticks

Set explicit ticks.

Then call:

```c
dvz_colorbar_clear_ticks(colorbar);
```

Assert:

* explicit mode is disabled;
* automatic tick generation runs again;
* automatic tick count and values are consistent with existing native behavior.

#### 5. Explicit empty ticks

Set:

```c
count = 0;
values = NULL;
labels = NULL;
```

Assert:

* call returns `true`;
* explicit mode is enabled;
* no tick marks are emitted;
* no tick labels are emitted;
* title and ramp still render;
* `clear_ticks()` restores automatic ticks.

#### 6. Validation failures leave state unchanged

Start from a known valid explicit tick state.

Then verify failure and unchanged state for:

```c
ticks == NULL
bad struct_size
flags != 0
count > DVZ_SCENE_MAX_COLORBAR_TICKS
count > 0 && values == NULL
values[i] = NAN
values[i] = INFINITY
labels != NULL && labels[i] == NULL
label too long
```

#### 7. Out-of-domain clipping

With scale domain `[0, 1]`, set:

```c
values = {-1.0, 0.5, 2.0}
labels = {"under", "mid", "over"}
```

Assert:

* call returns `true`;
* labels are preserved;
* rendered positions are clipped to low endpoint, midpoint, and high endpoint.

#### 8. Dynamic scale update

Set explicit ticks once.

Then change the scale domain.

Assert:

* explicit tick values remain stored unchanged;
* rendered positions are recomputed from the new domain;
* no automatic tick generation replaces them.

#### 9. Orientation coverage

Run explicit tick rendering for both:

```c
DVZ_COLORBAR_ORIENTATION_VERTICAL
DVZ_COLORBAR_ORIENTATION_HORIZONTAL
```

Assert no layout regression and expected tick/text work emission.

#### 10. Destroy path

Set explicit ticks and labels, then destroy the colorbar.

Assert no leak, no dangling pointer, no use-after-free. Since values and labels are copied into fixed storage, this should be straightforward.

### Python binding smoke tests

Add minimal generated-binding tests:

```python
cb.set_ticks([0.0, 0.5, 1.0])
cb.clear_ticks()
```

and:

```python
cb.set_ticks([0.0, 0.5, 1.0], labels=["low", "mid", "high"])
```

Also test:

```python
cb.set_ticks(np.array([0.0, 0.5, 1.0], dtype=np.float64))
```

Validation smoke tests:

```python
cb.set_ticks([0.0, float("nan")])  # should fail or raise
cb.set_ticks([0.0, 1.0], labels=["only one"])  # should fail or raise
cb.set_ticks([0.0, 1.0], labels=None)  # valid
```

The Python wrapper should preferably raise `ValueError` before calling C for obvious shape/count/finite errors, while still preserving the C API’s `bool` result.

---

## 6. **GSP Integration Notes**

After this lands, GSP may claim strict Datoviz support for:

* `ColorbarGuide.ticks` as scalar-domain tick values;
* explicit tick positions for continuous scalar scales;
* explicit `tick_labels` passed through exactly, within Datoviz label-length limits;
* vertical and horizontal colorbars, assuming existing Datoviz layout/anchor mapping can represent the requested placement;
* dynamic updates to colorbar tick state.

GSP should **not** claim Matplotlib-identical formatting when `tick_labels` is absent.

In that case:

* tick positions may be strict;
* generated numeric labels are Datoviz-native;
* formatting parity depends on `DvzFormatDesc`, not Matplotlib.

GSP should treat these as capability limits:

```text
max tick count: DVZ_SCENE_MAX_COLORBAR_TICKS
max label length: DVZ_SCENE_LABEL_SIZE - 1 bytes
label encoding/rendering: Datoviz text renderer dependent
out-of-domain ticks: accepted and clipped
collision avoidance: not guaranteed
```

For datetime-like, categorical, or unit-rich labels, GSP should supply explicit `tick_labels` if it needs exact parity.

The Datoviz API should remain numeric at the position level:

```text
double scalar value -> colorbar position
string label        -> rendered text
```

That is sufficient for GSP colorbar guides without exposing Datoviz internals.

---

## 7. **Risks/Open Questions**

### Duplicate tick structs

`DvzColorbarTicks` duplicates `DvzAxisTicks`.

That is acceptable. The semantic clarity is worth the tiny duplication. The implementation and Python generator can still share marshalling code internally.

### Naming risk

The docs must repeatedly state:

```text
Colorbar tick values are scale-domain values.
Axis tick values are panel data coordinates.
```

Otherwise users may incorrectly assume colorbar values are normalized positions.

### Out-of-domain clipping

Clipping is pragmatic but can produce overlapping endpoint labels:

```text
-1.0, 0.0 -> both at low endpoint
1.0, 2.0 -> both at high endpoint
```

This should be documented as caller responsibility. Do not add collision resolution in this API.

### Label exactness versus fixed storage

If Datoviz uses fixed-size label buffers, silent truncation would violate GSP strictness.

Prefer rejecting overlong labels with `false`.

If existing Datoviz text APIs already truncate silently, this is a consistency decision. For GSP strict parity, the backend should expose failure rather than silently degrade.

### Datetime and categorical scales

Do not add special datetime or categorical fields to this API.

The stable v0.4 contract should be:

```text
positions are double scalar values;
labels are optional exact strings.
```

Datetime/categorical parity should be achieved by explicit labels supplied by GSP.

### Future colorbar features

This design does not block future additions such as:

* minor ticks;
* tick side;
* label rotation;
* tick visibility flags;
* under/over extensions;
* logarithmic scale-aware formatting;
* collision avoidance;
* guide-level style options.

Those should not be added now.

The minimal stable v0.4 API should be:

```c
DvzColorbarTicks dvz_colorbar_ticks(void);
bool dvz_colorbar_set_ticks(DvzColorbar* colorbar, const DvzColorbarTicks* ticks);
bool dvz_colorbar_clear_ticks(DvzColorbar* colorbar);
```

That gives GSP the necessary explicit tick/label parity without broadening the public Datoviz abstraction surface.

