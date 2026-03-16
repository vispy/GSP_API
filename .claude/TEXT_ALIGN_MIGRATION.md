# TextAlign Migration Guide

## Overview

This guide shows how to update the text rendering implementations to use the new `TextAlign` type, fixing the anchor/alignment bugs in the process.

---

## Step 1: Update Matplotlib Renderer

**File:** `src/gsp_matplotlib/renderer/matplotlib_renderer_texts.py`

### Current Code (Buggy)

```python
# Lines 138-141 - INCORRECT VERTICAL MAPPING
ha_label = "center" if anchors_numpy[text_index, 0] == 0.0 else "right" if anchors_numpy[text_index, 0] == 1.0 else "left"
mpl_text.set_horizontalalignment(ha_label)
va_label = "center" if anchors_numpy[text_index, 1] == 0.0 else "top" if anchors_numpy[text_index, 1] == 1.0 else "bottom"
mpl_text.set_verticalalignment(va_label)
```

### Updated Code (Fixed with TextAlign)

```python
# Add import at the top
from gsp.types import TextAlign

# Replace lines 138-141 with:
anchor_x = anchors_numpy[text_index, 0]
anchor_y = anchors_numpy[text_index, 1]
align = TextAlign.from_anchor_coordinates(anchor_x, anchor_y)
ha_label, va_label = align.to_matplotlib_alignment()
mpl_text.set_horizontalalignment(ha_label)
mpl_text.set_verticalalignment(va_label)
```

### Why This is Better

1. **Correctness**: Properly maps anchor coordinates to alignment
2. **Maintainability**: Intent is clear; easy to understand
3. **Type Safety**: IDE can help catch errors
4. **Reusability**: Same conversion logic can be used elsewhere

---

## Step 2: Update DataViz Renderer

**File:** `src/gsp_datoviz/renderer/datoviz_renderer_texts.py`

### Current Code (Incomplete)

```python
# Lines 73-80: Load anchors but never use them
colors_buffer = TransBufUtils.to_buffer(texts.get_colors())
font_sizes_buffer = TransBufUtils.to_buffer(texts.get_font_sizes())
anchors_buffer = TransBufUtils.to_buffer(texts.get_anchors())  # ← Loaded but unused!
angles_buffer = TransBufUtils.to_buffer(texts.get_angles())

colors_numpy = Bufferx.to_numpy(colors_buffer)
font_sizes_numpy = Bufferx.to_numpy(font_sizes_buffer)
anchors_numpy = Bufferx.to_numpy(anchors_buffer)  # ← Loaded but unused!
angles_numpy = Bufferx.to_numpy(angles_buffer)

# ... later at lines 145-148:
dvz_glyphs.set_strings(text_strings, string_pos=vertices_3d)
dvz_glyphs.set_color(glyph_colors)
dvz_glyphs.set_angle(glyphs_angles)
dvz_glyphs.set_scale(glyph_scales)
# NOTE: No anchor/alignment handling!
```

### Updated Code (Option A: If DataViz supports per-string anchors)

```python
# Add import at the top
from gsp.types import TextAlign

# Keep lines 73-80 as-is (anchors are loaded)

# After line 148, add anchor handling:
# Convert anchors to TextAlign values (if datoviz supports it)
text_aligns = np.zeros((text_count,), dtype=np.int32)
for text_index in range(text_count):
    anchor_x = anchors_numpy[text_index, 0]
    anchor_y = anchors_numpy[text_index, 1]
    align = TextAlign.from_anchor_coordinates(anchor_x, anchor_y)
    text_aligns[text_index] = int(align.value)

# Apply alignment to datoviz visual (if method exists)
if hasattr(dvz_glyphs, 'set_text_align'):
    dvz_glyphs.set_text_align(text_aligns)
```

### Updated Code (Option B: Per-glyph anchors)

```python
# Add import at the top
from gsp.types import TextAlign

# Keep lines 73-80 as-is

# Build per-glyph alignments from per-string alignments
glyph_aligns = np.zeros((glyph_count,), dtype=np.int32)
for text_index in range(text_count):
    anchor_x = anchors_numpy[text_index, 0]
    anchor_y = anchors_numpy[text_index, 1]
    align = TextAlign.from_anchor_coordinates(anchor_x, anchor_y)

    for glyph_index in range(len(text_strings[text_index])):
        global_glyph_index = sum(len(s) for s in text_strings[:text_index]) + glyph_index
        glyph_aligns[global_glyph_index] = int(align.value)

# Apply alignment (if method exists)
if hasattr(dvz_glyphs, 'set_text_align'):
    dvz_glyphs.set_text_align(glyph_aligns)
```

### Updated Code (Option C: Manual position offset - Fallback)

```python
# If datoviz doesn't support alignment, manually adjust vertex positions
# This requires estimating text bounding boxes

from gsp.types import TextAlign

# After getting text sizes, adjust positions
for text_index in range(text_count):
    anchor_x = anchors_numpy[text_index, 0]
    anchor_y = anchors_numpy[text_index, 1]
    align = TextAlign.from_anchor_coordinates(anchor_x, anchor_y)

    # Estimate text width/height (this varies by font/size)
    # For now, use a simple heuristic
    text_width_estimate = len(text_strings[text_index]) * font_sizes_numpy[text_index, 0] * 0.6
    text_height_estimate = font_sizes_numpy[text_index, 0]

    # Adjust vertex position based on alignment
    v, h = align.to_components()
    offset_x = 0.0
    offset_y = 0.0

    # Horizontal offset
    if h.value == 1:  # CENTER
        offset_x = -text_width_estimate / 2.0
    elif h.value == 2:  # RIGHT
        offset_x = -text_width_estimate

    # Vertical offset
    if v.value == 1:  # CENTER
        offset_y = -text_height_estimate / 2.0
    elif v.value == 2:  # BOTTOM
        offset_y = -text_height_estimate

    vertices_3d[text_index, 0] += offset_x
    vertices_3d[text_index, 1] += offset_y
```

---

## Step 3: Update Example Code (Optional)

**File:** `examples/texts_example.py`

### Current Code

```python
# Lines 82-89: Manual anchor specification
if vertical_alignment == "top":
    anchors_numpy = np.array([[+1.0, -1.0], [+1.0, -1.0], [0.0, -1.0], [0.0, -1.0], [-1.0, -1.0], [-1.0, -1.0]], dtype=np.float32)
elif vertical_alignment == "center":
    anchors_numpy = np.array([[+1.0, +0.0], [+1.0, +0.0], [0.0, +0.0], [0.0, +0.0], [-1.0, +0.0], [-1.0, +0.0]], dtype=np.float32)
elif vertical_alignment == "bottom":
    anchors_numpy = np.array([[+1.0, +1.0], [+1.0, +1.0], [0.0, +1.0], [0.0, +1.0], [-1.0, +1.0], [-1.0, +1.0]], dtype=np.float32)
```

### Updated Code (More Readable)

```python
from gsp.types import TextAlign

if vertical_alignment == "top":
    aligns = [
        TextAlign.TOP_RIGHT, TextAlign.TOP_RIGHT,
        TextAlign.TOP_CENTER, TextAlign.TOP_CENTER,
        TextAlign.TOP_LEFT, TextAlign.TOP_LEFT,
    ]
elif vertical_alignment == "center":
    aligns = [
        TextAlign.CENTER_RIGHT, TextAlign.CENTER_RIGHT,
        TextAlign.CENTER_CENTER, TextAlign.CENTER_CENTER,
        TextAlign.CENTER_LEFT, TextAlign.CENTER_LEFT,
    ]
elif vertical_alignment == "bottom":
    aligns = [
        TextAlign.BOTTOM_RIGHT, TextAlign.BOTTOM_RIGHT,
        TextAlign.BOTTOM_CENTER, TextAlign.BOTTOM_CENTER,
        TextAlign.BOTTOM_LEFT, TextAlign.BOTTOM_LEFT,
    ]

anchors_numpy = np.array([align.to_anchor_coordinates() for align in aligns], dtype=np.float32)
```

---

## Step 4: Add Type Hints to Texts Visual

**File:** `src/gsp/visuals/texts.py`

### Optional: Add TextAlign Support

```python
from gsp.types import TextAlign

class Texts(VisualBase):
    """Texts visual."""

    # ... existing code ...

    @staticmethod
    def create_from_text_aligns(
        positions: TransBuf,
        strings: list[str],
        colors: TransBuf,
        font_sizes: TransBuf,
        aligns: list[TextAlign],  # ← New parameter
        angles: TransBuf,
        font_name: str,
    ) -> "Texts":
        """Create Texts visual using TextAlign values instead of raw anchors.

        Args:
            positions: Positions of the texts.
            strings: List of text strings.
            colors: Colors of the texts.
            font_sizes: Font sizes of the texts.
            aligns: List of TextAlign values specifying text alignment.
            angles: Rotation angles of the texts.
            font_name: Font name for the texts.

        Returns:
            Texts: A Texts visual with anchors converted from TextAlign values.
        """
        import numpy as np

        # Convert TextAlign values to anchor coordinates
        anchors_data = np.array(
            [align.to_anchor_coordinates() for align in aligns],
            dtype=np.float32
        )

        from ..extra.bufferx import Bufferx
        from gsp.types import BufferType
        anchors_buffer = Bufferx.from_numpy(anchors_data, BufferType.vec2)

        return Texts(positions, strings, colors, font_sizes, anchors_buffer, angles, font_name)
```

---

## Step 5: Testing

### Create Unit Tests

**File:** `tests/test_text_align.py`

```python
import pytest
import numpy as np
from gsp.types import TextAlign, VerticalAlign, HorizontalAlign


class TestTextAlign:
    """Test TextAlign encoding and conversions."""

    def test_direct_access(self):
        """Test accessing predefined alignments."""
        assert TextAlign.TOP_LEFT.value == 0
        assert TextAlign.CENTER_CENTER.value == 11
        assert TextAlign.BOTTOM_RIGHT.value == 22

    def test_components(self):
        """Test extracting vertical and horizontal components."""
        align = TextAlign.CENTER_RIGHT
        assert align.vertical() == VerticalAlign.CENTER
        assert align.horizontal() == HorizontalAlign.RIGHT

    def test_from_components(self):
        """Test creating from components."""
        align = TextAlign.from_components(VerticalAlign.BOTTOM, HorizontalAlign.LEFT)
        assert align == TextAlign.BOTTOM_LEFT
        assert align.value == 20

    def test_to_anchor_coordinates(self):
        """Test conversion to normalized anchor coordinates."""
        assert TextAlign.TOP_LEFT.to_anchor_coordinates() == (-1.0, -1.0)
        assert TextAlign.CENTER_CENTER.to_anchor_coordinates() == (0.0, 0.0)
        assert TextAlign.BOTTOM_RIGHT.to_anchor_coordinates() == (1.0, 1.0)

    def test_from_anchor_coordinates(self):
        """Test creation from normalized anchor coordinates."""
        align = TextAlign.from_anchor_coordinates(-1.0, -1.0)
        assert align == TextAlign.TOP_LEFT

        align = TextAlign.from_anchor_coordinates(0.0, 0.0)
        assert align == TextAlign.CENTER_CENTER

    def test_to_matplotlib_alignment(self):
        """Test conversion to matplotlib (ha, va) strings."""
        ha, va = TextAlign.TOP_RIGHT.to_matplotlib_alignment()
        assert ha == "right"
        assert va == "top"

        ha, va = TextAlign.CENTER_LEFT.to_matplotlib_alignment()
        assert ha == "left"
        assert va == "center"

    def test_roundtrip_anchor_coordinates(self):
        """Test roundtrip: TextAlign → anchors → TextAlign."""
        for align in [TextAlign.TOP_LEFT, TextAlign.CENTER_CENTER, TextAlign.BOTTOM_RIGHT]:
            x, y = align.to_anchor_coordinates()
            recovered = TextAlign.from_anchor_coordinates(x, y)
            assert recovered == align


class TestTextAlignMatplotlib:
    """Test matplotlib integration."""

    def test_matplotlib_rendering(self):
        """Test that TextAlign produces correct matplotlib alignments."""
        # This would be an integration test with actual matplotlib
        pass
```

### Visual Regression Tests

```python
# tests/test_text_rendering_visual.py
def test_texts_alignment_matplotlib():
    """Test text alignment rendering with matplotlib."""
    # Create texts with different alignments
    # Render and compare against reference images
    pass

def test_texts_alignment_datoviz():
    """Test text alignment rendering with datoviz."""
    # Same test for datoviz backend
    pass
```

---

## Implementation Checklist

- [ ] Create `TextAlign` type in `src/gsp/types/text_align.py`
- [ ] Update `src/gsp/types/__init__.py` to export `TextAlign`, `VerticalAlign`, `HorizontalAlign`
- [ ] Update matplotlib renderer: `src/gsp_matplotlib/renderer/matplotlib_renderer_texts.py`
  - [ ] Fix vertical anchor mapping using `TextAlign.from_anchor_coordinates()`
  - [ ] Use `TextAlign.to_matplotlib_alignment()` for correct alignment strings
- [ ] Update datoviz renderer: `src/gsp_datoviz/renderer/datoviz_renderer_texts.py`
  - [ ] Implement anchor handling (choose Option A, B, or C)
  - [ ] Test with datoviz visual API
- [ ] Update example: `examples/texts_example.py` (optional but recommended)
- [ ] Add unit tests: `tests/test_text_align.py`
- [ ] Add visual regression tests
- [ ] Run full test suite with both backends
- [ ] Update documentation
- [ ] Create changelog entry

---

## Verification Steps

After implementation:

1. **Run unit tests:**
   ```bash
   pytest tests/test_text_align.py -v
   ```

2. **Run text rendering tests:**
   ```bash
   pytest tests/ -k "text" -v
   ```

3. **Run both backend tests:**
   ```bash
   GSP_BACKEND=matplotlib pytest tests/test_text_rendering_visual.py
   GSP_BACKEND=datoviz pytest tests/test_text_rendering_visual.py
   ```

4. **Visual inspection:**
   - Run `examples/texts_example.py` with both backends
   - Compare output against expected reference images
   - Verify text alignment is correct for all 9 positions

5. **Check for regressions:**
   ```bash
   pytest tests/ --cov=src --cov-report=term-missing
   ```

---

## Rollback Plan

If issues arise:

1. Keep the original buggy code in version control
2. The new `TextAlign` type is additive (doesn't break existing code)
3. Can revert renderer changes without affecting the type definition
4. Example code changes are optional and can be reverted independently

---

## Performance Considerations

The `TextAlign` approach:
- ✅ **Same or better performance** than original (simple arithmetic)
- ✅ **No additional memory** (single int instead of float tuple)
- ✅ **Better cache locality** (single value vs. array)
- ✅ **No numpy operations** needed for alignment logic

No performance regression expected.
