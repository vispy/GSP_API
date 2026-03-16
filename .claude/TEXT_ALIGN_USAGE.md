# TextAlign Type Usage Guide

## Overview

The `TextAlign` type provides a clean, type-safe way to handle text alignment combining both vertical and horizontal alignment into a single enum value.

**Location:** `src/gsp/types/text_align.py`

**Encoding:** `value = vertical * 10 + horizontal` where:
- Vertical: TOP=0, CENTER=1, BOTTOM=2
- Horizontal: LEFT=0, CENTER=1, RIGHT=2

---

## Basic Usage

### Import

```python
from gsp.types import TextAlign, VerticalAlign, HorizontalAlign
```

### Direct Access

```python
# Access predefined alignments
align = TextAlign.TOP_LEFT      # Value: 0
align = TextAlign.CENTER_CENTER # Value: 11
align = TextAlign.BOTTOM_RIGHT  # Value: 22
```

### Component Access

```python
align = TextAlign.CENTER_RIGHT
vertical = align.vertical()       # Returns VerticalAlign.CENTER
horizontal = align.horizontal()  # Returns HorizontalAlign.RIGHT

v, h = align.to_components()     # Tuple unpacking
```

### Creating from Components

```python
# Using enums
align = TextAlign.from_components(VerticalAlign.CENTER, HorizontalAlign.RIGHT)
# Result: TextAlign.CENTER_RIGHT (value 12)

# Using integers
align = TextAlign.from_components(1, 2)  # Same as above
```

---

## Conversion Methods

### To Matplotlib Alignment

Convert to matplotlib's (ha, va) string parameters:

```python
align = TextAlign.TOP_RIGHT
ha, va = align.to_matplotlib_alignment()
# ha = "right", va = "top"

# Use with matplotlib Text
import matplotlib.text
mpl_text = matplotlib.text.Text()
mpl_text.set_horizontalalignment(ha)
mpl_text.set_verticalalignment(va)
```

### To Normalized Anchor Coordinates

Convert to the normalized [-1, 1] anchor system:

```python
align = TextAlign.TOP_LEFT
anchor_x, anchor_y = align.to_anchor_coordinates()
# anchor_x = -1.0, anchor_y = -1.0

align = TextAlign.CENTER_CENTER
anchor_x, anchor_y = align.to_anchor_coordinates()
# anchor_x = 0.0, anchor_y = 0.0

align = TextAlign.BOTTOM_RIGHT
anchor_x, anchor_y = align.to_anchor_coordinates()
# anchor_x = 1.0, anchor_y = 1.0
```

### From Normalized Anchor Coordinates

Create TextAlign from legacy anchor values:

```python
align = TextAlign.from_anchor_coordinates(-1.0, -1.0)
# Returns: TextAlign.TOP_LEFT

align = TextAlign.from_anchor_coordinates(0.0, 0.0)
# Returns: TextAlign.CENTER_CENTER

# Handles rounding for non-exact values
align = TextAlign.from_anchor_coordinates(-0.8, 0.2)
# Rounds to nearest valid alignment
```

---

## All Available Alignments

| Enum Value | Integer | Vertical | Horizontal |
|---|---|---|---|
| `TOP_LEFT` | 0 | TOP | LEFT |
| `TOP_CENTER` | 1 | TOP | CENTER |
| `TOP_RIGHT` | 2 | TOP | RIGHT |
| `CENTER_LEFT` | 10 | CENTER | LEFT |
| `CENTER_CENTER` | 11 | CENTER | CENTER |
| `CENTER_RIGHT` | 12 | CENTER | RIGHT |
| `BOTTOM_LEFT` | 20 | BOTTOM | LEFT |
| `BOTTOM_CENTER` | 21 | BOTTOM | CENTER |
| `BOTTOM_RIGHT` | 22 | BOTTOM | RIGHT |

---

## Fixing Text Rendering

### Matplotlib Renderer Fix

**Before (Buggy):**
```python
# matplotlib_renderer_texts.py
va_label = "center" if anchors_numpy[text_index, 1] == 0.0 else "top" if anchors_numpy[text_index, 1] == 1.0 else "bottom"
mpl_text.set_verticalalignment(va_label)
```

**After (Using TextAlign):**
```python
# Convert anchor coordinates to TextAlign
anchor_x, anchor_y = anchors_numpy[text_index, :]
align = TextAlign.from_anchor_coordinates(anchor_x, anchor_y)

# Get correct matplotlib alignment
ha, va = align.to_matplotlib_alignment()
mpl_text.set_horizontalalignment(ha)
mpl_text.set_verticalalignment(va)
```

### DataViz Renderer Enhancement

**Before (Incomplete):**
```python
# datoviz_renderer_texts.py
anchors_numpy = Bufferx.to_numpy(anchors_buffer)
# ... never used!
```

**After (Using TextAlign):**
```python
# Convert each text's anchor to TextAlign
text_aligns = []
for text_index in range(text_count):
    anchor_x, anchor_y = anchors_numpy[text_index, :]
    align = TextAlign.from_anchor_coordinates(anchor_x, anchor_y)
    text_aligns.append(align)

# Pass to datoviz (if it supports it)
dvz_glyphs.set_text_align(text_aligns)
```

---

## Example: Text Positioning with Alignment

```python
import numpy as np
from gsp.visuals import Texts
from gsp.types import TextAlign, Buffer, BufferType
from gsp_matplotlib.extra.bufferx import Bufferx

# Create texts at different positions with specific alignments
positions = np.array([
    [0.0, 0.5, 0.0],    # Top position
    [0.0, 0.0, 0.0],    # Center position
    [0.0, -0.5, 0.0],   # Bottom position
], dtype=np.float32)

# Use TextAlign to specify anchors
aligns = [
    TextAlign.TOP_LEFT,      # Anchor at top-left of text
    TextAlign.CENTER_CENTER, # Anchor at center of text
    TextAlign.BOTTOM_RIGHT,  # Anchor at bottom-right of text
]

# Convert to anchor coordinates for Texts visual
anchors = np.array([align.to_anchor_coordinates() for align in aligns], dtype=np.float32)

# Create the Texts visual with proper anchors
texts = Texts(
    positions_buffer,
    strings=["Top", "Center", "Bottom"],
    colors_buffer,
    font_sizes_buffer,
    Bufferx.from_numpy(anchors, BufferType.vec2),  # Use converted anchors
    angles_buffer,
    font_name="Arial"
)
```

---

## Type Safety Benefits

### Before (Error-Prone)
```python
# Easy to make mistakes with magic numbers
anchors_numpy = np.array([[1.0, -1.0], [-1.0, 1.0]], dtype=np.float32)
# Is this right? Which dimension is which? What values are valid?
```

### After (Type-Safe)
```python
from gsp.types import TextAlign

aligns = [TextAlign.TOP_RIGHT, TextAlign.BOTTOM_LEFT]
anchors_numpy = np.array([align.to_anchor_coordinates() for align in aligns])
# Clear intent, no ambiguity, caught by IDE/linter
```

---

## Integer Encoding Benefits

The encoding scheme `value = vertical * 10 + horizontal` provides several advantages:

### 1. **Compactness**
```python
align = TextAlign.CENTER_RIGHT  # Single int value: 12
# vs
vertical = 1
horizontal = 2  # Two separate values
```

### 2. **Easy Encoding/Decoding**
```python
# Encoding: no special function needed
value = vertical * 10 + horizontal

# Decoding: simple arithmetic
vertical = value // 10
horizontal = value % 10
```

### 3. **Storage Efficiency**
- Single byte stores 9 possible values
- No wasted bits
- Serializes cleanly to JSON/binary formats

### 4. **Debugging**
```python
# Integer value immediately tells you the alignment
print(f"Alignment: {align.value}")  # Output: "11"
# Quickly decode: vertical=1, horizontal=1 → CENTER_CENTER
```

---

## Integration with Serialization

The integer values serialize cleanly:

```python
import json
from gsp.types import TextAlign

align = TextAlign.TOP_RIGHT
data = {"text_align": align.value}  # Serializes as {"text_align": 2}

# On load
align = TextAlign(data["text_align"])  # TextAlign.TOP_RIGHT
```

---

## Migration Path

For existing code using anchor coordinates:

1. **Identify** where `anchors_numpy` is used
2. **Create** `TextAlign` values from coordinates: `TextAlign.from_anchor_coordinates(x, y)`
3. **Use** TextAlign methods instead of manual alignment strings
4. **Test** with both matplotlib and datoviz backends

Example migration:
```python
# OLD CODE
ha_label = "center" if anchor_x == 0.0 else "right" if anchor_x == 1.0 else "left"
va_label = "center" if anchor_y == 0.0 else "top" if anchor_y == 1.0 else "bottom"
mpl_text.set_horizontalalignment(ha_label)
mpl_text.set_verticalalignment(va_label)

# NEW CODE
align = TextAlign.from_anchor_coordinates(anchor_x, anchor_y)
ha, va = align.to_matplotlib_alignment()
mpl_text.set_horizontalalignment(ha)
mpl_text.set_verticalalignment(va)
```

---

## Implementation Notes

- All methods are type-hinted for IDE support
- Enum values use `IntEnum` for direct integer operations
- Conversion methods include validation and error handling
- Compatible with numpy operations (can be used in arrays)
- No external dependencies beyond Python stdlib
