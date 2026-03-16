# TextAlign Quick Reference

## Enum Values at a Glance

```
╔═══════════════╦═══════╗  ╔═══════════════╦═══════╗  ╔═══════════════╦═══════╗
║     TOP       ║ Value ║  ║    CENTER     ║ Value ║  ║    BOTTOM     ║ Value ║
╠═══════════════╬═══════╣  ╠═══════════════╬═══════╣  ╠═══════════════╬═══════╣
║  LEFT    00   ║   0   ║  ║  LEFT    10   ║  10   ║  ║  LEFT    20   ║  20   ║
║  CENTER  01   ║   1   ║  ║  CENTER  11   ║  11   ║  ║  CENTER  21   ║  21   ║
║  RIGHT   02   ║   2   ║  ║  RIGHT   12   ║  12   ║  ║  RIGHT   22   ║  22   ║
╚═══════════════╩═══════╝  ╚═══════════════╩═══════╝  ╚═══════════════╩═══════╝
```

## Import

```python
from gsp.types import TextAlign, VerticalAlign, HorizontalAlign
```

## Creating TextAlign Values

### Method 1: Direct Access (Most Common)
```python
align = TextAlign.TOP_LEFT
align = TextAlign.CENTER_CENTER
align = TextAlign.BOTTOM_RIGHT
```

### Method 2: From Components
```python
align = TextAlign.from_components(VerticalAlign.CENTER, HorizontalAlign.RIGHT)
align = TextAlign.from_components(1, 2)  # Same thing
```

### Method 3: From Anchor Coordinates
```python
align = TextAlign.from_anchor_coordinates(-1.0, -1.0)  # TOP_LEFT
align = TextAlign.from_anchor_coordinates(0.0, 0.0)    # CENTER_CENTER
align = TextAlign.from_anchor_coordinates(1.0, 1.0)    # BOTTOM_RIGHT
```

## Getting Information

### Get Components
```python
align = TextAlign.CENTER_RIGHT
v = align.vertical()      # VerticalAlign.CENTER
h = align.horizontal()    # HorizontalAlign.RIGHT
v, h = align.to_components()
```

### Convert to Anchor Coordinates
```python
align = TextAlign.TOP_LEFT
x, y = align.to_anchor_coordinates()
# x = -1.0, y = -1.0
```

### Convert to Matplotlib Alignment
```python
align = TextAlign.TOP_RIGHT
ha, va = align.to_matplotlib_alignment()
# ha = "right", va = "top"
```

## Common Use Cases

### Case 1: Matplotlib Text Rendering
```python
from gsp.types import TextAlign
import matplotlib.text

align = TextAlign.CENTER_LEFT
ha, va = align.to_matplotlib_alignment()

text = matplotlib.text.Text()
text.set_horizontalalignment(ha)
text.set_verticalalignment(va)
```

### Case 2: Create from Normalized Anchors
```python
anchor_x, anchor_y = -0.5, 0.7  # From some system
align = TextAlign.from_anchor_coordinates(anchor_x, anchor_y)
# Automatically rounded to nearest valid alignment
```

### Case 3: Store in Numpy Array
```python
import numpy as np

aligns = [
    TextAlign.TOP_LEFT,
    TextAlign.CENTER_CENTER,
    TextAlign.BOTTOM_RIGHT,
]

# Convert to integer array
align_values = np.array([int(a.value) for a in aligns], dtype=np.int32)

# Or use integer constructor
recovered = TextAlign(align_values[0])  # TextAlign.TOP_LEFT
```

### Case 4: Serialize to JSON
```python
import json
from gsp.types import TextAlign

align = TextAlign.CENTER_RIGHT
data = json.dumps({"alignment": align.value})

# Load back
data = json.loads(data)
align = TextAlign(data["alignment"])
```

## Encoding Explained

**Formula:** `value = vertical * 10 + horizontal`

- **Vertical Component:** `value // 10`
  - 0 = TOP
  - 1 = CENTER
  - 2 = BOTTOM

- **Horizontal Component:** `value % 10`
  - 0 = LEFT
  - 1 = CENTER
  - 2 = RIGHT

### Decoding Examples
```
Value 0:  0 // 10 = 0 (TOP),     0 % 10 = 0 (LEFT)     → TOP_LEFT
Value 11: 11 // 10 = 1 (CENTER), 11 % 10 = 1 (CENTER)  → CENTER_CENTER
Value 22: 22 // 10 = 2 (BOTTOM), 22 % 10 = 2 (RIGHT)   → BOTTOM_RIGHT
```

## Anchor Coordinate Mapping

```
Anchor System:        Vertical:           Horizontal:
  (-1, -1)              -1.0 = TOP          -1.0 = LEFT
  (-1,  0)               0.0 = CENTER       0.0 = CENTER
  (-1,  1)               1.0 = BOTTOM       1.0 = RIGHT

TextAlign:
  [0]  [1]  [2]        Vertical Index:     Horizontal Index:
  [10][11][12]          0 = TOP             0 = LEFT
  [20][21][22]          1 = CENTER          1 = CENTER
                        2 = BOTTOM          2 = RIGHT
```

## All 9 Alignments

| Name | Value | Vertical | Horizontal | Anchor (x, y) |
|------|-------|----------|------------|---------------|
| TOP_LEFT | 0 | TOP | LEFT | (-1.0, -1.0) |
| TOP_CENTER | 1 | TOP | CENTER | (0.0, -1.0) |
| TOP_RIGHT | 2 | TOP | RIGHT | (1.0, -1.0) |
| CENTER_LEFT | 10 | CENTER | LEFT | (-1.0, 0.0) |
| CENTER_CENTER | 11 | CENTER | CENTER | (0.0, 0.0) |
| CENTER_RIGHT | 12 | CENTER | RIGHT | (1.0, 0.0) |
| BOTTOM_LEFT | 20 | BOTTOM | LEFT | (-1.0, 1.0) |
| BOTTOM_CENTER | 21 | BOTTOM | CENTER | (0.0, 1.0) |
| BOTTOM_RIGHT | 22 | BOTTOM | RIGHT | (1.0, 1.0) |

## Matplotlib Alignment Mapping

| TextAlign | Matplotlib ha | Matplotlib va |
|-----------|---------------|---------------|
| *_LEFT | "left" | N/A |
| *_CENTER | "center" | N/A |
| *_RIGHT | "right" | N/A |
| TOP_* | N/A | "top" |
| CENTER_* | N/A | "center" |
| BOTTOM_* | N/A | "bottom" |

## Performance Notes

- ✅ Single integer value → memory efficient
- ✅ Integer arithmetic → fast operations
- ✅ No array/list overhead
- ✅ Serializes cleanly to single number
- ✅ Easy to debug (value tells you the alignment)

## Common Mistakes to Avoid

❌ **Don't:** Mix anchor coordinates with TextAlign values
```python
# WRONG
align = TextAlign.TOP_LEFT
x, y = -1.0, -1.0
mismatch = align.value != x or y  # Type error
```

✅ **Do:** Convert between systems explicitly
```python
# CORRECT
align = TextAlign.TOP_LEFT
x, y = align.to_anchor_coordinates()  # Now consistent
```

❌ **Don't:** Assume linear value ordering
```python
# WRONG - assumes TOP comes before CENTER
if align.value < 11:
    print("Top or center?")  # Unreliable
```

✅ **Do:** Use component methods
```python
# CORRECT
if align.vertical() == VerticalAlign.CENTER:
    print("Vertically centered")
```

## Type Hints

```python
from typing import Tuple
from gsp.types import TextAlign, VerticalAlign, HorizontalAlign

def process_alignment(align: TextAlign) -> Tuple[str, str]:
    """Process alignment and return matplotlib parameters."""
    return align.to_matplotlib_alignment()

def create_aligned_text(align: TextAlign | VerticalAlign | HorizontalAlign) -> None:
    """Accept alignment in various forms."""
    if isinstance(align, (VerticalAlign, HorizontalAlign)):
        # Handle single-component alignment
        pass
    else:
        # align is TextAlign
        ha, va = align.to_matplotlib_alignment()
```

## Further Reading

- Implementation: `src/gsp/types/text_align.py`
- Usage Guide: `TEXT_ALIGN_USAGE.md`
- Migration Guide: `TEXT_ALIGN_MIGRATION.md`
- Bug Report: `TEXT_RENDERING_REVIEW.md`
