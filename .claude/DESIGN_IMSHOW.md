# GSP_API `imshow()` API Design

## Overview

`imshow()` displays 2D image data from a `Buffer`. This is a focused, minimal API that accepts only local buffers—transforms/lazy evaluation can be added later.

---

## Function Signature

```python
def imshow(
    data: Buffer,
    *,
    cmap: str | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    origin: Literal["upper", "lower"] = "upper",
    extent: tuple[float, float, float, float] | None = None,
    aspect: Literal["auto", "equal"] | float = "auto",
    interpolation: Literal["nearest", "bilinear", "bicubic"] = "nearest",
    alpha: float = 1.0,
) -> ImageReference:
    """
    Display a 2D image from a buffer.

    Args:
        data: Image buffer (2D for grayscale, 3D for RGB/RGBA)
        cmap: Colormap name for single-channel images (ignored for RGB/RGBA)
        vmin: Minimum value for normalization (auto if None)
        vmax: Maximum value for normalization (auto if None)
        origin: 'upper' (default) places origin at top-left; 'lower' at bottom-left
        extent: Custom spatial coordinates [left, right, bottom, top]
        aspect: 'auto' (default), 'equal', or numeric ratio
        interpolation: Pixel interpolation method
        alpha: Transparency (0.0 to 1.0)

    Returns:
        ImageReference: Handle for updating image properties
    """
```

---

## Parameter Details

### `data: Buffer` (Required)
- **Only local buffers** for now (no transforms, numpy arrays, or file paths)
- Must be 2D (grayscale) or 3D (RGB/RGBA)
- Buffer metadata includes shape and dtype

### `cmap: str | None = None`
- Colormap for single-channel (2D) images
- Ignored for RGB/RGBA (3D) images
- Examples: `"viridis"`, `"hot"`, `"RdBu"`, `"gray"`

### `vmin, vmax: float | None = None`
- Value range for normalization
- Both `None` = auto-scale to data min/max
- Useful for fixed ranges across multiple images

### `origin: Literal["upper", "lower"] = "upper"`
- `"upper"` (default): Array indexing (top-left is origin)
- `"lower"`: Cartesian (bottom-left is origin)

### `extent: tuple[float, float, float, float] | None = None`
- Custom spatial coordinates: `[left, right, bottom, top]`
- Maps array indices to spatial coordinates
- Example: `extent=[0, 10, 0, 10]` for 0-10 range in both axes

### `aspect: Literal["auto", "equal"] | float = "auto"`
- `"auto"`: Stretch to fill axes
- `"equal"`: Preserve pixel aspect ratio (1:1)
- Numeric: Custom width-to-height ratio (e.g., `2.0` for 2:1)

### `interpolation: Literal["nearest", "bilinear", "bicubic"] = "nearest"`
- `"nearest"`: Pixelated look (good for discrete data)
- `"bilinear"`: Smooth interpolation
- `"bicubic"`: Higher-quality smooth interpolation

### `alpha: float = 1.0`
- Transparency: `0.0` (fully transparent) to `1.0` (opaque)

---

## Return Type: ImageReference

Enables interactive updates without recreating the image.

```python
class ImageReference:
    def set_data(self, data: Buffer) -> None:
        """Update image data (e.g., for animations)"""

    def set_cmap(self, cmap: str) -> None:
        """Change colormap dynamically"""

    def set_clim(self, vmin: float, vmax: float) -> None:
        """Update value normalization"""

    def get_data(self) -> Buffer:
        """Retrieve current image buffer"""
```

---

## Backend Implementation

### Matplotlib Backend
- Direct delegation to `ax.imshow()`
- Buffer → numpy array conversion
- Full parameter support

### DatoViz Backend
- GPU texture-based rendering
- Colormap via fragment shader
- Efficient updates via texture rebinding
- May require buffer → GPU memory transfer

---

## Usage Examples

```python
import gsp
from gsp import Buffer

# Simple grayscale
data_2d = Buffer(...)
gsp.imshow(data_2d)

# With colormap and range
gsp.imshow(data_2d, cmap="hot", vmin=0, vmax=100)

# RGB image
data_rgb = Buffer(...)  # Shape: (height, width, 3)
gsp.imshow(data_rgb)

# Custom coordinates and aspect
gsp.imshow(data_2d, extent=[0, 1, 0, 1], origin="lower", aspect="equal")

# Animation support
img_ref = gsp.imshow(frame_1)
for frame in frames[1:]:
    img_ref.set_data(frame)
    # Render/display updated image

# Dynamic colormap updates
img_ref.set_cmap("viridis")
img_ref.set_clim(vmin=-1, vmax=1)
```

---

## Design Rationale

| Decision | Why |
|----------|-----|
| **Only `Buffer` input** | Local, predictable data; transforms deferred to future |
| **Keyword-only params** | Clear intent, prevents accidental positional args |
| **Return `ImageReference`** | Enables reactive updates, consistent with matplotlib artists |
| **Default `origin="upper"`** | Matches matplotlib/array conventions |
| **Strict dtypes via Buffer** | Prevents silent conversion bugs |

---

## Future Extensions

- **Transforms**: Accept `TransBuf` to support lazy/remote computation
- **Interactive**: Mouse hover for value display, zoom/pan
- **Contours**: Overlay contour lines on image
- **Annotations**: Text, arrows, shapes on image
