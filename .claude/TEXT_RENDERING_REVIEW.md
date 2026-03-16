# Text Rendering Alignment/Anchors Review

## Summary

The text rendering implementation has **critical bugs** in anchor/alignment handling that cause incorrect text positioning across backends. The issues are inconsistent between matplotlib and datoviz renderers.

---

## Issues Found

### 1. **CRITICAL: Inverted Vertical Anchor Mapping in Matplotlib**

**File:** `src/gsp_matplotlib/renderer/matplotlib_renderer_texts.py` (lines 138-141)

**Current Implementation:**
```python
ha_label = "center" if anchors_numpy[text_index, 0] == 0.0 else "right" if anchors_numpy[text_index, 0] == 1.0 else "left"
mpl_text.set_horizontalalignment(ha_label)
va_label = "center" if anchors_numpy[text_index, 1] == 0.0 else "top" if anchors_numpy[text_index, 1] == 1.0 else "bottom"
mpl_text.set_verticalalignment(va_label)
```

**The Problem:**
- **Vertical anchors are backwards**
- Current mapping: `1.0 = "top"`, `0.0 = "center"`, `-1.0 = "bottom"`
- Expected mapping: `-1.0 = "top"`, `0.0 = "center"`, `1.0 = "bottom"`
- This is evident in the example (lines 82-89 of `examples/texts_example.py`)

**Impact:**
- Text with vertical anchor `-1.0` (intended "top") appears at the bottom
- Text with vertical anchor `1.0` (intended "bottom") appears at the top
- This is visually incorrect and confusing

**Root Cause:**
The anchor values use a normalized coordinate system where:
- `-1.0` represents the negative direction (top/left in standard graphics)
- `0.0` represents the center
- `1.0` represents the positive direction (bottom/right in standard graphics)

But the renderer incorrectly assumes `1.0` means "top" for vertical alignment.

---

### 2. **MISSING: DataViz Renderer Completely Ignores Anchors**

**File:** `src/gsp_datoviz/renderer/datoviz_renderer_texts.py` (lines 73-80, 145-148)

**Current Implementation:**
```python
anchors_buffer = TransBufUtils.to_buffer(texts.get_anchors())
anchors_numpy = Bufferx.to_numpy(anchors_buffer)

# ... later, when rendering:

dvz_glyphs.set_strings(text_strings, string_pos=vertices_3d)
dvz_glyphs.set_color(glyph_colors)
dvz_glyphs.set_angle(glyphs_angles)
dvz_glyphs.set_scale(glyph_scales)
# NOTE: anchors_numpy is fetched but NEVER USED
```

**The Problem:**
- Anchors are loaded into `anchors_numpy` but never passed to the datoviz visual
- No `dvz_glyphs.set_anchor()` or equivalent call exists
- Text always renders with default anchor (likely top-left or center)
- This completely ignores user anchor specifications

**Impact:**
- DataViz text rendering doesn't respect anchor positioning
- All text uses a hardcoded anchor regardless of user input
- Inconsistent behavior between matplotlib and datoviz backends

---

### 3. **Semantic Inconsistency in Anchor Convention**

**Files:**
- Example: `examples/texts_example.py` (lines 82-89)
- Matplotlib Renderer: `src/gsp_matplotlib/renderer/matplotlib_renderer_texts.py` (lines 138-141)

**The Confusion:**
The anchor buffer uses normalized coordinates in the range `[-1, 1]`:
```
Horizontal: -1.0 (left), 0.0 (center), +1.0 (right)
Vertical:   -1.0 (top),  0.0 (center), +1.0 (bottom)
```

However, matplotlib's `ha`/`va` parameters use string labels:
```
ha: "left", "center", "right"
va: "top", "center", "bottom"
```

The current mapping logic tries to convert between these, but:
1. **Horizontal mapping works correctly (by accident):**
   - `-1.0` → falls into `else` case → `"left"` ✓
   - `0.0` → `"center"` ✓
   - `1.0` → `"right"` ✓

2. **Vertical mapping is inverted:**
   - `-1.0` → falls into `else` case → `"bottom"` ✗ (should be `"top"`)
   - `0.0` → `"center"` ✓
   - `1.0` → `"top"` ✗ (should be `"bottom"`)

---

## Visual Example

From `examples/texts_example.py`, texts with these anchors:

| Text    | Position | Anchor (x, y) | Expected Alignment | Current (Matplotlib) | DataViz      |
|---------|----------|---------------|-------------------|----------------------|--------------|
| Hello   | top      | (1.0, -1.0)   | right, top        | right, **bottom**    | (ignored)    |
| Hello   | center   | (1.0, 0.0)    | right, center     | right, center ✓      | (ignored)    |
| Hello   | bottom   | (1.0, 1.0)    | right, bottom     | right, **top**       | (ignored)    |

---

## Test Case

This simple test would reveal the bugs:

```python
import numpy as np
from gsp.visuals import Texts
from gsp.types import Buffer, BufferType
from gsp_matplotlib.extra.bufferx import Bufferx

# Create three text objects with different vertical anchors
positions = np.array([
    [0.0, 0.5, 0.0],   # top position
    [0.0, 0.0, 0.0],   # center position
    [0.0, -0.5, 0.0],  # bottom position
], dtype=np.float32)

anchors = np.array([
    [-1.0, -1.0],  # top-left (anchor at top-left of text box)
    [0.0, 0.0],    # center (anchor at center of text box)
    [1.0, 1.0],    # bottom-right (anchor at bottom-right of text box)
], dtype=np.float32)

# With correct implementation:
# Top text with anchor=-1.0 should align text TOP at y=0.5
# Center text with anchor=0.0 should align text CENTER at y=0.0
# Bottom text with anchor=1.0 should align text BOTTOM at y=-0.5

# With current buggy implementation:
# Top text appears BELOW y=0.5 (bottom-aligned)
# Bottom text appears ABOVE y=-0.5 (top-aligned)
```

---

## Recommended Fixes

### Fix 1: Correct Vertical Anchor Mapping in Matplotlib

**File:** `src/gsp_matplotlib/renderer/matplotlib_renderer_texts.py`

Replace lines 140-141 with proper mapping:

```python
va_label = "center" if anchors_numpy[text_index, 1] == 0.0 else "bottom" if anchors_numpy[text_index, 1] == 1.0 else "top"
mpl_text.set_verticalalignment(va_label)
```

Or more explicitly using a mapping dict for clarity:

```python
va_map = {
    -1.0: "top",
    0.0: "center",
    1.0: "bottom"
}
va_label = va_map.get(anchors_numpy[text_index, 1], "center")
mpl_text.set_verticalalignment(va_label)

ha_map = {
    -1.0: "left",
    0.0: "center",
    1.0: "right"
}
ha_label = ha_map.get(anchors_numpy[text_index, 0], "center")
mpl_text.set_horizontalalignment(ha_label)
```

### Fix 2: Implement Anchor Support in DataViz Renderer

**File:** `src/gsp_datoviz/renderer/datoviz_renderer_texts.py`

Need to investigate if datoviz's Glyph visual has anchor/alignment methods (e.g., `set_anchor()`, `set_alignment()`).

Then apply the anchors:

```python
# Option A: If datoviz supports per-glyph anchors
glyph_anchors = np.zeros((glyph_count, 2), dtype=np.float32)
for text_index in range(text_count):
    for glyph_index in range(len(text_strings[text_index])):
        global_glyph_index = sum(len(s) for s in text_strings[:text_index]) + glyph_index
        glyph_anchors[global_glyph_index, :] = anchors_numpy[text_index, :]
dvz_glyphs.set_anchor(glyph_anchors)

# Option B: If datoviz only supports per-string anchors
string_anchors = anchors_numpy  # Already per-string
dvz_glyphs.set_anchor(string_anchors)
```

If datoviz doesn't support anchors natively, alternative approaches:
1. Offset vertex positions manually to account for text dimensions
2. Document the limitation and disable anchor support for datoviz
3. Use a post-processing step to adjust glyph positions

---

## Files Affected

| File | Line(s) | Issue | Severity |
|------|---------|-------|----------|
| `src/gsp_matplotlib/renderer/matplotlib_renderer_texts.py` | 140-141 | Inverted vertical anchor | **CRITICAL** |
| `src/gsp_datoviz/renderer/datoviz_renderer_texts.py` | 73-80, 145-148 | Missing anchor implementation | **CRITICAL** |
| `examples/texts_example.py` | (works correctly - no changes) | (none) | N/A |

---

## Testing Recommendations

1. **Create unit tests** for text anchor mapping
2. **Visual regression tests** comparing rendered output against reference images
3. **Backend compatibility tests** ensuring both matplotlib and datoviz handle anchors identically
4. **Edge case tests** for unusual anchor values (outside [-1, 1])
5. **Integration tests** with rotation to ensure anchors work correctly with angles

---

## Additional Notes

- The `sanity_check_attributes()` method in `Texts` class (line 232) is empty and should validate anchor values
- Consider normalizing anchor values or clamping them to [-1, 1] range with warnings for invalid values
- Documentation should clearly specify the anchor coordinate system
- Consider adding type hints to clarify that anchors are normalized in [-1, 1]
