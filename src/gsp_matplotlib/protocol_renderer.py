"""Matplotlib reference rendering for formal protocol visual models."""

from __future__ import annotations

import matplotlib.axes
import matplotlib.collections
import matplotlib.image
import matplotlib.markers
import matplotlib.path
import matplotlib.patches
import matplotlib.transforms
import numpy as np
import numpy.typing as npt

from gsp.protocol.visuals import (
    ImageInterpolation,
    ImageVisual,
    MarkerShape,
    MarkerVisual,
    PathVisual,
    PointVisual,
    SegmentVisual,
    StrokeCap,
    StrokeJoin,
)


_MARKER_SHAPES_MPL = {
    MarkerShape.DISC: "o",
    MarkerShape.SQUARE: "s",
    MarkerShape.TRIANGLE: "^",
    MarkerShape.CROSS: "+",
}

_DIAMOND_PATH = matplotlib.path.Path(
    np.array(
        [[0.0, 0.5], [0.5, 0.0], [0.0, -0.5], [-0.5, 0.0], [0.0, 0.5]], dtype=np.float32
    )
)

_STROKE_CAPS_MPL = {
    StrokeCap.BUTT: "butt",
    StrokeCap.ROUND: "round",
    StrokeCap.SQUARE: "projecting",
}

_STROKE_JOINS_MPL = {
    StrokeJoin.MITER: "miter",
    StrokeJoin.ROUND: "round",
    StrokeJoin.BEVEL: "bevel",
}


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


def render_point_visual(
    axes: matplotlib.axes.Axes, visual: PointVisual
) -> matplotlib.collections.PathCollection:
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


def render_marker_visual(
    axes: matplotlib.axes.Axes, visual: MarkerVisual
) -> tuple[matplotlib.collections.PathCollection, ...]:
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
            offsets=np.array(
                [[offsets[index, 0], offsets[index, 1]]], dtype=np.float32
            ),
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


def render_segment_visual(
    axes: matplotlib.axes.Axes, visual: SegmentVisual
) -> matplotlib.collections.LineCollection:
    """Render a protocol segment visual into a Matplotlib axes."""
    segments = np.stack(
        [visual.start_positions[:, :2], visual.end_positions[:, :2]], axis=1
    )
    segment_list = [
        np.ascontiguousarray(segment, dtype=np.float32) for segment in segments
    ]
    collection = matplotlib.collections.LineCollection(
        segment_list,
        colors=_rgba_for_matplotlib(visual.colors),
        linewidths=_linewidth_values_from_pixel_widths(axes, visual.widths),
        capstyle=_STROKE_CAPS_MPL[visual.cap],
    )
    collection.set_gid(visual.id)
    axes.add_collection(collection)
    return collection


def render_path_visual(
    axes: matplotlib.axes.Axes, visual: PathVisual
) -> tuple[matplotlib.patches.PathPatch, ...]:
    """Render protocol open polyline subpaths into a Matplotlib axes."""
    subpaths = _path_subpath_arrays(visual)
    colors = _rgba_for_matplotlib(visual.colors)
    linewidths = _linewidth_values_from_pixel_widths(axes, visual.widths)
    width_values = (
        linewidths
        if isinstance(linewidths, np.ndarray)
        else np.full((len(subpaths),), float(linewidths), dtype=np.float32)
    )

    patches: list[matplotlib.patches.PathPatch] = []
    for index, vertices in enumerate(subpaths):
        codes = np.full(
            (vertices.shape[0],), matplotlib.path.Path.LINETO, dtype=np.uint8
        )
        codes[0] = matplotlib.path.Path.MOVETO
        path = matplotlib.path.Path(vertices, codes)
        patch = matplotlib.patches.PathPatch(
            path,
            facecolor="none",
            edgecolor=colors[index],
            linewidth=float(width_values[index]),
            capstyle=_STROKE_CAPS_MPL[visual.cap],
            joinstyle=_STROKE_JOINS_MPL[visual.join],
            fill=False,
        )
        patch.set_gid(visual.id)
        axes.add_patch(patch)
        patches.append(patch)
    return tuple(patches)


def render_image_visual(
    axes: matplotlib.axes.Axes, visual: ImageVisual
) -> matplotlib.image.AxesImage:
    """Render a protocol image visual into a Matplotlib axes."""
    interpolation = (
        "nearest" if visual.interpolation == ImageInterpolation.NEAREST else "bilinear"
    )
    image = axes.imshow(
        visual.image,
        extent=visual.extent,
        interpolation=interpolation,
        origin=visual.origin.value,
    )
    image.set_gid(visual.id)
    return image


def _path_subpath_arrays(visual: PathVisual) -> tuple[npt.NDArray[np.float32], ...]:
    offsets = visual.positions[:, :2]
    subpaths: list[npt.NDArray[np.float32]] = []
    start = 0
    for length in visual.path_lengths:
        stop = start + length
        subpaths.append(np.ascontiguousarray(offsets[start:stop], dtype=np.float32))
        start = stop
    return tuple(subpaths)


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


def _linewidth_values_from_pixel_widths(
    axes: matplotlib.axes.Axes,
    widths: np.ndarray | float,
) -> npt.NDArray[np.float32] | float:
    """Convert protocol pixel stroke widths to Matplotlib point linewidths."""
    pixel_to_point = np.float32(_pixel_to_point(axes))
    if isinstance(widths, np.ndarray):
        return np.ascontiguousarray(
            widths.reshape(-1).astype(np.float32, copy=False) * pixel_to_point
        )
    return float(widths * float(pixel_to_point))


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


def _rgba_tuple(
    color: npt.NDArray[np.float32] | npt.NDArray[np.float64],
) -> tuple[float, float, float, float]:
    return (float(color[0]), float(color[1]), float(color[2]), float(color[3]))
