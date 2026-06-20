"""Minimal VisPy2 producer API for GSP protocol visuals.

This MVP makes VisPy2 a small user-facing producer of formal GSP protocol
objects. Rendering is delegated to the Matplotlib reference protocol backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from gsp.protocol import ImageInterpolation, ImageOrigin, ImageVisual, PointVisual
from gsp_matplotlib.protocol_renderer import render_image_visual, render_point_visual


_visual_counter = count(1)


@dataclass(slots=True)
class Figure:
    """Container for the minimal VisPy2 protocol scene."""

    axes: list["Axes"] = field(default_factory=list)

    def add_axes(self) -> "Axes":
        """Add one protocol-producing axes to the figure."""
        axes = Axes(figure=self)
        self.axes.append(axes)
        return axes

    def visuals(self) -> tuple[PointVisual | ImageVisual, ...]:
        """Return protocol visuals in creation order."""
        return tuple(visual for axes in self.axes for visual in axes.visuals)

    def render_matplotlib(self) -> tuple[Any, Any]:
        """Render the protocol scene through the Matplotlib reference backend."""
        import matplotlib.pyplot as plt

        fig, mpl_axes = plt.subplots()
        for visual in self.visuals():
            if isinstance(visual, ImageVisual):
                render_image_visual(mpl_axes, visual)
            elif isinstance(visual, PointVisual):
                render_point_visual(mpl_axes, visual)
            else:
                raise TypeError(f"unsupported protocol visual: {type(visual)!r}")
        mpl_axes.set_aspect("auto")
        return fig, mpl_axes

    def savefig(self, path: str | Path, **kwargs: Any) -> None:
        """Render through Matplotlib and save the result."""
        fig, _ = self.render_matplotlib()
        try:
            fig.savefig(path, **kwargs)
        finally:
            import matplotlib.pyplot as plt

            plt.close(fig)

    def show(self) -> tuple[Any, Any]:
        """Render and show the Matplotlib figure."""
        fig, mpl_axes = self.render_matplotlib()
        import matplotlib.pyplot as plt

        plt.show()
        return fig, mpl_axes


@dataclass(slots=True)
class Axes:
    """Minimal axes object that produces GSP protocol visuals."""

    figure: Figure
    visuals: list[PointVisual | ImageVisual] = field(default_factory=list)

    def scatter(
        self,
        x: npt.ArrayLike,
        y: npt.ArrayLike | None = None,
        *,
        c: npt.ArrayLike | None = None,
        color: npt.ArrayLike | None = None,
        s: npt.ArrayLike | float = 36.0,
        size: npt.ArrayLike | float | None = None,
        id: str | None = None,
    ) -> PointVisual:
        """Create a protocol point visual from x/y or an ``(N, 2|3)`` array."""
        positions = _positions(x, y)
        colors = _colors(c if c is not None else color, positions.shape[0])
        sizes = _sizes(size if size is not None else s, positions.shape[0])
        visual = PointVisual(
            id=id or _visual_id("points"),
            positions=positions,
            colors=colors,
            sizes=sizes,
        )
        self.visuals.append(visual)
        return visual

    def imshow(
        self,
        image: npt.ArrayLike,
        *,
        extent: tuple[float, float, float, float] | None = None,
        origin: str | ImageOrigin = ImageOrigin.UPPER,
        interpolation: str | ImageInterpolation = ImageInterpolation.NEAREST,
        id: str | None = None,
    ) -> ImageVisual:
        """Create a protocol image visual."""
        image_array = np.asarray(image)
        if image_array.dtype == np.dtype(np.float64):
            image_array = image_array.astype(np.float32)
        if extent is None:
            height, width = image_array.shape[:2]
            if _origin(origin) == ImageOrigin.UPPER:
                extent = (-0.5, width - 0.5, height - 0.5, -0.5)
            else:
                extent = (-0.5, width - 0.5, -0.5, height - 0.5)
        visual = ImageVisual(
            id=id or _visual_id("image"),
            image=image_array,
            extent=extent,
            origin=_origin(origin),
            interpolation=_interpolation(interpolation),
        )
        self.visuals.append(visual)
        return visual


def subplots() -> tuple[Figure, Axes]:
    """Create a one-axes VisPy2 protocol figure."""
    fig = Figure()
    ax = fig.add_axes()
    return fig, ax


def scatter(x: npt.ArrayLike, y: npt.ArrayLike | None = None, **kwargs: Any) -> PointVisual:
    """Create a point visual in a temporary one-axes figure."""
    _, ax = subplots()
    return ax.scatter(x, y, **kwargs)


def imshow(image: npt.ArrayLike, **kwargs: Any) -> ImageVisual:
    """Create an image visual in a temporary one-axes figure."""
    _, ax = subplots()
    return ax.imshow(image, **kwargs)


def _visual_id(prefix: str) -> str:
    return f"visual:{prefix}-{next(_visual_counter)}"


def _positions(x: npt.ArrayLike, y: npt.ArrayLike | None) -> npt.NDArray[np.float32]:
    x_array = np.asarray(x, dtype=np.float32)
    if y is None:
        if x_array.ndim != 2 or x_array.shape[1] not in (2, 3):
            raise ValueError("scatter requires x/y arrays or an array with shape (N, 2) or (N, 3)")
        return np.ascontiguousarray(x_array)
    y_array = np.asarray(y, dtype=np.float32)
    if x_array.ndim != 1 or y_array.ndim != 1 or x_array.shape[0] != y_array.shape[0]:
        raise ValueError("x and y must be one-dimensional arrays with the same length")
    return np.ascontiguousarray(np.column_stack([x_array, y_array]).astype(np.float32))


def _colors(value: npt.ArrayLike | None, count_: int) -> npt.NDArray[np.uint8] | npt.NDArray[np.float32]:
    if value is None:
        return np.tile(np.array([[31, 119, 180, 255]], dtype=np.uint8), (count_, 1))
    array = np.asarray(value)
    if array.ndim == 1 and array.shape[0] == 4:
        array = np.tile(array.reshape(1, 4), (count_, 1))
    if array.ndim != 2 or array.shape != (count_, 4):
        raise ValueError("color must be RGBA with shape (4,) or (N, 4)")
    if array.dtype == np.dtype(np.uint8):
        return np.ascontiguousarray(array)
    if np.issubdtype(array.dtype, np.integer):
        return np.ascontiguousarray(array.astype(np.uint8))
    return np.ascontiguousarray(array.astype(np.float32))


def _sizes(value: npt.ArrayLike | float, count_: int) -> npt.NDArray[np.float32] | float:
    if np.isscalar(value):
        return float(value)
    array = np.asarray(value, dtype=np.float32)
    if array.ndim != 1 or array.shape[0] != count_:
        raise ValueError("size must be scalar or shape (N,)")
    return np.ascontiguousarray(array)


def _origin(value: str | ImageOrigin) -> ImageOrigin:
    if isinstance(value, ImageOrigin):
        return value
    return ImageOrigin(value)


def _interpolation(value: str | ImageInterpolation) -> ImageInterpolation:
    if isinstance(value, ImageInterpolation):
        return value
    return ImageInterpolation(value)
