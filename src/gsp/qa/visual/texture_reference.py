"""Backend-neutral reference sampling for Texture2D visual QA fixtures."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from gsp.protocol import TextureFilter


RGBA8Image = npt.NDArray[np.uint8]
UVArray = npt.NDArray[np.floating]
RGBAArray = npt.NDArray[np.float64]


def sample_texture2d_rgba8(
    image: RGBA8Image,
    uvs: UVArray,
    *,
    texture_filter: TextureFilter,
) -> RGBAArray:
    """Sample clamp-to-edge RGBA8 texels using the normative GSP convention."""
    _validate_inputs(image, uvs, texture_filter)
    height, width, _ = image.shape
    flat_uvs = np.asarray(uvs, dtype=np.float64).reshape(-1, 2)
    result = np.empty((flat_uvs.shape[0], 4), dtype=np.float64)

    for index, (u, v) in enumerate(flat_uvs):
        uc = float(np.clip(u, 0.0, 1.0))
        vc = float(np.clip(v, 0.0, 1.0))
        if texture_filter is TextureFilter.NEAREST:
            ix = min(int(np.floor(width * uc)), width - 1)
            iy = min(int(np.floor(height * (1.0 - vc))), height - 1)
            result[index] = image[iy, ix].astype(np.float64) / 255.0
            continue

        x = width * uc - 0.5
        y = height * (1.0 - vc) - 0.5
        x0 = int(np.floor(x))
        y0 = int(np.floor(y))
        tx = x - x0
        ty = y - y0
        x1 = x0 + 1
        y1 = y0 + 1
        x0 = min(max(x0, 0), width - 1)
        x1 = min(max(x1, 0), width - 1)
        y0 = min(max(y0, 0), height - 1)
        y1 = min(max(y1, 0), height - 1)
        c00 = image[y0, x0].astype(np.float64) / 255.0
        c10 = image[y0, x1].astype(np.float64) / 255.0
        c01 = image[y1, x0].astype(np.float64) / 255.0
        c11 = image[y1, x1].astype(np.float64) / 255.0
        result[index] = (
            (1.0 - tx) * (1.0 - ty) * c00
            + tx * (1.0 - ty) * c10
            + (1.0 - tx) * ty * c01
            + tx * ty * c11
        )

    return result.reshape((*uvs.shape[:-1], 4))


def multiply_texture_rgba(samples: RGBAArray, base_rgba: npt.ArrayLike) -> RGBAArray:
    """Multiply straight-alpha sampled channels by normalized base RGBA."""
    base = np.asarray(base_rgba, dtype=np.float64)
    if base.shape != (4,) or not np.all(np.isfinite(base)):
        raise ValueError("base_rgba must contain four finite normalized channels")
    return np.asarray(samples, dtype=np.float64) * base


def _validate_inputs(
    image: RGBA8Image, uvs: UVArray, texture_filter: TextureFilter
) -> None:
    if image.dtype != np.dtype(np.uint8) or image.ndim != 3 or image.shape[2] != 4:
        raise TypeError("image must be a uint8 array with shape (H, W, 4)")
    if image.shape[0] == 0 or image.shape[1] == 0:
        raise ValueError("image dimensions must be positive")
    if uvs.ndim == 0 or uvs.shape[-1] != 2:
        raise ValueError("uvs must have shape (..., 2)")
    if not np.issubdtype(uvs.dtype, np.floating):
        raise TypeError("uvs must have floating dtype")
    if not np.all(np.isfinite(uvs)):
        raise ValueError("uvs must be finite")
    if not isinstance(texture_filter, TextureFilter):
        raise TypeError("texture_filter must be a TextureFilter")
