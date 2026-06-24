"""Matplotlib reference rendering for formal protocol visual models."""

from __future__ import annotations

import matplotlib.axes
import matplotlib.collections
import matplotlib.image
import matplotlib.markers
import matplotlib.path
import matplotlib.transforms
import numpy as np
import numpy.typing as npt

from gsp.protocol.visuals import ImageInterpolation, ImageVisual, MarkerShape, MarkerVisual, PointVisual


_MARKER_SHAPES_MPL = {
    MarkerShape.DISC: "o",
    MarkerShape.SQUARE: "s",
    MarkerShape.TRIANGLE: "^",
    MarkerShape.CROSS: "+",
}

_DIAMOND_PATH = matplotlib.path.Path(
    np.array([[0.0, 0.5], [0.5, 0.0], [0.0, -0.5], [-0.5, 0.0], [0.0, 0.5]], dtype=np.float32)
)


def _rgba_for_matplotlib(colors: np.ndarray) -> np.ndarray:
    if colors.dtype == np.dtype(np.uint8):
        return colors.astype(np.float32) / 255.0
    return colors


def _marker_areas_from_pixel_diameters(
    axes: matplotlib.axes.Axes,
    sizes: np.ndarray | float,
) -> npt.NDArray[np.float32] | float:
    """Convert protocol pixel diameters to Matplotlib scatter area units."""
    pixel_to_point = _pixel_to_point(axes)
    if isinstance(sizes, np.ndarray):
        diameters = sizes.reshape(-1).astype(np.float32, copy=False)
        areas: npt.NDArray[np.float32] = diameters * np.float32(pixel_to_point)
        return areas * areas
    return float((sizes * pixel_to_point) ** 2)


def render_point_visual(axes: matplotlib.axes.Axes, visual: PointVisual) -> matplotlib.collections.PathCollection:
    """Render a protocol point visual into a Matplotlib axes."""
    offsets = visual.positions[:, :2]
    areas = _marker_areas_from_pixel_diameters(axes, visual.sizes)
    collection = axes.scatter(
        offsets[:, 0],
        offsets[:, 1],
        s=areas,
        c=_rgba_for_matplotlib(visual.colors),
    )
    collection.set_gid(visual.id)
    return collection


def render_marker_visual(axes: matplotlib.axes.Axes, visual: MarkerVisual) -> tuple[matplotlib.collections.PathCollection, ...]:
    """Render a protocol marker visual into a Matplotlib axes."""
    offsets = visual.positions[:, :2]
    areas = _marker_area_values(axes, visual.sizes, offsets.shape[0])
    fill_colors = _rgba_for_matplotlib(visual.fill_colors)
    stroke_color = _rgba_tuple(_rgba_for_matplotlib(visual.stroke_color))
    shapes = visual.shape_values()
    angles = visual.angle_values()

    collections: list[matplotlib.collections.PathCollection] = []
    for index, (shape, angle) in enumerate(zip(shapes, angles, strict=True)):
        collection = matplotlib.collections.PathCollection(
            [_marker_path(shape, float(angle))],
            sizes=[areas[index]],
            offsets=np.array([[offsets[index, 0], offsets[index, 1]]], dtype=np.float32),
            offset_transform=axes.transData,
            facecolors=[fill_colors[index]],
            edgecolors=[stroke_color],
            linewidths=_linewidth_from_pixel_width(axes, visual.stroke_width),
        )
        collection.set_transform(matplotlib.transforms.IdentityTransform())
        axes.add_collection(collection)
        collection.set_gid(visual.id)
        collections.append(collection)
    return tuple(collections)


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


def _marker_area_values(
    axes: matplotlib.axes.Axes,
    sizes: np.ndarray | float,
    count: int,
) -> npt.NDArray[np.float32]:
    areas = _marker_areas_from_pixel_diameters(axes, sizes)
    if isinstance(areas, np.ndarray):
        return np.ascontiguousarray(areas.astype(np.float32, copy=False).reshape(-1))
    return np.full((count,), float(areas), dtype=np.float32)


def _linewidth_from_pixel_width(axes: matplotlib.axes.Axes, width: float) -> float:
    """Convert protocol pixel stroke width to Matplotlib point linewidth."""
    return float(width * _pixel_to_point(axes))


def _pixel_to_point(axes: matplotlib.axes.Axes) -> float:
    return 72.0 / float(axes.figure.dpi)


def _marker_path(shape: MarkerShape, angle: float) -> matplotlib.path.Path:
    if shape == MarkerShape.DIAMOND:
        path = _DIAMOND_PATH
    else:
        marker = matplotlib.markers.MarkerStyle(_MARKER_SHAPES_MPL[shape])
        path = marker.get_path().transformed(marker.get_transform())
    if angle == 0.0:
        return path
    return path.transformed(matplotlib.transforms.Affine2D().rotate(angle))


def _rgba_tuple(color: npt.NDArray[np.float32] | npt.NDArray[np.float64]) -> tuple[float, float, float, float]:
    return (float(color[0]), float(color[1]), float(color[2]), float(color[3]))
