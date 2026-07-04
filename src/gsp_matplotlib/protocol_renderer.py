"""Matplotlib reference rendering for formal protocol visual models."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, cast

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
    CanvasMetricsSource,
    CanvasSize,
    ColorScale,
    ColorbarGuide,
    PanelTextGuide,
    ResolvedCanvas,
    ResolvedLayoutSnapshot,
    View2D,
    View3D,
    View3DDiagnosticCode,
    project_view3d_data_point,
    validate_mesh_visual_flat_lambert,
)
from gsp_matplotlib.guides import render_axis_guides, render_panel_text_guides
from gsp_matplotlib.layout import resolve_matplotlib_layout_snapshot
from gsp.protocol.visuals import (
    CoordinateSpace,
    DepthMode,
    FontRole,
    ImageInterpolation,
    ImageVisual,
    MeshColorMode,
    MeshShading,
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
    resolved_canvas: ResolvedCanvas
    view_snapshot_id: str | None = None

    @property
    def layout_snapshot_id(self) -> str:
        """Return the resolved layout snapshot id used by this render result."""
        return self.layout_snapshot.snapshot_id


def render_protocol_scene_with_layout(
    *,
    visuals: Iterable[ProtocolVisual],
    view: View2D | None = None,
    view3d: View3D | None = None,
    axis_guides: Iterable[AxisGuide] = (),
    panel_text_guides: Iterable[PanelTextGuide] = (),
    colorbar_guides: Iterable[ColorbarGuide] = (),
    color_scales: Mapping[str, ColorScale] | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
    snapshot_id: str = "layout:matplotlib",
    figure: matplotlib.figure.Figure | None = None,
    axes: matplotlib.axes.Axes | None = None,
    canvas_size: CanvasSize | None = None,
    output_dpi: float | None = None,
    device_scale: float = 1.0,
    view_snapshot_id: str | None = None,
) -> MatplotlibProtocolRenderResult:
    """Render a protocol scene and report the resolved layout snapshot used."""
    if axes is None:
        import matplotlib.pyplot as plt

        if figure is None:
            figure = plt.figure()
            resolved_canvas = _configure_matplotlib_canvas(
                figure,
                canvas_size=canvas_size,
                output_dpi=output_dpi,
                device_scale=device_scale,
            )
            axes = figure.add_subplot()
        else:
            resolved_canvas = _configure_matplotlib_canvas(
                figure,
                canvas_size=canvas_size,
                output_dpi=output_dpi,
                device_scale=device_scale,
            )
            axes = figure.add_subplot()
    elif figure is None:
        figure = cast(matplotlib.figure.Figure, axes.figure)
        resolved_canvas = _configure_matplotlib_canvas(
            figure,
            canvas_size=canvas_size,
            output_dpi=output_dpi,
            device_scale=device_scale,
        )
    else:
        resolved_canvas = _configure_matplotlib_canvas(
            figure,
            canvas_size=canvas_size,
            output_dpi=output_dpi,
            device_scale=device_scale,
        )

    color_scale_map = color_scales if color_scales is not None else {}
    for visual in visuals:
        _render_protocol_visual(
            axes,
            visual,
            view=view,
            color_scales=color_scale_map,
            transform_resources=transform_resources,
            view3d=view3d,
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
    return MatplotlibProtocolRenderResult(
        figure,
        axes,
        snapshot,
        resolved_canvas,
        view_snapshot_id=view_snapshot_id,
    )


def _render_protocol_visual(
    axes: matplotlib.axes.Axes,
    visual: ProtocolVisual,
    *,
    view: View2D | None = None,
    color_scales: Mapping[str, ColorScale] | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
    view3d: View3D | None = None,
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
            axes,
            visual,
            view=view,
            view3d=view3d,
            transform_resources=transform_resources,
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


def _configure_matplotlib_canvas(
    figure: matplotlib.figure.Figure,
    *,
    canvas_size: CanvasSize | None,
    output_dpi: float | None,
    device_scale: float,
) -> ResolvedCanvas:
    if canvas_size is None:
        dpi = output_dpi if output_dpi is not None else _logical_figure_dpi(figure)
        width_in, height_in = figure.get_size_inches()
        requested = CanvasSize.pixel_exact(width_in * dpi, height_in * dpi)
        resolved = requested.resolve(
            output_dpi=dpi,
            device_scale=device_scale,
            metrics_source=CanvasMetricsSource.BACKEND_REPORTED,
        )
    else:
        dpi = output_dpi if output_dpi is not None else canvas_size.reference_dpi
        resolved = canvas_size.resolve(
            output_dpi=dpi,
            device_scale=device_scale,
            metrics_source=CanvasMetricsSource.EXPLICIT,
        )
        figure.set_dpi(dpi)
        figure.set_size_inches(
            resolved.framebuffer_width / dpi,
            resolved.framebuffer_height / dpi,
            forward=True,
        )

    setattr(figure, "_gsp_resolved_canvas", resolved)
    return resolved


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
    segments = np.stack([start_positions, end_positions], axis=1)
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
    view3d: View3D | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
) -> matplotlib.collections.PolyCollection:
    """Render the bounded MeshVisual reference subset into a Matplotlib axes."""
    if visual.canonical_shading() is MeshShading.TEXTURE2D_UNLIT:
        raise NotImplementedError(
            "meshvisual_material_texture2d_unlit_unsupported: Matplotlib "
            "PolyCollection mesh rendering does not support Texture2D sampling"
        )
    if visual.face_color_encoding is not None:
        raise NotImplementedError(
            "Matplotlib MeshVisual scalar face colors are capability-gated"
        )
    color_mode = visual.resolved_color_mode()
    if color_mode is MeshColorMode.VERTEX:
        raise NotImplementedError(
            "Matplotlib MeshVisual vertex colors are capability-gated"
        )
    if visual.color is None:
        raise ValueError("MeshVisual color is required for Matplotlib rendering")
    mesh_color = visual.color

    vertex_depth: npt.NDArray[np.float64] | None = None
    if visual.positions.shape[1] == 3:
        positions, transform, vertex_depth = _render_mesh3d_positions(
            axes, visual, view3d=view3d
        )
    else:
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

    if visual.canonical_shading() is MeshShading.FLAT_LAMBERT:
        facecolors = _resolve_flat_lambert_facecolors(
            visual,
            facecolors,
            view3d=view3d,
        )

    if vertex_depth is not None:
        _validate_mesh3d_opaque_colors(facecolors)
        if visual.depth_test is not DepthMode.DISABLED:
            polygons, facecolors = _mesh3d_depth_polygons(
                projected_positions=positions,
                source_positions=np.asarray(visual.positions, dtype=np.float64),
                faces=visual.faces,
                facecolors=facecolors,
                vertex_depth=vertex_depth,
            )
        else:
            polygons = [
                np.ascontiguousarray(triangle, dtype=np.float32)
                for triangle in triangles
            ]
    else:
        polygons = [
            np.ascontiguousarray(triangle, dtype=np.float32) for triangle in triangles
        ]

    collection = matplotlib.collections.PolyCollection(
        polygons,
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
    canvas_width_px, canvas_height_px = _figure_canvas_size_px(axes.figure)
    if guide.orientation.value == "vertical":
        width = guide.style.ramp_width_px / canvas_width_px
        height = min(
            axes_box.height,
            max(
                guide.style.min_length_px / canvas_height_px,
                axes_box.height * guide.style.length_fraction,
            ),
        )
        gap = guide.style.label_gap_px / canvas_width_px
        y0 = axes_box.y0 + max(0.0, (axes_box.height - height) / 2.0)
        cax_bounds = (
            min(0.965 - width, axes_box.x1 + gap),
            y0,
            width,
            height,
        )
    else:
        height = guide.style.ramp_width_px / canvas_height_px
        width = min(
            axes_box.width,
            max(
                guide.style.min_length_px / canvas_width_px,
                axes_box.width * guide.style.length_fraction,
            ),
        )
        gap = guide.style.label_gap_px / canvas_height_px
        x0 = axes_box.x0 + max(0.0, (axes_box.width - width) / 2.0)
        cax_bounds = (
            x0,
            max(0.035, axes_box.y0 - gap - height),
            width,
            height,
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


def _figure_canvas_size_px(figure: Any) -> tuple[float, float]:
    resolved = getattr(figure, "_gsp_resolved_canvas", None)
    if isinstance(resolved, ResolvedCanvas):
        return resolved.canvas_width_px, resolved.canvas_height_px
    width_in, height_in = figure.get_size_inches()
    dpi = _logical_figure_dpi(figure)
    return float(width_in * dpi), float(height_in * dpi)


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
        if (
            isinstance(visual, TextVisual)
            and visual.coordinate_space == CoordinateSpace.NDC
        ):
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


def _render_mesh3d_positions(
    axes: matplotlib.axes.Axes,
    visual: MeshVisual,
    *,
    view3d: View3D | None,
) -> tuple[npt.NDArray[np.float64], matplotlib.transforms.Transform, npt.NDArray[np.float64]]:
    if visual.transform is not None:
        raise NotImplementedError(
            f"{View3DDiagnosticCode.MESH3D_TRANSFORM_UNSUPPORTED.value}: "
            "Matplotlib MeshVisual 3D path does not apply 2D affine transforms"
        )
    source = np.asarray(visual.positions, dtype=np.float64)
    if visual.coordinate_space == CoordinateSpace.DATA:
        if view3d is None:
            raise NotImplementedError(
                f"{View3DDiagnosticCode.MESH3D_REQUIRES_VIEW3D.value}: "
                "Matplotlib MeshVisual DATA positions3d require View3D"
            )
        aspect_ratio = _axes_pixel_aspect_ratio(axes)
        panel_ndc3 = np.asarray(
            [
                project_view3d_data_point(
                    view3d, tuple(point), aspect_ratio=aspect_ratio
                )
                for point in source
            ],
            dtype=np.float64,
        )
    elif visual.coordinate_space == CoordinateSpace.NDC:
        panel_ndc3 = source
    else:
        raise NotImplementedError(
            f"{View3DDiagnosticCode.MESH3D_COORDINATE_SPACE_UNSUPPORTED.value}: "
            f"unsupported MeshVisual 3D coordinate_space {visual.coordinate_space!r}"
        )
    return panel_ndc_to_axes_fraction(panel_ndc3[:, :2]), axes.transAxes, panel_ndc3[:, 2]


def _axes_pixel_aspect_ratio(axes: matplotlib.axes.Axes) -> float:
    axes_box = axes.get_position()
    canvas_width_px, canvas_height_px = _figure_canvas_size_px(axes.figure)
    width = max(float(axes_box.width) * canvas_width_px, 1.0)
    height = max(float(axes_box.height) * canvas_height_px, 1.0)
    return width / height


def _validate_mesh3d_opaque_colors(colors: npt.NDArray[Any]) -> None:
    alpha = np.asarray(colors)[:, 3]
    if colors.dtype == np.dtype(np.uint8):
        translucent = bool(np.any(alpha < 255))
    else:
        translucent = bool(np.any(alpha < 1.0))
    if translucent:
        raise NotImplementedError(
            f"{View3DDiagnosticCode.MESH3D_ALPHA_NOT_STRICT.value}: "
            "Matplotlib MeshVisual 3D depth path requires opaque face colors"
        )


def _mesh3d_depth_polygons(
    *,
    projected_positions: npt.NDArray[np.float64],
    source_positions: npt.NDArray[np.float64],
    faces: npt.NDArray[np.integer],
    facecolors: npt.NDArray[Any],
    vertex_depth: npt.NDArray[np.float64],
) -> tuple[list[npt.NDArray[np.float32]], npt.NDArray[Any]]:
    """Return painter-sorted 3D polygons, merging simple triangulated quads.

    Matplotlib has no 3D depth buffer in this protocol reference path, so 3D
    meshes use a painter fallback. Sorting every triangle independently can
    split a logical quad face while orbiting a cube. Adjacent coplanar triangles
    with identical resolved color are therefore drawn as one polygon.
    """
    edge_to_faces: dict[tuple[int, int], list[int]] = {}
    for face_index, face in enumerate(faces):
        indices = [int(index) for index in face]
        for start, stop in ((0, 1), (1, 2), (2, 0)):
            edge = (
                min(indices[start], indices[stop]),
                max(indices[start], indices[stop]),
            )
            edge_to_faces.setdefault(edge, []).append(face_index)

    visited = np.zeros(faces.shape[0], dtype=np.bool_)
    polygons: list[npt.NDArray[np.float32]] = []
    colors: list[npt.NDArray[Any]] = []
    depths: list[float] = []

    for face_index, face in enumerate(faces):
        if visited[face_index]:
            continue
        visited[face_index] = True
        partner = _mesh3d_coplanar_quad_partner(
            face_index=face_index,
            source_positions=source_positions,
            faces=faces,
            facecolors=facecolors,
            edge_to_faces=edge_to_faces,
            visited=visited,
        )
        if partner is None:
            face_indices = np.asarray(face, dtype=np.int64)
            polygon = projected_positions[face_indices]
            depth = float(np.mean(vertex_depth[face_indices]))
        else:
            visited[partner] = True
            face_indices = _mesh3d_projected_quad_indices(
                projected_positions=projected_positions,
                first_face=face,
                second_face=faces[partner],
            )
            polygon = projected_positions[face_indices]
            depth = float(np.mean(vertex_depth[face_indices]))
        polygons.append(np.ascontiguousarray(polygon, dtype=np.float32))
        colors.append(np.asarray(facecolors[face_index]))
        depths.append(depth)

    order = np.argsort(-np.asarray(depths, dtype=np.float64), kind="stable")
    sorted_polygons = [polygons[int(index)] for index in order]
    sorted_colors = np.asarray([colors[int(index)] for index in order], dtype=facecolors.dtype)
    return sorted_polygons, sorted_colors


def _mesh3d_coplanar_quad_partner(
    *,
    face_index: int,
    source_positions: npt.NDArray[np.float64],
    faces: npt.NDArray[np.integer],
    facecolors: npt.NDArray[Any],
    edge_to_faces: dict[tuple[int, int], list[int]],
    visited: npt.NDArray[np.bool_],
) -> int | None:
    face = faces[face_index]
    indices = [int(index) for index in face]
    candidates: list[int] = []
    for start, stop in ((0, 1), (1, 2), (2, 0)):
        edge = (
            min(indices[start], indices[stop]),
            max(indices[start], indices[stop]),
        )
        candidates.extend(
            index
            for index in edge_to_faces.get(edge, ())
            if index != face_index and not visited[index]
        )
    for candidate in candidates:
        if not _mesh3d_facecolors_match(facecolors[face_index], facecolors[candidate]):
            continue
        if _mesh3d_faces_form_coplanar_quad(
            source_positions, face, faces[candidate]
        ):
            return int(candidate)
    return None


def _mesh3d_facecolors_match(first: npt.NDArray[Any], second: npt.NDArray[Any]) -> bool:
    if np.issubdtype(np.asarray(first).dtype, np.floating) or np.issubdtype(
        np.asarray(second).dtype, np.floating
    ):
        return bool(np.allclose(first, second, rtol=1.0e-6, atol=1.0e-8))
    return bool(np.array_equal(first, second))


def _mesh3d_faces_form_coplanar_quad(
    source_positions: npt.NDArray[np.float64],
    first_face: npt.NDArray[np.integer],
    second_face: npt.NDArray[np.integer],
) -> bool:
    first = [int(index) for index in first_face]
    second = [int(index) for index in second_face]
    unique_indices = tuple(dict.fromkeys((*first, *second)))
    if len(set(first).intersection(second)) != 2 or len(unique_indices) != 4:
        return False
    first_normal = _mesh3d_face_normal(source_positions[np.asarray(first)])
    second_normal = _mesh3d_face_normal(source_positions[np.asarray(second)])
    if first_normal is None or second_normal is None:
        return False
    if abs(float(np.dot(first_normal, second_normal))) < 1.0 - 1.0e-6:
        return False
    plane_point = source_positions[first[0]]
    distances = (source_positions[np.asarray(unique_indices)] - plane_point) @ first_normal
    return bool(np.all(np.abs(distances) <= 1.0e-6))


def _mesh3d_face_normal(
    vertices: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64] | None:
    normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
    norm = float(np.linalg.norm(normal))
    if norm <= 1.0e-12:
        return None
    return np.asarray(normal / norm, dtype=np.float64)


def _mesh3d_projected_quad_indices(
    *,
    projected_positions: npt.NDArray[np.float64],
    first_face: npt.NDArray[np.integer],
    second_face: npt.NDArray[np.integer],
) -> npt.NDArray[np.int64]:
    unique_indices = np.asarray(
        tuple(dict.fromkeys((*[int(index) for index in first_face], *[int(index) for index in second_face]))),
        dtype=np.int64,
    )
    points = projected_positions[unique_indices]
    center = np.mean(points, axis=0)
    angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
    return unique_indices[np.argsort(angles, kind="stable")]


def _resolve_flat_lambert_facecolors(
    visual: MeshVisual,
    facecolors: npt.NDArray[Any],
    *,
    view3d: View3D | None,
) -> npt.NDArray[np.float32]:
    validate_mesh_visual_flat_lambert(visual, view3d=view3d)
    if view3d is None:
        raise ValueError("flat_lambert requires View3D")
    base = np.asarray(_rgba_for_matplotlib(facecolors), dtype=np.float32)
    normals = np.asarray(visual.normalized_face_normals(), dtype=np.float64)
    light_factor = np.full(
        (normals.shape[0],),
        float(view3d.ambient_light_intensity),
        dtype=np.float64,
    )
    if view3d.directional_light is not None:
        light_direction = np.asarray(
            view3d.directional_light.direction_to_light,
            dtype=np.float64,
        )
        light_direction = light_direction / np.linalg.norm(light_direction)
        lambert = np.maximum(0.0, normals @ light_direction)
        light_factor = light_factor + (
            float(view3d.directional_light.intensity) * lambert
        )
    light_factor = np.clip(light_factor, 0.0, 1.0)
    resolved = base.copy()
    resolved[:, :3] = np.clip(base[:, :3] * light_factor[:, np.newaxis], 0.0, 1.0)
    resolved[:, 3] = base[:, 3]
    return np.ascontiguousarray(resolved, dtype=np.float32)


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
    resolved = getattr(axes.figure, "_gsp_resolved_canvas", None)
    if isinstance(resolved, ResolvedCanvas):
        return resolved.framebuffer_per_canvas_px * 72.0 / resolved.output_dpi
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
