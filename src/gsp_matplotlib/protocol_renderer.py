"""Matplotlib reference rendering for formal protocol visual models."""

from __future__ import annotations

from collections.abc import Mapping

import matplotlib.axes
import matplotlib.colorbar
import matplotlib.collections
import matplotlib.cm
import matplotlib.colors
import matplotlib.image
import matplotlib.markers
import matplotlib.path
import matplotlib.patches
import matplotlib.text
import matplotlib.transforms
import numpy as np
import numpy.typing as npt

from gsp.protocol import ColorScale, ColorbarGuide
from gsp.protocol.visuals import (
    CoordinateSpace,
    FontRole,
    ImageInterpolation,
    ImageVisual,
    MeshColorMode,
    MeshVisual,
    MarkerShape,
    MarkerVisual,
    PathVisual,
    PointVisual,
    SegmentVisual,
    StrokeCap,
    StrokeJoin,
    TextAnchorX,
    TextAnchorY,
    TextVisual,
)
from gsp_matplotlib.color_mapping import (
    listed_colormap_for_scale,
    map_scalar_values,
    resolve_color_scale,
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


_FONT_FAMILIES_MPL = {
    FontRole.SANS: "sans-serif",
    FontRole.SERIF: "serif",
    FontRole.MONOSPACE: "monospace",
}

_TEXT_ANCHOR_X_MPL = {
    TextAnchorX.LEFT: "left",
    TextAnchorX.CENTER: "center",
    TextAnchorX.RIGHT: "right",
}

_TEXT_ANCHOR_Y_MPL = {
    TextAnchorY.BASELINE: "baseline",
    TextAnchorY.TOP: "top",
    TextAnchorY.CENTER: "center",
    TextAnchorY.BOTTOM: "bottom",
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
    axes: matplotlib.axes.Axes,
    visual: PointVisual,
    *,
    color_scales: Mapping[str, ColorScale] | None = None,
) -> matplotlib.collections.PathCollection:
    """Render a protocol point visual into a Matplotlib axes."""
    offsets = visual.positions[:, :2]
    areas = _marker_areas_from_pixel_diameters(axes, visual.sizes)
    colors = _point_colors(visual, color_scales=color_scales)
    collection = axes.scatter(
        offsets[:, 0],
        offsets[:, 1],
        s=areas,
        c=colors,
    )
    collection.set_gid(visual.id)
    return collection


def render_marker_visual(
    axes: matplotlib.axes.Axes,
    visual: MarkerVisual,
    *,
    color_scales: Mapping[str, ColorScale] | None = None,
) -> tuple[matplotlib.collections.PathCollection, ...]:
    """Render a protocol marker visual into a Matplotlib axes."""
    offsets = visual.positions[:, :2]
    areas = _marker_area_values(axes, visual.sizes, offsets.shape[0])
    fill_colors = _marker_fill_colors(visual, color_scales=color_scales)
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


def render_mesh_visual(
    axes: matplotlib.axes.Axes, visual: MeshVisual
) -> matplotlib.collections.PolyCollection:
    """Render the strict 2D MeshVisual subset into a Matplotlib axes."""
    if visual.face_color_encoding is not None:
        raise NotImplementedError(
            "Matplotlib MeshVisual scalar face colors are capability-gated"
        )
    if visual.positions.shape[1] != 2:
        raise NotImplementedError(
            "Matplotlib MeshVisual reference supports 2D positions only"
        )
    color_mode = visual.resolved_color_mode()
    if color_mode is MeshColorMode.VERTEX:
        raise NotImplementedError(
            "Matplotlib MeshVisual vertex colors are capability-gated"
        )

    triangles = visual.positions[visual.faces][:, :, :2]
    if color_mode is MeshColorMode.UNIFORM:
        facecolors = np.repeat(
            visual.color[np.newaxis, :], visual.faces.shape[0], axis=0
        )
    elif color_mode is MeshColorMode.FACE:
        facecolors = visual.color
    else:
        raise NotImplementedError(f"unsupported mesh color mode: {color_mode.value}")

    collection = matplotlib.collections.PolyCollection(
        [np.ascontiguousarray(triangle, dtype=np.float32) for triangle in triangles],
        facecolors=_rgba_for_matplotlib(facecolors),
        edgecolors="none",
        closed=True,
        antialiaseds=False,
        zorder=visual.order,
    )
    collection.set_gid(visual.id)
    axes.add_collection(collection)
    return collection


def render_text_visual(
    axes: matplotlib.axes.Axes, visual: TextVisual
) -> tuple[matplotlib.text.Text, ...]:
    """Render protocol text labels into a Matplotlib axes."""
    positions = visual.positions[:, :2]
    colors = _rgba_for_matplotlib(visual.rgba_values())
    font_sizes = visual.font_size_values() * np.float32(_pixel_to_point(axes))
    anchor_x_values = visual.anchor_x_values()
    anchor_y_values = visual.anchor_y_values()
    rotations = np.rad2deg(visual.rotation_values())
    transform = _text_transform(axes, visual.coordinate_space)
    font_family = _FONT_FAMILIES_MPL.get(visual.font_role)

    artists: list[matplotlib.text.Text] = []
    for index, text in enumerate(visual.texts):
        artist = axes.text(
            float(positions[index, 0]),
            float(positions[index, 1]),
            text,
            color=_rgba_tuple(colors[index]),
            fontsize=float(font_sizes[index]),
            fontfamily=font_family,
            horizontalalignment=_TEXT_ANCHOR_X_MPL[anchor_x_values[index]],
            verticalalignment=_TEXT_ANCHOR_Y_MPL[anchor_y_values[index]],
            rotation=float(rotations[index]),
            rotation_mode="anchor",
            transform=transform,
            zorder=visual.z_order,
        )
        artist.set_gid(visual.id)
        artist.set_url(f"{visual.id}#{index}")
        artists.append(artist)
    return tuple(artists)


def render_image_visual(
    axes: matplotlib.axes.Axes,
    visual: ImageVisual,
    *,
    color_scales: Mapping[str, ColorScale] | None = None,
) -> matplotlib.image.AxesImage:
    """Render a protocol image visual into a Matplotlib axes."""
    interpolation = (
        "nearest" if visual.interpolation == ImageInterpolation.NEAREST else "bilinear"
    )
    image_data = visual.image
    cmap = None
    if visual.color_scale_id is not None:
        scale = resolve_color_scale(color_scales, visual.color_scale_id)
        image_data = map_scalar_values(visual.image, scale)
    else:
        cmap = visual.colormap.value if visual.colormap is not None else None
        if cmap is None and visual.image.ndim == 2:
            cmap = "gray"
    image = axes.imshow(
        image_data,
        extent=visual.extent,
        interpolation=interpolation,
        origin=visual.origin.value,
        cmap=cmap,
    )
    if visual.clim is not None and visual.color_scale_id is None:
        image.set_clim(*visual.clim)
    image.set_gid(visual.id)
    return image


def render_colorbar_guide(
    axes: matplotlib.axes.Axes,
    guide: ColorbarGuide,
    *,
    color_scales: Mapping[str, ColorScale],
) -> matplotlib.colorbar.Colorbar:
    """Render a semantic colorbar guide for one Matplotlib axes."""
    scale = resolve_color_scale(color_scales, guide.color_scale_id)
    norm = matplotlib.colors.Normalize(
        vmin=scale.normalize.vmin, vmax=scale.normalize.vmax, clip=True
    )
    mappable = matplotlib.cm.ScalarMappable(
        norm=norm,
        cmap=listed_colormap_for_scale(scale),
    )
    colorbar = axes.figure.colorbar(
        mappable,
        ax=axes,
        orientation=guide.orientation.value,
    )
    colorbar.set_label(guide.label)
    if guide.ticks:
        colorbar.set_ticks(guide.ticks)
    if guide.tick_labels is not None:
        colorbar.set_ticklabels(guide.tick_labels)
    colorbar.ax.set_gid(guide.id)
    return colorbar


def _text_transform(
    axes: matplotlib.axes.Axes, coordinate_space: CoordinateSpace
) -> matplotlib.transforms.Transform:
    if coordinate_space == CoordinateSpace.DATA:
        return axes.transData
    if coordinate_space == CoordinateSpace.NDC:
        return (
            matplotlib.transforms.Affine2D().scale(0.5).translate(0.5, 0.5)
            + axes.transAxes
        )
    raise ValueError(f"unsupported coordinate_space: {coordinate_space!r}")


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


def _point_colors(
    visual: PointVisual, *, color_scales: Mapping[str, ColorScale] | None
) -> npt.NDArray[np.float64] | npt.NDArray[np.float32]:
    if visual.color_encoding is not None:
        scale = resolve_color_scale(color_scales, visual.color_encoding.color_scale_id)
        return map_scalar_values(
            visual.color_encoding.values, scale, alpha=visual.color_encoding.alpha
        )
    if visual.colors is None:
        raise ValueError("PointVisual requires colors or color_encoding")
    return _rgba_for_matplotlib(visual.colors)


def _marker_fill_colors(
    visual: MarkerVisual, *, color_scales: Mapping[str, ColorScale] | None
) -> npt.NDArray[np.float64] | npt.NDArray[np.float32]:
    if visual.fill_color_encoding is not None:
        scale = resolve_color_scale(
            color_scales, visual.fill_color_encoding.color_scale_id
        )
        return map_scalar_values(
            visual.fill_color_encoding.values,
            scale,
            alpha=visual.fill_color_encoding.alpha,
        )
    if visual.fill_colors is None:
        raise ValueError("MarkerVisual requires fill_colors or fill_color_encoding")
    return _rgba_for_matplotlib(visual.fill_colors)


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
