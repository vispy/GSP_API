# Text Anchor Mapping - Bugs Detailed

## Bug #1: Matplotlib Vertical Anchor Inverted

### Current Code (WRONG)
```python
# matplotlib_renderer_texts.py, lines 138-141
ha_label = "center" if anchors_numpy[text_index, 0] == 0.0 else "right" if anchors_numpy[text_index, 0] == 1.0 else "left"
mpl_text.set_horizontalalignment(ha_label)
va_label = "center" if anchors_numpy[text_index, 1] == 0.0 else "top" if anchors_numpy[text_index, 1] == 1.0 else "bottom"
mpl_text.set_verticalalignment(va_label)
```

### What It Currently Does
```
Horizontal (CORRECT by accident):
  anchor = -1.0  →  else case  →  "left"     ✓
  anchor =  0.0  →  "center"   →  "center"   ✓
  anchor = +1.0  →  "right"    →  "right"    ✓

Vertical (WRONG):
  anchor = -1.0  →  else case  →  "bottom"   ✗ (should be "top")
  anchor =  0.0  →  "center"   →  "center"   ✓
  anchor = +1.0  →  "top"      →  "top"      ✗ (should be "bottom")
```

### What It Should Do
```
Both follow normalized coordinate system where:
  -1.0 = negative direction (left/top in screen coords)
   0.0 = center
  +1.0 = positive direction (right/bottom in screen coords)
```

### The Fix
Option 1 (Explicit mapping - RECOMMENDED):
```python
# Horizontal alignment
ha_map = {-1.0: "left", 0.0: "center", 1.0: "right"}
ha_label = ha_map.get(anchors_numpy[text_index, 0], "center")
mpl_text.set_horizontalalignment(ha_label)

# Vertical alignment
va_map = {-1.0: "top", 0.0: "center", 1.0: "bottom"}
va_label = va_map.get(anchors_numpy[text_index, 1], "center")
mpl_text.set_verticalalignment(va_label)
```

Option 2 (Ternary fix):
```python
va_label = "center" if anchors_numpy[text_index, 1] == 0.0 else "bottom" if anchors_numpy[text_index, 1] == 1.0 else "top"
mpl_text.set_verticalalignment(va_label)
```

---

## Bug #2: DataViz Renderer Completely Ignores Anchors

### Current Code (INCOMPLETE)
```python
# datoviz_renderer_texts.py, lines 73-80
colors_buffer = TransBufUtils.to_buffer(texts.get_colors())
font_sizes_buffer = TransBufUtils.to_buffer(texts.get_font_sizes())
anchors_buffer = TransBufUtils.to_buffer(texts.get_anchors())  # ← Loaded but never used!
angles_buffer = TransBufUtils.to_buffer(texts.get_angles())

colors_numpy = Bufferx.to_numpy(colors_buffer)
font_sizes_numpy = Bufferx.to_numpy(font_sizes_buffer)
anchors_numpy = Bufferx.to_numpy(anchors_buffer)  # ← Loaded but never used!
angles_numpy = Bufferx.to_numpy(angles_buffer)

# ... later, when rendering:
dvz_glyphs.set_strings(text_strings, string_pos=vertices_3d)  # Lines 145
dvz_glyphs.set_color(glyph_colors)                           # Line 146
dvz_glyphs.set_angle(glyphs_angles)                          # Line 147
dvz_glyphs.set_scale(glyph_scales)                           # Line 148
# ↑ No set_anchor() call! The anchors_numpy variable is completely unused
```

### What It Currently Does
- Loads anchor data into memory
- Never uses it
- Text renders with whatever default anchor datoviz uses
- User's anchor specifications are silently ignored

### What It Should Do
One of these approaches:

**Approach A: Per-string anchors (if datoviz supports it)**
```python
# After line 148, add:
dvz_glyphs.set_anchor(anchors_numpy)
```

**Approach B: Per-glyph anchors (if datoviz requires individual glyph data)**
```python
# Build glyph anchors from string anchors
glyph_anchors = np.zeros((glyph_count, 2), dtype=np.float32)
for text_index in range(text_count):
    for glyph_index in range(len(text_strings[text_index])):
        global_glyph_index = sum(len(s) for s in text_strings[:text_index]) + glyph_index
        glyph_anchors[global_glyph_index, :] = anchors_numpy[text_index, :]

# Then apply:
dvz_glyphs.set_anchor(glyph_anchors)
```

**Approach C: Post-process vertex positions (if datoviz doesn't support anchors)**
```python
# Manually offset text positions based on anchors and text dimensions
# This is complex and requires knowing text bounding boxes
```

### First Steps
1. Check datoviz documentation for anchor/alignment methods
2. Inspect `_DvzGlyphs` class for available methods
3. Implement the appropriate approach
4. Test against matplotlib renderer output

---

## Real-World Example

From `examples/texts_example.py`:

```python
# Test case: text at y=0.5 with vertical anchor pointing down (should align TOP of text at y=0.5)
anchors_numpy = np.array([[0.0, -1.0]], dtype=np.float32)  # vertical anchor = -1.0

# Current Matplotlib Behavior:
# anchor = -1.0 → va_label = "bottom" → text appears BELOW y=0.5 ✗

# Correct Behavior Should Be:
# anchor = -1.0 → va_label = "top" → TOP of text appears AT y=0.5 ✓

# Current DataViz Behavior:
# anchor is ignored → text appears with default alignment (probably centered) ✗

# Correct Behavior Should Be:
# anchor = -1.0 → text TOP appears AT y=0.5 ✓
```

---

## Summary Table

| Backend | Horizontal | Vertical | Status |
|---------|-----------|----------|--------|
| Matplotlib | ✓ Works correctly | ✗ Completely inverted | BROKEN |
| DataViz | ✗ Ignored | ✗ Ignored | BROKEN |

Both backends are broken for text anchor handling!

---

## Impact

### User Perspective
- Text alignment doesn't work as expected
- Inconsistent behavior between backends
- Visual layout broken for applications relying on proper text alignment

### Developer Perspective
- Example code in `texts_example.py` produces incorrect output
- Anchor specification in Texts visual is effectively non-functional
- No test coverage for anchor functionality

### Priority
🔴 **CRITICAL** - Core feature (text alignment) is broken
