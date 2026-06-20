"""Matplotlib reference rendering for formal protocol visual models."""

from __future__ import annotations

import matplotlib.axes
import matplotlib.image
import matplotlib.collections
import numpy as np

from gsp.protocol.visuals import ImageInterpolation, ImageVisual, PointVisual


def _rgba_for_matplotlib(colors: np.ndarray) -> np.ndarray:
    if colors.dtype == np.dtype(np.uint8):
        return colors.astype(np.float32) / 255.0
    return colors


def render_point_visual(axes: matplotlib.axes.Axes, visual: PointVisual) -> matplotlib.collections.PathCollection:
    """Render a protocol point visual into a Matplotlib axes."""
    offsets = visual.positions[:, :2]
    sizes = visual.sizes if isinstance(visual.sizes, float) else visual.sizes.reshape(-1)
    collection = axes.scatter(
        offsets[:, 0],
        offsets[:, 1],
        s=sizes,
        c=_rgba_for_matplotlib(visual.colors),
    )
    collection.set_gid(visual.id)
    return collection


def render_image_visual(axes: matplotlib.axes.Axes, visual: ImageVisual) -> matplotlib.image.AxesImage:
    """Render a protocol image visual into a Matplotlib axes."""
    interpolation = "nearest" if visual.interpolation == ImageInterpolation.NEAREST else "bilinear"
    image = axes.imshow(
        visual.image,
        extent=visual.extent,
        interpolation=interpolation,
        origin=visual.origin.value,
    )
    image.set_gid(visual.id)
    return image
