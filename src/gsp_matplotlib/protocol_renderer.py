"""Matplotlib reference rendering for formal protocol visual models."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import cast

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
import matplotlib.figure
import numpy as np
import numpy.typing as npt

from gsp.protocol import (
    AffineTransform2DResource,
    AxisGuide,
    ColorScale,
    ColorbarGuide,
    PanelTextGuide,
    ResolvedLayoutSnapshot,
    View2D,
)
from gsp_matplotlib.guides import render_axis_guides, render_panel_text_guides
from gsp_matplotlib.layout import resolve_matplotlib_layout_snapshot
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
from gsp_matplotlib.transforms import (
    panel_ndc_to_axes_fraction,
    transformed_positions,
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


ProtocolVisual = (
    PointVisual
    | MarkerVisual
    | SegmentVisual
    | PathVisual
    | MeshVisual
    | ImageVisual
    | TextVisual
)


@dataclass(frozen=True, slots=True)
class MatplotlibProtocolRenderResult:
    """Matplotlib protocol render result with resolved layout identity."""

    figure: matplotlib.figure.Figure
    axes: matplotlib.axes.Axes
    layout_snapshot: ResolvedLayoutSnapshot

    @property
    def layout_snapshot_id(self) -> str:
        """Return the resolved layout snapshot id used by this render result."""
        return self.layout_snapshot.snapshot_id


def render_protocol_scene_with_layout(
    *,
    visuals: Iterable[ProtocolVisual],
    view: View2D | None = None,
    axis_guides: Iterable[AxisGuide] = (),
    panel_text_guides: Iterable[PanelTextGuide] = (),
    colorbar_guides: Iterable[ColorbarGuide] = (),
    color_scales: Mapping[str, ColorScale] | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
    snapshot_id: str = "layout:matplotlib",
    figure: matplotlib.figure.Figure | None = None,
    axes: matplotlib.axes.Axes | None = None,
    device_scale: float = 1.0,
) -> MatplotlibProtocolRenderResult:
    """Render a protocol scene and report the resolved layout snapshot used."""
    if axes is None:
        import matplotlib.pyplot as plt

        if figure is None:
            figure, axes = plt.subplots()
        else:
            axes = figure.add_subplot()
    elif figure is None:
        figure = cast(matplotlib.figure.Figure, axes.figure)

    color_scale_map = color_scales if color_scales is not None else {}
    for visual in visuals:
        _render_protocol_visual(
            axes,
            visual,
            view=view,
            color_scales=color_scale_map,
            transform_resources=transform_resources,
        )

    axis_guide_tuple = tuple(axis_guides)
    panel_text_guide_tuple = tuple(panel_text_guides)
    if view is not None:
        axes.set_xlim(view.x_range)
        axes.set_ylim(view.y_range)
        axes.set_aspect("equal" if view.aspect_policy.value == "equal" else "auto")
        render_axis_guides(axes, view, axis_guide_tuple)
    render_panel_text_guides(axes, panel_text_guide_tuple)
    for guide in colorbar_guides:
        render_colorbar_guide(axes, guide, color_scales=color_scale_map)

    snapshot = resolve_matplotlib_layout_snapshot(
        figure,
        axes,
        snapshot_id=snapshot_id,
        view=view,
        axis_guides=axis_guide_tuple,
        panel_text_guides=panel_text_guide_tuple,
        device_scale=device_scale,
    )
    return MatplotlibProtocolRenderResult(figure, axes, snapshot)


def _render_protocol_visual(
    axes: matplotlib.axes.Axes,
    visual: ProtocolVisual,
    *,
    view: View2D | None = None,
    color_scales: Mapping[str, ColorScale] | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
) -> object:
    if isinstance(visual, ImageVisual):
        return render_image_visual(axes, visual, color_scales=color_scales)
    if isinstance(visual, MarkerVisual):
        return render_marker_visual(
            axes,
            visual,
            view=view,
            color_scales=color_scales,
            transform_resources=transform_resources,
        )
    if isinstance(visual, SegmentVisual):
        return render_segment_visual(
            axes, visual, view=view, transform_resources=transform_resources
        )
    if isinstance(visual, PathVisual):
        return render_path_visual(
            axes, visual, view=view, transform_resources=transform_resources
        )
    if isinstance(visual, MeshVisual):
        return render_mesh_visual(
            axes, visual, view=view, transform_resources=transform_resources
        )
    if isinstance(visual, PointVisual):
        return render_point_visual(
            axes,
            visual,
            view=view,
            color_scales=color_scales,
            transform_resources=transform_resources,
        )
    if isinstance(visual, TextVisual):
        return render_text_visual(
            axes, visual, view=view, transform_resources=transform_resources
        )
    raise TypeError(f"unsupported protocol visual: {type(visual)!r}")


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
    view: View2D | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
) -> matplotlib.collections.PathCollection:
    """Render a protocol point visual into a Matplotlib axes."""
    offsets, transform = _render_positions(
        axes, visual, visual.positions, view, transform_resources
    )
    areas = _marker_areas_from_pixel_diameters(axes, visual.sizes)
    colors = _point_colors(visual, color_scales=color_scales)
    collection = axes.scatter(
        offsets[:, 0],
        offsets[:, 1],
        s=areas,
        c=colors,
        transform=transform,
    )
    collection.set_gid(visual.id)
    return collection


def render_marker_visual(
    axes: matplotlib.axes.Axes,
    visual: MarkerVisual,
    *,
    color_scales: Mapping[str, ColorScale] | None = None,
    view: View2D | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
) -> tuple[matplotlib.collections.PathCollection, ...]:
    """Render a protocol marker visual into a Matplotlib axes."""
    offsets, transform = _render_positions(
        axes, visual, visual.positions, view, transform_resources
    )
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
            offset_transform=transform,
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
    axes: matplotlib.axes.Axes,
    visual: SegmentVisual,
    *,
    view: View2D | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
) -> matplotlib.collections.LineCollection:
    """Render a protocol segment visual into a Matplotlib axes."""
    start_positions, transform = _render_positions(
        axes, visual, visual.start_positions, view, transform_resources
    )
    end_positions, _ = _render_positions(
        axes, visual, visual.end_positions, view, transform_resources
    )
    segments = np.stack(
        [start_positions, end_positions], axis=1
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
    collection.set_transform(transform)
    collection.set_gid(visual.id)
    axes.add_collection(collection)
    return collection


def render_path_visual(
    axes: matplotlib.axes.Axes,
    visual: PathVisual,
    *,
    view: View2D | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
) -> tuple[matplotlib.patches.PathPatch, ...]:
    """Render protocol open polyline subpaths into a Matplotlib axes."""
    positions, transform = _render_positions(
        axes, visual, visual.positions, view, transform_resources
    )
    subpaths = _path_subpath_arrays(visual, positions)
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
        patch.set_transform(transform)
        patch.set_gid(visual.id)
        axes.add_patch(patch)
        patches.append(patch)
    return tuple(patches)


def render_mesh_visual(
    axes: matplotlib.axes.Axes,
    visual: MeshVisual,
    *,
    view: View2D | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
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
    if visual.color is None:
        raise ValueError("MeshVisual color is required for Matplotlib rendering")
    mesh_color = visual.color

    positions, transform = _render_positions(
        axes, visual, visual.positions, view, transform_resources
    )
    triangles = positions[visual.faces]
    if color_mode is MeshColorMode.UNIFORM:
        facecolors = np.repeat(mesh_color[np.newaxis, :], visual.faces.shape[0], axis=0)
    elif color_mode is MeshColorMode.FACE:
        facecolors = mesh_color
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
    collection.set_transform(transform)
    collection.set_gid(visual.id)
    axes.add_collection(collection)
    return collection


def render_text_visual(
    axes: matplotlib.axes.Axes,
    visual: TextVisual,
    *,
    view: View2D | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
) -> tuple[matplotlib.text.Text, ...]:
    """Render protocol text labels into a Matplotlib axes."""
    positions, transform = _render_positions(
        axes, visual, visual.positions, view, transform_resources
    )
    colors = _rgba_for_matplotlib(visual.rgba_values())
    font_sizes = visual.font_size_values() * np.float32(_pixel_to_point(axes))
    anchor_x_values = visual.anchor_x_values()
    anchor_y_values = visual.anchor_y_values()
    rotations = np.rad2deg(visual.rotation_values())
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
    axes_box = axes.get_position()
    if guide.orientation.value == "vertical":
        cax_bounds = (
            axes_box.x0 + axes_box.width * 0.82,
            axes_box.y0 + axes_box.height * 0.18,
            axes_box.width * 0.035,
            axes_box.height * 0.64,
        )
    else:
        cax_bounds = (
            axes_box.x0 + axes_box.width * 0.18,
            axes_box.y0 + axes_box.height * 0.10,
            axes_box.width * 0.64,
            axes_box.height * 0.045,
        )
    cax = axes.figure.add_axes(cax_bounds)
    colorbar = axes.figure.colorbar(
        mappable,
        cax=cax,
        orientation=guide.orientation.value,
    )
    colorbar.set_label(guide.label)
    if guide.ticks:
        colorbar.set_ticks(guide.ticks)
    if guide.tick_labels is not None:
        colorbar.set_ticklabels(guide.tick_labels)
    colorbar.ax.tick_params(labelsize=8, length=4, width=0.8)
    colorbar.ax.xaxis.label.set_fontsize(8)
    colorbar.ax.yaxis.label.set_fontsize(8)
    colorbar.ax.set_gid(guide.id)
    return colorbar


def _path_subpath_arrays(
    visual: PathVisual, offsets: npt.NDArray[np.float64]
) -> tuple[npt.NDArray[np.float32], ...]:
    subpaths: list[npt.NDArray[np.float32]] = []
    start = 0
    for length in visual.path_lengths:
        stop = start + length
        subpaths.append(np.ascontiguousarray(offsets[start:stop], dtype=np.float32))
        start = stop
    return tuple(subpaths)


def _render_positions(
    axes: matplotlib.axes.Axes,
    visual: PointVisual
    | MarkerVisual
    | SegmentVisual
    | PathVisual
    | MeshVisual
    | TextVisual,
    positions: npt.NDArray[np.float32] | npt.NDArray[np.float64],
    view: View2D | None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None,
) -> tuple[npt.NDArray[np.float64], matplotlib.transforms.Transform]:
    transformed = transformed_positions(
        positions, visual.transform, transform_resources
    )
    if view is None:
        if isinstance(visual, TextVisual) and visual.coordinate_space == CoordinateSpace.NDC:
            return panel_ndc_to_axes_fraction(transformed), axes.transAxes
        return transformed, axes.transData
    if visual.coordinate_space == CoordinateSpace.DATA:
        x0, x1 = view.xlim
        y0, y1 = view.ylim
        panel_ndc = np.empty_like(transformed, dtype=np.float64)
        panel_ndc[:, 0] = -1.0 + 2.0 * (transformed[:, 0] - x0) / (x1 - x0)
        panel_ndc[:, 1] = -1.0 + 2.0 * (transformed[:, 1] - y0) / (y1 - y0)
    elif visual.coordinate_space == CoordinateSpace.NDC:
        panel_ndc = transformed
    else:
        raise ValueError(f"unsupported coordinate_space: {visual.coordinate_space!r}")
    return panel_ndc_to_axes_fraction(panel_ndc), axes.transAxes


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
    return 72.0 / _logical_figure_dpi(axes.figure)


def _logical_figure_dpi(figure: object) -> float:
    """Return the caller-requested DPI when GUI backends apply device scaling."""
    dpi = getattr(figure, "_original_dpi", getattr(figure, "dpi"))
    return float(dpi)


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
