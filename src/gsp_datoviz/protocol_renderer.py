"""Datoviz v0.4 protocol adapter slice.

This module targets the C-shaped top-level Datoviz facade exposed by the local
v0.4 checkout, for example ``dvz_scene`` and ``dvz_visual_set_data``. It does
not use the older ``datoviz.App`` or ``datoviz.visuals`` wrapper APIs.
"""

from __future__ import annotations

import ctypes
from collections.abc import Mapping
from dataclasses import dataclass, field
from dataclasses import replace
import os
from pathlib import Path
import tempfile
from types import ModuleType
from typing import Any, Literal, cast
from zlib import crc32

import numpy as np
import numpy.typing as npt

from gsp.protocol import (
    AffineTransform2DResource,
    CapabilitySnapshot,
    ColorMapId,
    ColorScale,
    ColorbarGuide,
    ColorbarOrientation,
    ColorbarPlacement,
    ImageOrigin,
    ImageVisual,
    MeshColorMode,
    MeshVisual,
    MarkerShape,
    MarkerVisual,
    PathVisual,
    PointVisual,
    SegmentVisual,
    TextVisual,
    TextAnchorX,
    TextAnchorY,
    StrokeCap,
    StrokeJoin,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryRequest,
    QueryResult,
    QueryScope,
    QueryStatus,
    SCALAR_COLOR_QUERY_PAYLOAD_KIND,
    ScalarColorQueryPayload,
    ScalarColorSlot,
    TRANSFORM_QUERY_PAYLOAD_KIND,
    View2D,
    VisualFamily,
    VisualTransformBinding,
)
from gsp.protocol.color_mapping import (
    map_scalar_value,
    map_scalar_values,
    resolve_color_scale,
)
from gsp.protocol.visuals import CoordinateSpace, ImageInterpolation
from gsp_datoviz.capabilities import (
    datoviz_v04_axis_provider_capability,
    datoviz_v04_capability_snapshot,
    datoviz_v04_capture_diagnostics,
    datoviz_v04_capture_ready,
)
from gsp_datoviz.query import (
    decode_dvz_query_result,
    datoviz_v04_query_binding_diagnostics,
    datoviz_v04_query_binding_ready,
)


_REQUIRED_DVZ_V04_FUNCTIONS = (
    "dvz_scene",
    "dvz_figure",
    "dvz_panel_full",
    "dvz_panel_add_visual",
    "dvz_panel_set_domain",
    "dvz_point",
    "dvz_image",
    "dvz_visual_set_data",
    "dvz_visual_set_texture",
)

_REQUIRED_DVZ_SAMPLED_FIELD_FUNCTIONS = (
    "dvz_sampled_field_desc",
    "dvz_field_data_view",
    "dvz_sampled_field",
    "dvz_sampled_field_set_data",
    "dvz_visual_set_field",
)

_REQUIRED_DVZ_MARKER_FUNCTIONS = (
    "dvz_marker",
    "dvz_marker_style",
    "dvz_marker_set_style",
)

_REQUIRED_DVZ_SEGMENT_FUNCTIONS = (
    "dvz_segment",
    "dvz_segment_set_caps",
)

_REQUIRED_DVZ_PATH_FUNCTIONS = (
    "dvz_path",
    "dvz_path_set_subpaths",
    "dvz_path_set_caps",
    "dvz_path_set_join",
)


_REQUIRED_DVZ_MESH_FUNCTIONS = (
    "dvz_mesh",
    "dvz_visual_set_data",
    "dvz_visual_set_index_data",
    "dvz_visual_set_depth_test",
)

_OPTIONAL_UNVERIFIED_DVZ_MESH_FUNCTIONS: tuple[str, ...] = ()


_REQUIRED_DVZ_TEXT_FUNCTIONS = (
    "dvz_text",
    "dvz_text_set_string",
    "dvz_text_style",
    "dvz_text_set_style",
    "dvz_text_set_placement",
)

_OPTIONAL_UNVERIFIED_DVZ_TEXT_FUNCTIONS: tuple[str, ...] = ()

DVZ_FIELD_DIM_2D = 0
DVZ_FIELD_FORMAT_RGBA8_UNORM = 22
DVZ_FIELD_SEMANTIC_COLOR = 4
DVZ_COLOR_ROLE_SRGB_COLOR = 1
DVZ_SCENE_TARGET_NONE = 0
DVZ_SCENE_TARGET_ITEM = 2
DVZ_QUERY_HIT_FRONTMOST = 0
DVZ_QUERY_PROFILE_UNSUPPORTED = 0
DVZ_QUERY_CAPABILITY_ITEM = 0x02
DVZ_QUERY_CAPABILITY_PIXEL = 0x10
DVZ_COORD_VIEW = 0
DVZ_COORD_DATA = 1
DVZ_SHAPE_ASPECT_FILLED = 0
DVZ_SHAPE_ASPECT_OUTLINE = 2
DVZ_ALPHA_BLENDED = 1
DVZ_IMAGE_SAMPLING_LINEAR = 0
DVZ_IMAGE_SAMPLING_NEAREST = 1
DVZ_COLOR_PIPELINE_LINEAR_SRGB = 0
DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND = 1
DVZ_SCALE_CONTINUOUS = 0
DVZ_BUILTIN_COLORMAP_VIRIDIS = 1
DVZ_BUILTIN_COLORMAP_MAGMA = 2
DVZ_BUILTIN_COLORMAP_PLASMA = 3
DVZ_BUILTIN_COLORMAP_INFERNO = 4
DVZ_BUILTIN_COLORMAP_CIVIDIS = 5
DVZ_BUILTIN_COLORMAP_GRAY = 7
DVZ_SEGMENT_CAP_ROUND = 1
DVZ_SEGMENT_CAP_SQUARE = 4
DVZ_SEGMENT_CAP_BUTT = 5
DVZ_PATH_JOIN_MITER = 0
DVZ_PATH_JOIN_ROUND = 1
DVZ_PATH_JOIN_BEVEL = 2
DVZ_TEXT_PLACEMENT_SCREEN = 0
DVZ_TEXT_PLACEMENT_DATA = 1
DVZ_COLORBAR_ORIENTATION_VERTICAL = 0
DVZ_COLORBAR_ORIENTATION_HORIZONTAL = 1
DVZ_COLORBAR_PLACEMENT_ATTACHED = 0
DVZ_COLORBAR_PLACEMENT_DETACHED = 1
DVZ_PLACEMENT_SPACE_PANEL = 0
DVZ_HORIZONTAL_ANCHOR_RIGHT = 2
DVZ_VERTICAL_ANCHOR_CENTER = 1
DVZ_SCENE_ANCHOR_PANEL_TOP = 2
DVZ_SCENE_ANCHOR_PANEL_LEFT = 4
DVZ_SCENE_ANCHOR_PANEL_RIGHT = 6
DVZ_SCENE_ANCHOR_PANEL_BOTTOM = 8
DVZ_SCENE_ANCHOR_DATA = 10
DVZ_TEXT_RENDERER_MSDF_ATLAS = 3
DEFAULT_BACKGROUND_RGBA8 = (255, 255, 255, 255)

DatovizColorPipeline = Literal["linear_srgb", "legacy_srgb_blend"]


class _CompatDvzTextPlacement(ctypes.Structure):
    """Header-matched fallback for builds that omit the Python placement factory."""

    _fields_ = (
        ("struct_size", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("mode", ctypes.c_int),
        ("anchor", ctypes.c_int),
        ("position", ctypes.c_double * 3),
        ("offset", ctypes.c_float * 2),
        ("text_anchor", ctypes.c_float * 2),
        ("has_text_anchor", ctypes.c_bool),
        ("angle", ctypes.c_float),
        ("depth_test", ctypes.c_bool),
    )

_MARKER_SHAPE_FALLBACKS = {
    MarkerShape.DISC: 0,
    MarkerShape.SQUARE: 1,
    MarkerShape.TRIANGLE: 2,
    MarkerShape.DIAMOND: 3,
    MarkerShape.CROSS: 4,
}

_MARKER_SHAPE_NAMES = {
    MarkerShape.DISC: "DVZ_MARKER_SHAPE_DISC",
    MarkerShape.SQUARE: "DVZ_MARKER_SHAPE_SQUARE",
    MarkerShape.TRIANGLE: "DVZ_MARKER_SHAPE_TRIANGLE",
    MarkerShape.DIAMOND: "DVZ_MARKER_SHAPE_DIAMOND",
    MarkerShape.CROSS: "DVZ_MARKER_SHAPE_CROSS",
}

_STROKE_CAP_FALLBACKS = {
    StrokeCap.BUTT: DVZ_SEGMENT_CAP_BUTT,
    StrokeCap.ROUND: DVZ_SEGMENT_CAP_ROUND,
    StrokeCap.SQUARE: DVZ_SEGMENT_CAP_SQUARE,
}

_STROKE_CAP_NAMES = {
    StrokeCap.BUTT: "DVZ_SEGMENT_CAP_BUTT",
    StrokeCap.ROUND: "DVZ_SEGMENT_CAP_ROUND",
    StrokeCap.SQUARE: "DVZ_SEGMENT_CAP_SQUARE",
}

_STROKE_JOIN_FALLBACKS = {
    StrokeJoin.MITER: DVZ_PATH_JOIN_MITER,
    StrokeJoin.ROUND: DVZ_PATH_JOIN_ROUND,
    StrokeJoin.BEVEL: DVZ_PATH_JOIN_BEVEL,
}

_STROKE_JOIN_NAMES = {
    StrokeJoin.MITER: "DVZ_PATH_JOIN_MITER",
    StrokeJoin.ROUND: "DVZ_PATH_JOIN_ROUND",
    StrokeJoin.BEVEL: "DVZ_PATH_JOIN_BEVEL",
}

_VISUAL_ATTRIBUTE_ALIASES = {
    "diameter_px": ("diameter",),
    "stroke_width_px": ("stroke_width",),
}

_BUILTIN_COLORMAP_NAMES = {
    ColorMapId.GRAY: ("DVZ_BUILTIN_COLORMAP_GRAY", DVZ_BUILTIN_COLORMAP_GRAY),
    ColorMapId.VIRIDIS: (
        "DVZ_BUILTIN_COLORMAP_VIRIDIS",
        DVZ_BUILTIN_COLORMAP_VIRIDIS,
    ),
    ColorMapId.MAGMA: ("DVZ_BUILTIN_COLORMAP_MAGMA", DVZ_BUILTIN_COLORMAP_MAGMA),
    ColorMapId.PLASMA: ("DVZ_BUILTIN_COLORMAP_PLASMA", DVZ_BUILTIN_COLORMAP_PLASMA),
    ColorMapId.INFERNO: (
        "DVZ_BUILTIN_COLORMAP_INFERNO",
        DVZ_BUILTIN_COLORMAP_INFERNO,
    ),
    ColorMapId.CIVIDIS: (
        "DVZ_BUILTIN_COLORMAP_CIVIDIS",
        DVZ_BUILTIN_COLORMAP_CIVIDIS,
    ),
}


class DatovizV04Unavailable(RuntimeError):
    """Raised when the imported Datoviz facade is not the expected v0.4 shape."""


class DatovizV04Unsupported(ValueError):
    """Raised when a GSP v0.1 visual asks for semantics this slice does not support."""


def is_datoviz_v04_facade(module: ModuleType | Any) -> bool:
    """Return whether a module-like object exposes the required v0.4 facade."""
    return all(hasattr(module, name) for name in _REQUIRED_DVZ_V04_FUNCTIONS)


def datoviz_v04_sampled_field_ready(module: ModuleType | Any) -> bool:
    """Return whether a facade exposes the sampled-field image binding path."""
    return not datoviz_v04_sampled_field_diagnostics(module)


def datoviz_v04_sampled_field_diagnostics(module: ModuleType | Any) -> tuple[str, ...]:
    """Return missing sampled-field binding requirements."""
    return tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_SAMPLED_FIELD_FUNCTIONS
        if not hasattr(module, name)
    )


def datoviz_v04_mesh_diagnostics(module: ModuleType | Any) -> tuple[str, ...]:
    """Return why Datoviz MeshVisual rendering is disabled for this slice."""
    diagnostics = [
        f"missing {name}"
        for name in _REQUIRED_DVZ_MESH_FUNCTIONS
        if not hasattr(module, name)
    ]
    diagnostics.extend(
        f"unverified {name}"
        for name in _OPTIONAL_UNVERIFIED_DVZ_MESH_FUNCTIONS
        if not hasattr(module, name)
    )
    return tuple(diagnostics)


def datoviz_v04_mesh_ready(module: ModuleType | Any) -> bool:
    """Return whether this adapter slice may render MeshVisual through Datoviz."""
    return not datoviz_v04_mesh_diagnostics(module)


def datoviz_v04_text_diagnostics(module: ModuleType | Any) -> tuple[str, ...]:
    """Return why Datoviz TextVisual rendering is disabled for this slice."""
    diagnostics = [
        f"missing {name}"
        for name in _REQUIRED_DVZ_TEXT_FUNCTIONS
        if not hasattr(module, name)
    ]
    diagnostics.extend(
        f"unverified {name}"
        for name in _OPTIONAL_UNVERIFIED_DVZ_TEXT_FUNCTIONS
        if not hasattr(module, name)
    )
    return tuple(diagnostics)


def datoviz_v04_text_ready(module: ModuleType | Any) -> bool:
    """Return whether this adapter slice may render TextVisual through Datoviz."""
    return not datoviz_v04_text_diagnostics(module)


def import_datoviz_v04() -> ModuleType:
    """Import Datoviz and validate the C-shaped v0.4 facade."""
    try:
        import datoviz as dvz
        if not is_datoviz_v04_facade(dvz):
            missing = [
                name for name in _REQUIRED_DVZ_V04_FUNCTIONS if not hasattr(dvz, name)
            ]
            raise DatovizV04Unavailable(
                f"Datoviz facade is missing v0.4 functions: {missing}"
            )
    except ModuleNotFoundError as exc:
        raise DatovizV04Unavailable("Datoviz is not importable") from exc
    except (OSError, RuntimeError) as exc:
        raise DatovizV04Unavailable(f"Datoviz is not importable: {exc}") from exc
    return cast(ModuleType, dvz)


def capability_snapshot() -> CapabilitySnapshot:
    """Return the GSP capability surface for the current bounded adapter slice."""
    return datoviz_v04_capability_snapshot()


def _datoviz_color_pipeline_value(
    dvz: Any, color_pipeline: DatovizColorPipeline
) -> int:
    """Return the Datoviz enum value for a GSP color-pipeline option."""
    if color_pipeline == "linear_srgb":
        return int(
            getattr(
                dvz, "DVZ_COLOR_PIPELINE_LINEAR_SRGB", DVZ_COLOR_PIPELINE_LINEAR_SRGB
            )
        )
    if color_pipeline == "legacy_srgb_blend":
        return int(
            getattr(
                dvz,
                "DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND",
                DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND,
            )
        )
    raise ValueError(f"unsupported Datoviz color pipeline: {color_pipeline!r}")


def _set_figure_color_pipeline(
    dvz: Any, figure: Any, color_pipeline: DatovizColorPipeline
) -> None:
    """Set the Datoviz figure color pipeline when the facade supports or requires it."""
    value = _datoviz_color_pipeline_value(dvz, color_pipeline)
    setter = getattr(dvz, "dvz_figure_set_color_pipeline", None)
    if setter is None:
        return
    setter(figure, value)


@dataclass
class _ScalarVisualData:
    """Scene-owned scalar color data retained for semantic query payloads."""

    visual_id: str
    visual_family: VisualFamily | str
    item_kind: str
    color_slot: ScalarColorSlot
    values: npt.NDArray[np.float64]
    color_scale: ColorScale
    alpha: float = 1.0


@dataclass
class DatovizV04ProtocolRenderer:
    """Minimal point/image renderer using Datoviz v0.4 top-level functions."""

    dvz: Any = None
    color_scales: Mapping[str, ColorScale] | None = None
    width: int = 800
    height: int = 600
    background_rgba8: tuple[int, int, int, int] = DEFAULT_BACKGROUND_RGBA8
    color_pipeline: DatovizColorPipeline = "linear_srgb"
    view: View2D | None = None
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None
    scene: Any = field(init=False)
    figure: Any = field(init=False)
    panel: Any = field(init=False)
    app: Any | None = field(default=None, init=False)
    offscreen_view: Any | None = field(default=None, init=False)
    live_view: Any | None = field(default=None, init=False)
    visuals: dict[str, Any] = field(default_factory=dict, init=False)
    sampled_fields: dict[str, Any] = field(default_factory=dict, init=False)
    native_scales: dict[str, Any] = field(default_factory=dict, init=False)
    native_colormaps: dict[str, Any] = field(default_factory=dict, init=False)
    colorbars: dict[str, Any] = field(default_factory=dict, init=False)
    scalar_visuals: dict[str, _ScalarVisualData] = field(default_factory=dict, init=False)
    transform_adaptations: dict[str, tuple[str, ...]] = field(
        default_factory=dict, init=False
    )
    _closed: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.dvz is None:
            self.dvz = import_datoviz_v04()
        elif not is_datoviz_v04_facade(self.dvz):
            missing = [
                name
                for name in _REQUIRED_DVZ_V04_FUNCTIONS
                if not hasattr(self.dvz, name)
            ]
            raise DatovizV04Unavailable(
                f"Datoviz facade is missing v0.4 functions: {missing}"
            )

        self.scene = self.dvz.dvz_scene()
        self.figure = self.dvz.dvz_figure(self.scene, self.width, self.height, 0)
        _set_figure_color_pipeline(self.dvz, self.figure, self.color_pipeline)
        self.panel = self.dvz.dvz_panel_full(self.figure)
        _set_panel_background_color(self.dvz, self.panel, self.background_rgba8)
        _configure_ndc_panel_view2d(self.dvz, self.panel)
        if self.view is not None:
            self.apply_datoviz_data_view2d(self.view)

    def capabilities(self) -> CapabilitySnapshot:
        """Return the capability snapshot for this adapter slice."""
        return datoviz_v04_capability_snapshot(self.dvz)

    def close(self) -> None:
        """Destroy the scene when the facade exposes a destroy helper."""
        if self._closed:
            return
        destroy_app = getattr(self.dvz, "dvz_app_destroy", None)
        if destroy_app is not None and self.app is not None:
            destroy_app(self.app)
        destroy = getattr(self.dvz, "dvz_scene_destroy", None)
        if destroy is not None:
            destroy(self.scene)
        self._closed = True

    def __enter__(self) -> "DatovizV04ProtocolRenderer":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def add_point_visual(self, visual: PointVisual) -> Any:
        """Create and attach a Datoviz point visual."""
        positions = _positions_3d(
            _adapt_visual_positions(
                visual.id,
                visual.positions,
                visual.transform,
                visual.coordinate_space,
                self.view,
                self.transform_resources,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        colors = _point_colors(visual, color_scales=self.color_scales)
        diameters = _diameters_from_pixel_diameters(visual.sizes, positions.shape[0])

        dvz_visual = self.dvz.dvz_point(self.scene, 0)
        _set_filled_point_style(self.dvz, dvz_visual)
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, colors)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_data(self.dvz, dvz_visual, "diameter_px", diameters)
        self.dvz.dvz_panel_add_visual(
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=_datoviz_visual_coord_space(visual.coordinate_space),
                z_layer=0,
            ),
        )
        self.visuals[visual.id] = dvz_visual
        if visual.color_encoding is not None:
            scale = resolve_color_scale(
                self.color_scales, visual.color_encoding.color_scale_id
            )
            self.scalar_visuals[visual.id] = _ScalarVisualData(
                visual_id=visual.id,
                visual_family=VisualFamily.POINT,
                item_kind="point",
                color_slot=ScalarColorSlot.COLOR,
                values=np.asarray(visual.color_encoding.values, dtype=np.float64),
                color_scale=scale,
                alpha=float(visual.color_encoding.alpha),
            )
        return dvz_visual

    def add_marker_visual(self, visual: MarkerVisual) -> Any:
        """Create and attach a Datoviz marker visual."""
        marker_diagnostics = _datoviz_marker_diagnostics(self.dvz)
        if marker_diagnostics:
            raise DatovizV04Unsupported(
                f"Datoviz v0.4 marker facade is unavailable: {', '.join(marker_diagnostics)}"
            )

        positions = _positions_3d(
            _adapt_visual_positions(
                visual.id,
                visual.positions,
                visual.transform,
                visual.coordinate_space,
                self.view,
                self.transform_resources,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        fill_colors = _marker_fill_colors(visual, color_scales=self.color_scales)
        diameters = _diameters_from_pixel_diameters(visual.sizes, positions.shape[0])
        shape_values = visual.shape_values()
        angles = np.ascontiguousarray(visual.angle_values())
        shapes = _marker_shapes(self.dvz, shape_values)

        dvz_visual = self.dvz.dvz_marker(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz marker visual allocation failed")
        _set_marker_style(
            self.dvz, dvz_visual, visual.stroke_color, visual.stroke_width
        )
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, fill_colors)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", fill_colors)
        _set_visual_data(self.dvz, dvz_visual, "diameter_px", diameters)
        _set_visual_data(self.dvz, dvz_visual, "angle", angles)
        _set_visual_data(self.dvz, dvz_visual, "shape", shapes)
        self.dvz.dvz_panel_add_visual(
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=_datoviz_visual_coord_space(visual.coordinate_space),
                z_layer=0,
            ),
        )
        self.visuals[visual.id] = dvz_visual
        if visual.fill_color_encoding is not None:
            scale = resolve_color_scale(
                self.color_scales, visual.fill_color_encoding.color_scale_id
            )
            self.scalar_visuals[visual.id] = _ScalarVisualData(
                visual_id=visual.id,
                visual_family="marker",
                item_kind="marker",
                color_slot=ScalarColorSlot.FILL,
                values=np.asarray(
                    visual.fill_color_encoding.values, dtype=np.float64
                ),
                color_scale=scale,
                alpha=float(visual.fill_color_encoding.alpha),
            )
        return dvz_visual

    def add_segment_visual(self, visual: SegmentVisual) -> Any:
        """Create and attach a Datoviz segment visual."""
        segment_diagnostics = _datoviz_segment_diagnostics(self.dvz)
        if segment_diagnostics:
            raise DatovizV04Unsupported(
                f"Datoviz v0.4 segment facade is unavailable: {', '.join(segment_diagnostics)}"
            )

        start_positions = _positions_3d(
            _adapt_visual_positions(
                visual.id,
                visual.start_positions,
                visual.transform,
                visual.coordinate_space,
                self.view,
                self.transform_resources,
            )
        )
        end_positions = _positions_3d(
            _adapt_visual_positions(
                visual.id,
                visual.end_positions,
                visual.transform,
                visual.coordinate_space,
                self.view,
                self.transform_resources,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        colors = _rgba8(visual.colors)
        widths = np.ascontiguousarray(visual.width_values())

        dvz_visual = self.dvz.dvz_segment(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz segment visual allocation failed")
        cap = _stroke_cap_value(self.dvz, visual.cap)
        result = self.dvz.dvz_segment_set_caps(dvz_visual, cap, cap)
        if result not in (0, None, True):
            raise DatovizV04Unsupported("Datoviz segment cap configuration failed")
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, colors)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position_start", start_positions)
        _set_visual_data(self.dvz, dvz_visual, "position_end", end_positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_data(self.dvz, dvz_visual, "stroke_width_px", widths)
        self.dvz.dvz_panel_add_visual(
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=_datoviz_visual_coord_space(visual.coordinate_space),
                z_layer=0,
            ),
        )
        self.visuals[visual.id] = dvz_visual
        return dvz_visual

    def add_path_visual(self, visual: PathVisual) -> Any:
        """Create and attach a Datoviz path visual."""
        path_diagnostics = _datoviz_path_diagnostics(self.dvz)
        if path_diagnostics:
            raise DatovizV04Unsupported(
                f"Datoviz v0.4 path facade is unavailable: {', '.join(path_diagnostics)}"
            )

        positions = _positions_3d(
            _adapt_visual_positions(
                visual.id,
                visual.positions,
                visual.transform,
                visual.coordinate_space,
                self.view,
                self.transform_resources,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        colors = _expand_path_colors(visual)
        widths = _expand_path_widths(visual)
        subpaths = np.ascontiguousarray(np.array(visual.path_lengths, dtype=np.uint32))

        dvz_visual = self.dvz.dvz_path(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz path visual allocation failed")
        cap = _stroke_cap_value(self.dvz, visual.cap)
        cap_result = self.dvz.dvz_path_set_caps(dvz_visual, cap, cap)
        if cap_result not in (0, None, True):
            raise DatovizV04Unsupported("Datoviz path cap configuration failed")
        join_result = self.dvz.dvz_path_set_join(
            dvz_visual,
            _stroke_join_value(self.dvz, visual.join),
            float(visual.miter_limit),
        )
        if join_result not in (0, None, True):
            raise DatovizV04Unsupported("Datoviz path join configuration failed")
        subpath_result = _set_path_subpaths(
            self.dvz, dvz_visual, len(visual.path_lengths), subpaths
        )
        if subpath_result not in (0, None, True):
            raise DatovizV04Unsupported("Datoviz path subpath configuration failed")
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, colors)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_data(self.dvz, dvz_visual, "stroke_width_px", widths)
        self.dvz.dvz_panel_add_visual(
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=_datoviz_visual_coord_space(visual.coordinate_space),
                z_layer=0,
            ),
        )
        self.visuals[visual.id] = dvz_visual
        return dvz_visual

    def add_image_visual(self, visual: ImageVisual) -> Any:
        """Create and attach a Datoviz image visual for RGBA/RGB uint8 images."""
        if visual.coordinate_space != CoordinateSpace.NDC:
            raise DatovizV04Unsupported(
                "Datoviz v0.4 slice currently supports NDC image extents only"
            )
        pixels = _rgba8_image_visual(visual, color_scales=self.color_scales)
        positions = _image_positions(visual.extent)
        texcoords = _image_texcoords(visual.origin)
        height, width = pixels.shape[:2]

        dvz_visual = self.dvz.dvz_image(self.scene, 0)
        _set_image_sampling(self.dvz, dvz_visual, visual.interpolation)
        _set_query_capabilities(
            self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM | DVZ_QUERY_CAPABILITY_PIXEL
        )
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "texcoords", texcoords)
        if datoviz_v04_sampled_field_ready(self.dvz):
            sampled_field = self._create_rgba8_sampled_field(pixels, width, height)
            if not _set_visual_field(self.dvz, dvz_visual, "field", sampled_field):
                raise DatovizV04Unsupported(
                    "Datoviz sampled-field image binding failed"
                )
            self.sampled_fields[visual.id] = sampled_field
        else:
            self.dvz.dvz_visual_set_texture(dvz_visual, pixels, width, height)
        self.dvz.dvz_panel_add_visual(
            self.panel,
            dvz_visual,
            _visual_attach_desc(self.dvz, coord_space="view", z_layer=0),
        )
        self.visuals[visual.id] = dvz_visual
        if visual.color_scale_id is not None:
            scale = resolve_color_scale(self.color_scales, visual.color_scale_id)
            self.scalar_visuals[visual.id] = _ScalarVisualData(
                visual_id=visual.id,
                visual_family=VisualFamily.IMAGE,
                item_kind="texel",
                color_slot=ScalarColorSlot.IMAGE,
                values=np.asarray(visual.image, dtype=np.float64),
                color_scale=scale,
            )
        return dvz_visual

    def add_mesh_visual(self, visual: MeshVisual) -> Any:
        """Create and attach a bounded Datoviz triangle mesh visual."""
        if visual.positions.shape[1] != 2:
            raise DatovizV04Unsupported(
                "Datoviz v0.4 MeshVisual strict adapter is limited to 2D positions "
                "until 3D camera semantics are accepted"
            )
        diagnostics = datoviz_v04_mesh_diagnostics(self.dvz)
        if diagnostics:
            raise DatovizV04Unsupported(
                "Datoviz v0.4 MeshVisual support is unavailable: "
                + "; ".join(diagnostics)
            )

        adapted_positions = _adapt_visual_positions(
            visual.id,
            visual.positions,
            visual.transform,
            visual.coordinate_space,
            self.view,
            self.transform_resources,
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        positions, colors, indices = _datoviz_mesh_payload(visual, adapted_positions)
        dvz_visual = self.dvz.dvz_mesh(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz mesh visual allocation failed")
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_index_data(self.dvz, dvz_visual, indices)
        result = self.dvz.dvz_visual_set_depth_test(dvz_visual, False)
        if result not in (0, None, True):
            raise DatovizV04Unsupported("Datoviz mesh depth-test disable failed")
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, colors)
        self.dvz.dvz_panel_add_visual(
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=_datoviz_visual_coord_space(visual.coordinate_space),
                z_layer=round(visual.order),
            ),
        )
        self.visuals[visual.id] = dvz_visual
        return dvz_visual

    def add_text_visual(self, visual: TextVisual) -> Any:
        """Create Datoviz retained text objects for bounded S024 text cases."""
        diagnostics = datoviz_v04_text_diagnostics(self.dvz)
        if diagnostics:
            raise DatovizV04Unsupported(
                "Datoviz v0.4 TextVisual support is unavailable: "
                + "; ".join(diagnostics)
            )

        positions = _positions_3d(
            _adapt_visual_positions(
                visual.id,
                visual.positions,
                visual.transform,
                visual.coordinate_space,
                self.view,
                self.transform_resources,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        colors = _rgba8(visual.rgba_values())
        sizes = visual.font_size_values()
        rotations = visual.rotation_values()
        anchor_x = visual.anchor_x_values()
        anchor_y = visual.anchor_y_values()
        mode = _text_placement_mode_value(self.dvz, visual.coordinate_space)
        texts: list[Any] = []

        for index, text_value in enumerate(visual.texts):
            text = self.dvz.dvz_text(self.panel, 0)
            if text is None:
                raise DatovizV04Unsupported("Datoviz text object allocation failed")

            style = self.dvz.dvz_text_style()
            style.size_px = float(sizes[index])
            style.renderer = _text_renderer_value(self.dvz)
            _assign_rgba8(style.color, colors[index])
            style_result = self.dvz.dvz_text_set_style(text, style)
            if style_result not in (0, None, True):
                raise DatovizV04Unsupported("Datoviz text style configuration failed")

            placement = _text_placement(self.dvz)
            placement.mode = mode
            placement.anchor = _text_anchor_value(self.dvz, visual.coordinate_space)
            placement.position[0] = float(positions[index, 0])
            placement.position[1] = float(positions[index, 1])
            placement.position[2] = float(visual.z_order)
            placement.text_anchor[0] = _text_anchor_x_value(anchor_x[index])
            placement.text_anchor[1] = _text_anchor_y_value(anchor_y[index])
            placement.has_text_anchor = True
            placement.angle = float(rotations[index])
            placement.depth_test = False
            _set_text_placement(self.dvz, text, placement)
            self.dvz.dvz_text_set_string(text, text_value.encode("utf-8"))
            texts.append(text)

        self.visuals[visual.id] = tuple(texts)
        return tuple(texts)

    def add_colorbar_guide(self, guide: ColorbarGuide) -> Any:
        """Create a native Datoviz colorbar bound to the guide's color scale."""
        scale = resolve_color_scale(self.color_scales, guide.color_scale_id)
        diagnostics = _datoviz_colorbar_diagnostics(self.dvz)
        if diagnostics:
            raise DatovizV04Unsupported(
                "colorbar_render_unsupported: Datoviz v0.4 ColorbarGuide "
                "facade is unavailable: " + "; ".join(diagnostics)
            )

        native_scale = self._create_native_colorbar_scale(scale, guide)
        desc = self.dvz.dvz_colorbar_desc()
        _configure_colorbar_layout(self.dvz, desc, guide, self.width, self.height)
        if hasattr(desc, "anchor"):
            desc.anchor = _colorbar_anchor_value(self.dvz, guide.placement)
        if hasattr(desc, "title"):
            desc.title = guide.label.encode("utf-8") if guide.label else None

        colorbar = self.dvz.dvz_colorbar(
            self.panel, native_scale, _ctypes_pointer_arg(desc)
        )
        if colorbar is None:
            raise DatovizV04Unsupported("Datoviz colorbar allocation failed")
        self.dvz.dvz_colorbar_set_orientation(
            colorbar, _colorbar_orientation_value(self.dvz, guide.orientation)
        )
        anchor_result = self.dvz.dvz_colorbar_set_anchor(
            colorbar, _colorbar_anchor_value(self.dvz, guide.placement)
        )
        if anchor_result not in (0, None, True):
            raise DatovizV04Unsupported("Datoviz colorbar anchor configuration failed")
        _configure_colorbar_format(self.dvz, colorbar)
        _configure_colorbar_ticks(self.dvz, colorbar, guide)
        if guide.label:
            self.dvz.dvz_colorbar_set_title(colorbar, guide.label.encode("utf-8"))
        self.colorbars[guide.id] = colorbar
        return colorbar

    def _create_native_colorbar_scale(
        self, scale: ColorScale, guide: ColorbarGuide
    ) -> Any:
        if scale.id in self.native_scales:
            return self.native_scales[scale.id]

        desc = self.dvz.dvz_scale_desc()
        if hasattr(desc, "kind"):
            desc.kind = _enum_value(
                self.dvz, "DvzScaleKind", "DVZ_SCALE_CONTINUOUS", DVZ_SCALE_CONTINUOUS
            )
        if hasattr(desc, "label"):
            desc.label = guide.label.encode("utf-8") if guide.label else None
        native_scale = self.dvz.dvz_scale(self.scene, _ctypes_pointer_arg(desc))
        if native_scale is None:
            raise DatovizV04Unsupported("Datoviz scale allocation failed")
        self.dvz.dvz_scale_set_domain(
            native_scale, scale.normalize.vmin, scale.normalize.vmax
        )
        self.dvz.dvz_scale_set_view_range(
            native_scale, scale.normalize.vmin, scale.normalize.vmax
        )
        colormap = self.dvz.dvz_colormap_builtin(
            self.scene, _builtin_colormap_value(self.dvz, scale.colormap.id)
        )
        if colormap is None:
            raise DatovizV04Unsupported("Datoviz colormap allocation failed")
        self.dvz.dvz_scale_set_colormap(native_scale, colormap)
        self.native_colormaps[scale.id] = colormap
        self.native_scales[scale.id] = native_scale
        return native_scale

    def show(self, *, frame_count: int = 0) -> None:
        """Open an interactive Datoviz window and run the app.

        A ``frame_count`` of 0 follows Datoviz convention and runs until the user
        closes the window. Tests may set ``GSP_TEST=True`` to avoid blocking.
        """
        if os.environ.get("GSP_TEST") == "True":
            return
        if frame_count < 0:
            raise ValueError("frame_count must be non-negative")
        self._ensure_live_view()
        app_run = getattr(self.dvz, "dvz_app_run", None)
        if app_run is None:
            raise DatovizV04Unavailable(
                "Datoviz interactive app run is unavailable: missing dvz_app_run"
            )
        app_run(self.app, frame_count)

    def _create_rgba8_sampled_field(
        self, pixels: npt.NDArray[np.uint8], width: int, height: int
    ) -> Any:
        """Create and upload a scene-owned RGBA8 sampled field."""
        desc = self.dvz.dvz_sampled_field_desc()
        desc.dim = DVZ_FIELD_DIM_2D
        desc.format = DVZ_FIELD_FORMAT_RGBA8_UNORM
        desc.semantic = DVZ_FIELD_SEMANTIC_COLOR
        desc.color_role = DVZ_COLOR_ROLE_SRGB_COLOR
        desc.width = width
        desc.height = height
        desc.depth = 1

        sampled_field = self.dvz.dvz_sampled_field(self.scene, desc)
        if sampled_field is None:
            raise DatovizV04Unsupported("Datoviz sampled-field image allocation failed")

        view = self.dvz.dvz_field_data_view()
        _set_data_view_payload(view, pixels)
        view.bytes_per_row = width * 4
        view.rows_per_image = height
        if not self.dvz.dvz_sampled_field_set_data(sampled_field, view):
            raise DatovizV04Unsupported("Datoviz sampled-field image upload failed")
        return sampled_field

    def capture_png_bytes(self) -> bytes:
        """Render one offscreen frame and return PNG screenshot/export bytes."""
        if not datoviz_v04_capture_ready(self.dvz):
            diagnostics = ", ".join(datoviz_v04_capture_diagnostics(self.dvz))
            raise DatovizV04Unavailable(
                f"Datoviz offscreen PNG capture is unavailable: {diagnostics}"
            )

        view = self._ensure_offscreen_view()
        self._render_offscreen_frame()

        path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as file:
                path = Path(file.name)
            result = self.dvz.dvz_view_capture_png(view, str(path).encode())
            if result != 0:
                raise DatovizV04Unsupported("Datoviz offscreen PNG capture failed")
            return path.read_bytes()
        finally:
            if path is not None:
                path.unlink(missing_ok=True)

    def _ensure_offscreen_view(self) -> Any:
        """Create the lazy offscreen app/view pair used by PNG capture."""
        if self.offscreen_view is not None:
            return self.offscreen_view

        self._ensure_app("offscreen")
        self.offscreen_view = self.dvz.dvz_view_offscreen(
            self.app, self.figure, self.width, self.height
        )
        if _is_null_handle(self.offscreen_view):
            raise DatovizV04Unavailable("Datoviz offscreen view creation failed")
        return self.offscreen_view

    def _ensure_live_view(self) -> Any:
        """Create the lazy interactive app/view pair used by show()."""
        if self.live_view is not None:
            return self.live_view

        self._ensure_app("interactive")
        view = getattr(self.dvz, "dvz_view", None)
        if view is None:
            raise DatovizV04Unavailable(
                "Datoviz interactive view is unavailable: missing dvz_view"
            )
        self.live_view = view(self.app, self.figure, None)
        if _is_null_handle(self.live_view):
            raise DatovizV04Unavailable("Datoviz interactive view creation failed")
        return self.live_view

    def _ensure_app(self, purpose: str) -> Any:
        """Create the lazy Datoviz app shared by live and offscreen views."""
        if self.app is not None:
            return self.app
        app = getattr(self.dvz, "dvz_app", None)
        if app is None:
            raise DatovizV04Unavailable(
                f"Datoviz {purpose} app creation is unavailable: missing dvz_app"
            )
        self.app = app(self.scene)
        if _is_null_handle(self.app):
            raise DatovizV04Unavailable(f"Datoviz {purpose} app creation failed")
        return self.app

    def _render_offscreen_frame(self) -> None:
        view_render_once = getattr(self.dvz, "dvz_view_render_once", None)
        if view_render_once is not None:
            result = view_render_once(self.offscreen_view)
        else:
            app_render_once = getattr(self.dvz, "dvz_app_render_once", None)
            if app_render_once is not None:
                result = app_render_once(self.app)
            else:
                result = self.dvz.dvz_app_run(self.app, 1)
        frame_ready = getattr(self.dvz, "DVZ_CANVAS_FRAME_READY", 0)
        if result not in (0, None, frame_ready):
            raise DatovizV04Unsupported("Datoviz offscreen frame render failed")

    def query_panel(self, request: QueryRequest) -> QueryResult:
        """Queue and poll one Datoviz panel query for data-scope panel coordinates."""
        request_diagnostic = _datoviz_query_request_diagnostic(request)
        if request_diagnostic is not None:
            unsupported = _unsupported_query_result(request, request_diagnostic)
            if unsupported is not None:
                return unsupported
        if not datoviz_v04_query_binding_ready(self.dvz):
            diagnostics = ", ".join(datoviz_v04_query_binding_diagnostics(self.dvz))
            unsupported = _unsupported_query_result(
                request, f"Datoviz query binding is unavailable: {diagnostics}"
            )
            if unsupported is not None:
                return unsupported

        dvz_request = self.dvz.dvz_query_request()
        dvz_request.request_id = _datoviz_request_id(request.id)
        dvz_request.target = getattr(
            self.dvz, "DVZ_SCENE_TARGET_ITEM", DVZ_SCENE_TARGET_ITEM
        )
        dvz_request.hit_policy = getattr(
            self.dvz, "DVZ_QUERY_HIT_FRONTMOST", DVZ_QUERY_HIT_FRONTMOST
        )
        dvz_request.profile = getattr(
            self.dvz, "DVZ_QUERY_PROFILE_UNSUPPORTED", DVZ_QUERY_PROFILE_UNSUPPORTED
        )

        x, y = request.coordinate
        if _panel_query(self.dvz, self.panel, float(x), float(y), dvz_request) != 0:
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.FAILED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic="Datoviz panel query enqueue failed",
            )

        if _query_frame_resolution_ready(self.dvz):
            self._ensure_offscreen_view()
            self._render_offscreen_frame()

        raw_result = self.dvz.DvzQueryResult()
        if not _scene_poll_query(self.dvz, self.scene, raw_result):
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.DROPPED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic="Datoviz query produced no resolved result during bounded poll",
            )

        decoded = replace(decode_dvz_query_result(raw_result), request_id=request.id)
        return self._decorate_scalar_query_result(decoded, request)

    def _decorate_scalar_query_result(
        self, result: QueryResult, request: QueryRequest
    ) -> QueryResult:
        """Attach exact S026 scalar payloads from retained protocol scene data."""
        if result.status != QueryStatus.HIT:
            return result

        wants_scalar_payload = (
            SCALAR_COLOR_QUERY_PAYLOAD_KIND
            in request.requested_extension_payload_kinds
        )
        metadata = self._scalar_metadata_for_query_result(result)
        if metadata is None:
            if wants_scalar_payload:
                return QueryResult(
                    request_id=request.id,
                    status=QueryStatus.UNSUPPORTED,
                    hit=False,
                    panel_coordinate=request.coordinate,
                    diagnostic=(
                        "scalar_query_source_unavailable: Datoviz query hit could not "
                        "be matched to a retained scalar-colored point or image visual"
                    ),
                )
            return result

        payload = _scalar_payload_for_query_result(metadata, result)
        if payload is None:
            if wants_scalar_payload:
                return QueryResult(
                    request_id=request.id,
                    status=QueryStatus.UNSUPPORTED,
                    hit=False,
                    panel_coordinate=request.coordinate,
                    diagnostic=(
                        "scalar_query_source_unavailable: Datoviz query hit did not "
                        "include a usable point item id or image texel id"
                    ),
                )
            return result

        return replace(
            result,
            displayed_rgba=payload.displayed_rgba,
            value=payload.source_value,
            extension_payload_kind=SCALAR_COLOR_QUERY_PAYLOAD_KIND,
            extension_payload=payload,
        )

    def _scalar_metadata_for_query_result(
        self, result: QueryResult
    ) -> _ScalarVisualData | None:
        if not self.scalar_visuals:
            return None
        if result.visual_id in self.scalar_visuals:
            return self.scalar_visuals[result.visual_id]

        candidates = [
            metadata
            for metadata in self.scalar_visuals.values()
            if metadata.visual_family == result.visual_family
        ]
        if len(candidates) == 1:
            return candidates[0]
        return None

    def configure_view2d_axes(
        self,
        view: View2D,
        *,
        x_label: str | None = None,
        y_label: str | None = None,
        grid: bool = False,
        backend_auto_ticks: bool = True,
        x_tick_values: tuple[float, ...] = (),
        x_tick_labels: tuple[str, ...] | None = None,
        y_tick_values: tuple[float, ...] = (),
        y_tick_labels: tuple[str, ...] | None = None,
    ) -> None:
        """Configure Datoviz v0.4-dev native panel domains and panel-owned axes.

        This is a capability-gated proof. It uses only the local v0.4-dev C ABI names
        verified in ``include/datoviz/scene.h`` and exposed by the supplied Python facade.
        """
        provider = datoviz_v04_axis_provider_capability(self.dvz)
        if provider.provider_status == "unsupported":
            diagnostic = (
                provider.diagnostics[0]
                if provider.diagnostics
                else "Datoviz native axis provider is unavailable"
            )
            raise DatovizV04Unavailable(diagnostic)
        has_explicit_ticks = bool(x_tick_values or y_tick_values)
        if not backend_auto_ticks and not has_explicit_ticks:
            raise DatovizV04Unsupported(
                "Datoviz native axis provider cannot realize explicit GSP ticks in this slice"
            )
        dim_x = getattr(self.dvz, "DVZ_DIM_X", 0)
        dim_y = getattr(self.dvz, "DVZ_DIM_Y", 1)
        self.apply_datoviz_data_view2d(view)

        x_axis = self.dvz.dvz_panel_axis(self.panel, dim_x)
        y_axis = self.dvz.dvz_panel_axis(self.panel, dim_y)

        tick_policy = self.dvz.dvz_axis_tick_policy()
        self.dvz.dvz_axis_set_tick_policy(x_axis, tick_policy)
        self.dvz.dvz_axis_set_tick_policy(y_axis, tick_policy)
        if x_tick_values and hasattr(self.dvz, "dvz_axis_set_ticks"):
            _set_axis_ticks(self.dvz, x_axis, x_tick_values, x_tick_labels)
        if y_tick_values and hasattr(self.dvz, "dvz_axis_set_ticks"):
            _set_axis_ticks(self.dvz, y_axis, y_tick_values, y_tick_labels)

        if hasattr(self.dvz, "dvz_axis_set_grid"):
            self.dvz.dvz_axis_set_grid(x_axis, grid)
            self.dvz.dvz_axis_set_grid(y_axis, grid)

        if x_label is not None:
            self.dvz.dvz_axis_set_label(x_axis, x_label.encode("utf-8"))
        if y_label is not None:
            self.dvz.dvz_axis_set_label(y_axis, y_label.encode("utf-8"))

    def apply_datoviz_data_view2d(self, view: View2D) -> Any:
        """Apply GSP ordered data ranges and Datoviz View2D policy."""
        has_panel_domain = hasattr(self.dvz, "dvz_panel_set_domain")
        if has_panel_domain:
            _set_datoviz_panel_domains(self.dvz, self.panel, view.x_range, view.y_range)
        panel_view = self.dvz.dvz_panel_view2d()
        if not has_panel_domain:
            _set_datoviz_data_domain(panel_view, "data_x", view.x_range)
            _set_datoviz_data_domain(panel_view, "data_y", view.y_range)
        if hasattr(panel_view, "padding"):
            panel_view.padding = 0.0
        result = self.dvz.dvz_panel_set_view2d(self.panel, panel_view)
        if result not in (0, None, True):
            raise DatovizV04Unsupported("Datoviz View2D data-domain setup failed")
        return panel_view


def _set_datoviz_data_domain(
    panel_view: Any, field_name: str, limits: tuple[float, float]
) -> None:
    domain = getattr(panel_view, field_name, None)
    if domain is None:
        raise DatovizV04Unsupported(
            f"Datoviz View2D descriptor is missing {field_name}"
        )
    if not hasattr(domain, "min") or not hasattr(domain, "max"):
        raise DatovizV04Unsupported(
            f"Datoviz View2D descriptor {field_name} is not writable"
        )
    domain.min = float(limits[0])
    domain.max = float(limits[1])


def _set_datoviz_panel_domains(
    dvz: Any,
    panel: Any,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
) -> None:
    """Set ordered panel DATA domains through the current Datoviz v0.4 contract."""
    setter = getattr(dvz, "dvz_panel_set_domain", None)
    if setter is None:
        raise DatovizV04Unsupported(
            "Datoviz View2D data-domain setup failed: missing dvz_panel_set_domain"
        )
    dim_x = getattr(dvz, "DVZ_DIM_X", 0)
    dim_y = getattr(dvz, "DVZ_DIM_Y", 1)
    for dim, limits in ((dim_x, x_range), (dim_y, y_range)):
        result = setter(panel, dim, float(limits[0]), float(limits[1]))
        if result not in (0, None, True):
            raise DatovizV04Unsupported("Datoviz panel data-domain setup failed")


def _set_axis_ticks(
    dvz: Any,
    axis: Any,
    values: tuple[float, ...],
    labels: tuple[str, ...] | None,
) -> None:
    tick_values = np.ascontiguousarray(np.asarray(values, dtype=np.float64))
    if labels is None:
        result = dvz.dvz_axis_set_ticks(axis, tick_values, None)
    else:
        encoded_labels = tuple(label.encode("utf-8") for label in labels)
        result = dvz.dvz_axis_set_ticks(axis, tick_values, encoded_labels)
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz explicit axis tick configuration failed")


def _positions_3d(
    positions: npt.NDArray[np.float32] | npt.NDArray[np.float64],
) -> npt.NDArray[np.float32]:
    array = np.asarray(positions, dtype=np.float32)
    if array.shape[1] == 3:
        return np.ascontiguousarray(array)
    zeros = np.zeros((array.shape[0], 1), dtype=np.float32)
    return np.ascontiguousarray(np.column_stack([array, zeros]))


def _is_null_handle(handle: Any) -> bool:
    """Return whether a Datoviz/ctypes handle is absent or a NULL pointer."""
    if handle is None:
        return True
    try:
        return not bool(handle)
    except TypeError:
        return False


def _adapt_visual_positions(
    visual_id: str,
    positions: npt.NDArray[np.float32] | npt.NDArray[np.float64],
    transform: VisualTransformBinding | None,
    coordinate_space: CoordinateSpace,
    view: View2D | None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None,
) -> npt.NDArray[np.float32] | npt.NDArray[np.float64]:
    transformed = _cpu_adapt_affine_positions(
        visual_id, positions, transform, transform_resources
    )
    if coordinate_space is CoordinateSpace.NDC:
        return transformed
    if coordinate_space is CoordinateSpace.DATA:
        return transformed
    raise DatovizV04Unsupported(
        f"Datoviz visual coordinate space is unsupported: {coordinate_space.value}"
    )


def _cpu_adapt_affine_positions(
    visual_id: str,
    positions: npt.NDArray[np.float32] | npt.NDArray[np.float64],
    transform: VisualTransformBinding | None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None,
) -> npt.NDArray[np.float32] | npt.NDArray[np.float64]:
    """Apply bounded S027 CPU transform adaptation for finite eager positions."""
    if transform is None:
        return positions
    xy = np.asarray(positions[:, :2], dtype=np.float64)
    homogeneous = np.column_stack([xy, np.ones((xy.shape[0],), dtype=np.float64)])
    matrix = _transform_binding_matrix(transform, transform_resources)
    transformed = np.asarray((homogeneous @ matrix.T)[:, :2], dtype=np.float64)
    if positions.shape[1] == 3:
        z = np.asarray(positions[:, 2:3], dtype=np.float64)
        transformed = np.column_stack([transformed, z])
    if not np.all(np.isfinite(transformed)):
        raise DatovizV04Unsupported(
            f"GSP_TRANSFORM_NONFINITE: CPU transform adaptation produced "
            f"non-finite positions for {visual_id}"
        )
    return np.ascontiguousarray(transformed.astype(positions.dtype, copy=False))


def _transform_binding_matrix(
    transform: VisualTransformBinding,
    transform_resources: Mapping[str, AffineTransform2DResource] | None,
) -> npt.NDArray[np.float64]:
    if transform.inline is not None:
        return np.asarray(transform.inline.matrix, dtype=np.float64)
    if transform.ref is None:
        raise DatovizV04Unsupported(
            "GSP_TRANSFORM_UNSUPPORTED_KIND: Datoviz transform binding is invalid"
        )
    if transform_resources is None or transform.ref.id not in transform_resources:
        if not transform.ref.required:
            return np.eye(3, dtype=np.float64)
        raise DatovizV04Unsupported(
            "GSP_TRANSFORM_MISSING_REF: Datoviz v0.4 transform CPU adapter "
            f"could not resolve named transform resource {transform.ref.id!r}"
        )
    return np.asarray(transform_resources[transform.ref.id].matrix, dtype=np.float64)


def _record_transform_adaptation(
    adaptations: dict[str, tuple[str, ...]],
    visual_id: str,
    transform: VisualTransformBinding | None,
) -> None:
    if transform is None:
        return
    adaptations[visual_id] = (
        "cpu_adapter_affine2d_eager_ndc",
        "query_inverse_unsupported",
    )


def _rgba8(colors: npt.NDArray[Any]) -> npt.NDArray[np.uint8]:
    if colors.dtype == np.dtype(np.uint8):
        return np.ascontiguousarray(colors)
    return np.ascontiguousarray(
        np.rint(np.asarray(colors) * 255.0).clip(0, 255).astype(np.uint8)
    )


def _datoviz_mesh_payload(
    visual: MeshVisual,
    positions: npt.NDArray[np.float32] | npt.NDArray[np.float64],
) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.uint8], npt.NDArray[np.uint32]]:
    if visual.face_color_encoding is not None:
        raise DatovizV04Unsupported(
            "Datoviz MeshVisual face scalar color encoding is unavailable"
        )
    if visual.color is None:
        raise DatovizV04Unsupported("Datoviz MeshVisual requires resolved RGBA colors")
    color_mode = visual.resolved_color_mode()
    positions = np.asarray(positions, dtype=np.float32)
    faces = np.asarray(visual.faces, dtype=np.uint32)
    colors = _rgba8(np.asarray(visual.color))

    if color_mode is MeshColorMode.UNIFORM:
        rgba = np.asarray(colors, dtype=np.uint8).reshape(1, 4)
        vertex_colors = np.repeat(rgba, positions.shape[0], axis=0)
        return (
            _positions_3d(positions),
            np.ascontiguousarray(vertex_colors),
            np.ascontiguousarray(faces.reshape(-1)),
        )
    if color_mode is MeshColorMode.VERTEX:
        return (
            _positions_3d(positions),
            np.ascontiguousarray(colors.reshape(positions.shape[0], 4)),
            np.ascontiguousarray(faces.reshape(-1)),
        )
    if color_mode is MeshColorMode.FACE:
        triangle_positions = positions[faces].reshape(-1, positions.shape[1])
        triangle_colors = np.repeat(colors.reshape(faces.shape[0], 4), 3, axis=0)
        triangle_indices = np.arange(triangle_positions.shape[0], dtype=np.uint32)
        return (
            _positions_3d(np.ascontiguousarray(triangle_positions)),
            np.ascontiguousarray(triangle_colors),
            np.ascontiguousarray(triangle_indices),
        )
    raise DatovizV04Unsupported(f"unsupported mesh color mode: {color_mode}")


def _diameters_from_pixel_diameters(
    sizes: npt.NDArray[np.float32] | npt.NDArray[np.float64] | float,
    count: int,
) -> npt.NDArray[np.float32]:
    if isinstance(sizes, np.ndarray):
        diameters = np.asarray(sizes, dtype=np.float32)
    else:
        diameters = np.full((count,), float(sizes), dtype=np.float32)
    return np.ascontiguousarray(diameters.reshape(-1))


def _visual_attach_desc(dvz: Any, *, coord_space: str, z_layer: int) -> Any:
    factory = getattr(dvz, "dvz_visual_attach_desc", None)
    if factory is not None:
        desc = factory()
    else:
        desc_type = getattr(dvz, "DvzVisualAttachDesc", None)
        if desc_type is None:
            raise DatovizV04Unavailable("Datoviz facade is missing DvzVisualAttachDesc")
        desc = desc_type()
        if hasattr(desc, "struct_size"):
            desc.struct_size = ctypes.sizeof(desc_type)
        if hasattr(desc, "flags"):
            desc.flags = 0

    desc.z_layer = z_layer
    if coord_space == "data":
        desc.coord_space = _coord_space_value(dvz, "DVZ_COORD_DATA", DVZ_COORD_DATA)
    elif coord_space == "view":
        desc.coord_space = _coord_space_value(dvz, "DVZ_COORD_VIEW", DVZ_COORD_VIEW)
    else:
        raise ValueError(f"unsupported Datoviz coordinate space: {coord_space}")
    return desc


def _datoviz_visual_coord_space(coordinate_space: CoordinateSpace) -> str:
    if coordinate_space is CoordinateSpace.NDC:
        return "view"
    if coordinate_space is CoordinateSpace.DATA:
        return "data"
    raise DatovizV04Unsupported(
        f"Datoviz visual coordinate space is unsupported: {coordinate_space.value}"
    )


def _coord_space_value(dvz: Any, name: str, fallback: int) -> int:
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzVisualCoordSpace", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _text_placement_mode_value(dvz: Any, coordinate_space: CoordinateSpace) -> int:
    if coordinate_space == CoordinateSpace.NDC:
        name = "DVZ_TEXT_PLACEMENT_DATA"
        fallback = DVZ_TEXT_PLACEMENT_DATA
    elif coordinate_space == CoordinateSpace.DATA:
        name = "DVZ_TEXT_PLACEMENT_DATA"
        fallback = DVZ_TEXT_PLACEMENT_DATA
    else:
        raise DatovizV04Unsupported(
            f"Datoviz TextVisual coordinate space is unsupported: {coordinate_space.value}"
        )
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzTextPlacementMode", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _text_anchor_value(dvz: Any, coordinate_space: CoordinateSpace) -> int:
    if coordinate_space in (CoordinateSpace.NDC, CoordinateSpace.DATA):
        name = "DVZ_SCENE_ANCHOR_DATA"
        fallback = DVZ_SCENE_ANCHOR_DATA
    else:
        raise DatovizV04Unsupported(
            f"Datoviz TextVisual coordinate space is unsupported: {coordinate_space.value}"
        )
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzSceneAnchor", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _text_renderer_value(dvz: Any) -> int:
    name = "DVZ_TEXT_RENDERER_MSDF_ATLAS"
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzTextRenderer", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return DVZ_TEXT_RENDERER_MSDF_ATLAS


def _text_placement(dvz: Any) -> Any:
    factory = getattr(dvz, "dvz_text_placement", None)
    if factory is not None:
        return factory()
    placement = _CompatDvzTextPlacement()
    placement.struct_size = ctypes.sizeof(_CompatDvzTextPlacement)
    placement.flags = 0
    placement.mode = DVZ_TEXT_PLACEMENT_SCREEN
    placement.anchor = DVZ_SCENE_ANCHOR_PANEL_TOP
    return placement


def _set_text_placement(dvz: Any, text: Any, placement: Any) -> None:
    if isinstance(placement, _CompatDvzTextPlacement):
        raw_setter = _datoviz_shared_library_function(dvz, "dvz_text_set_placement")
        if raw_setter is None:
            raise DatovizV04Unsupported(
                "Datoviz text placement fallback requires dvz_text_set_placement in libdatoviz"
            )
        raw_setter.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_CompatDvzTextPlacement),
        ]
        raw_setter.restype = None
        raw_setter(ctypes.cast(text, ctypes.c_void_p), ctypes.byref(placement))
        return
    result = dvz.dvz_text_set_placement(text, placement)
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz text placement configuration failed")


def _text_anchor_x_value(anchor: TextAnchorX) -> float:
    if anchor == TextAnchorX.LEFT:
        return 0.0
    if anchor == TextAnchorX.CENTER:
        return 0.5
    if anchor == TextAnchorX.RIGHT:
        return 1.0
    raise ValueError(f"unsupported text horizontal anchor: {anchor.value}")


def _text_anchor_y_value(anchor: TextAnchorY) -> float:
    if anchor == TextAnchorY.TOP:
        return 0.0
    if anchor in (TextAnchorY.CENTER, TextAnchorY.BASELINE):
        return 0.5
    if anchor == TextAnchorY.BOTTOM:
        return 1.0
    raise ValueError(f"unsupported text vertical anchor: {anchor.value}")


def _assign_rgba8(target: Any, color: npt.NDArray[np.uint8]) -> None:
    for index, channel in enumerate(color):
        target[index] = int(channel)


def _datoviz_shared_library_function(dvz: Any, name: str) -> Any | None:
    module_file = getattr(dvz, "__file__", None)
    if not isinstance(module_file, str):
        return None
    module_dir = Path(module_file).resolve().parent
    for filename in ("libdatoviz.so", "libdatoviz.dylib", "datoviz.dll"):
        library_path = module_dir / filename
        if not library_path.exists():
            continue
        try:
            library = ctypes.CDLL(str(library_path))
            return getattr(library, name)
        except (OSError, AttributeError):
            continue
    return None


def _rgba8_image_visual(
    visual: ImageVisual, *, color_scales: Mapping[str, ColorScale] | None
) -> npt.NDArray[np.uint8]:
    image = visual.image
    if image.ndim == 2:
        if visual.color_scale_id is not None:
            scale = resolve_color_scale(color_scales, visual.color_scale_id)
            return _rgba8_scalar_values(image, scale, alpha=1.0)
        return _rgba8_scalar_image(image, visual.clim)
    return _rgba8_image(image)


def _rgba8_image(image: npt.NDArray[Any]) -> npt.NDArray[np.uint8]:
    if image.dtype != np.dtype(np.uint8):
        image = np.rint(np.asarray(image) * 255.0).clip(0, 255).astype(np.uint8)
    if image.ndim != 3 or image.shape[2] not in (3, 4):
        raise DatovizV04Unsupported(
            "Datoviz v0.4 slice only supports uint8 RGB/RGBA images"
        )
    if image.shape[2] == 4:
        return np.ascontiguousarray(image)
    alpha = np.full((*image.shape[:2], 1), 255, dtype=np.uint8)
    return np.ascontiguousarray(np.concatenate([image, alpha], axis=2))


def _rgba8_scalar_image(
    image: npt.NDArray[Any], clim: tuple[float, float] | None
) -> npt.NDArray[np.uint8]:
    values = np.asarray(image, dtype=np.float32)
    if clim is None:
        vmin = float(np.min(values))
        vmax = float(np.max(values))
        if vmin == vmax:
            vmax = vmin + 1.0
    else:
        vmin, vmax = clim
    normalized = ((values - vmin) / (vmax - vmin)).clip(0.0, 1.0)
    gray = np.rint(normalized * 255.0).astype(np.uint8)
    alpha = np.full(gray.shape, 255, dtype=np.uint8)
    return np.ascontiguousarray(np.stack([gray, gray, gray, alpha], axis=2))


def _point_colors(
    visual: PointVisual, *, color_scales: Mapping[str, ColorScale] | None
) -> npt.NDArray[np.uint8]:
    if visual.color_encoding is not None:
        scale = resolve_color_scale(color_scales, visual.color_encoding.color_scale_id)
        return _rgba8_scalar_values(
            visual.color_encoding.values,
            scale,
            alpha=float(visual.color_encoding.alpha),
        )
    if visual.colors is None:
        raise ValueError("PointVisual requires colors or color_encoding")
    return _rgba8(visual.colors)


def _marker_fill_colors(
    visual: MarkerVisual, *, color_scales: Mapping[str, ColorScale] | None
) -> npt.NDArray[np.uint8]:
    if visual.fill_color_encoding is not None:
        scale = resolve_color_scale(
            color_scales, visual.fill_color_encoding.color_scale_id
        )
        return _rgba8_scalar_values(
            visual.fill_color_encoding.values,
            scale,
            alpha=float(visual.fill_color_encoding.alpha),
        )
    if visual.fill_colors is None:
        raise ValueError("MarkerVisual requires fill_colors or fill_color_encoding")
    return _rgba8(visual.fill_colors)


def _rgba8_scalar_values(
    values: npt.ArrayLike, scale: ColorScale, *, alpha: float
) -> npt.NDArray[np.uint8]:
    mapped = map_scalar_values(values, scale, alpha=alpha)
    return np.ascontiguousarray(
        np.rint(mapped * 255.0).clip(0, 255).astype(np.uint8)
    )


def _scalar_payload_for_query_result(
    metadata: _ScalarVisualData, result: QueryResult
) -> ScalarColorQueryPayload | None:
    item_id: int | None = None
    texel: tuple[int, int] | None = None
    if metadata.item_kind == "point":
        if result.item_id is None:
            return None
        if result.item_id < 0 or result.item_id >= metadata.values.shape[0]:
            return None
        source_value = float(metadata.values[result.item_id])
        item_id = result.item_id
    elif metadata.item_kind == "texel":
        texel = _resolved_scalar_texel(metadata.values, result)
        if texel is None:
            return None
        source_value = float(metadata.values[texel[0], texel[1]])
    else:
        return None

    mapped = map_scalar_value(source_value, metadata.color_scale, alpha=metadata.alpha)
    return ScalarColorQueryPayload(
        visual_id=metadata.visual_id,
        item_kind=metadata.item_kind,
        item_id=item_id,
        texel=texel,
        color_slot=metadata.color_slot,
        color_scale_id=metadata.color_scale.id,
        colormap_id=metadata.color_scale.colormap.id.value,
        source_value=mapped.source_value,
        normalized_value_raw=mapped.normalized_value_raw,
        normalized_value_clipped=mapped.normalized_value_clipped,
        range_class=mapped.range_class,
        lut_index=mapped.lut_index,
        displayed_rgba=mapped.displayed_rgba,
    )


def _resolved_scalar_texel(
    values: npt.NDArray[np.float64], result: QueryResult
) -> tuple[int, int] | None:
    if values.ndim != 2:
        return None
    height, width = values.shape
    if result.texel is not None:
        row, col = result.texel
        if 0 <= row < height and 0 <= col < width:
            return (row, col)
        flat_index = col if row == 0 else row * width + col
        if 0 <= flat_index < values.size:
            resolved_row, resolved_col = np.unravel_index(flat_index, values.shape)
            return (int(resolved_row), int(resolved_col))
    if result.item_id is not None and 0 <= result.item_id < values.size:
        resolved_row, resolved_col = np.unravel_index(result.item_id, values.shape)
        return (int(resolved_row), int(resolved_col))
    return None


def _set_data_view_payload(view: Any, pixels: npt.NDArray[np.uint8]) -> None:
    try:
        view.data = pixels
    except TypeError:
        view.data = pixels.ctypes.data


def _set_visual_field(
    dvz: Any, visual: Any, slot_name: str, sampled_field: Any
) -> bool:
    try:
        return bool(dvz.dvz_visual_set_field(visual, slot_name, sampled_field))
    except (ctypes.ArgumentError, TypeError):
        return bool(
            dvz.dvz_visual_set_field(visual, slot_name.encode("utf-8"), sampled_field)
        )


def _ctypes_pointer_arg(value: Any) -> Any:
    if isinstance(value, ctypes.Structure):
        return ctypes.byref(value)
    return value


def _enum_value(dvz: Any, enum_type_name: str, name: str, fallback: int) -> int:
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, enum_type_name, None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _builtin_colormap_value(dvz: Any, colormap_id: ColorMapId) -> int:
    name, fallback = _BUILTIN_COLORMAP_NAMES[colormap_id]
    return _enum_value(dvz, "DvzBuiltinColormap", name, fallback)


def _colorbar_orientation_value(
    dvz: Any, orientation: ColorbarOrientation
) -> int:
    if orientation is ColorbarOrientation.VERTICAL:
        return _enum_value(
            dvz,
            "DvzColorbarOrientation",
            "DVZ_COLORBAR_ORIENTATION_VERTICAL",
            DVZ_COLORBAR_ORIENTATION_VERTICAL,
        )
    if orientation is ColorbarOrientation.HORIZONTAL:
        return _enum_value(
            dvz,
            "DvzColorbarOrientation",
            "DVZ_COLORBAR_ORIENTATION_HORIZONTAL",
            DVZ_COLORBAR_ORIENTATION_HORIZONTAL,
        )
    raise DatovizV04Unsupported(
        f"unsupported Datoviz colorbar orientation: {orientation.value}"
    )


def _colorbar_anchor_value(
    dvz: Any, placement: ColorbarPlacement | None
) -> int:
    if placement is ColorbarPlacement.RIGHT or placement is None:
        return _enum_value(
            dvz,
            "DvzSceneAnchor",
            "DVZ_SCENE_ANCHOR_PANEL_RIGHT",
            DVZ_SCENE_ANCHOR_PANEL_RIGHT,
        )
    if placement is ColorbarPlacement.LEFT:
        return _enum_value(
            dvz,
            "DvzSceneAnchor",
            "DVZ_SCENE_ANCHOR_PANEL_LEFT",
            DVZ_SCENE_ANCHOR_PANEL_LEFT,
        )
    if placement is ColorbarPlacement.BOTTOM:
        return _enum_value(
            dvz,
            "DvzSceneAnchor",
            "DVZ_SCENE_ANCHOR_PANEL_BOTTOM",
            DVZ_SCENE_ANCHOR_PANEL_BOTTOM,
        )
    if placement is ColorbarPlacement.TOP:
        return _enum_value(
            dvz,
            "DvzSceneAnchor",
            "DVZ_SCENE_ANCHOR_PANEL_TOP",
            DVZ_SCENE_ANCHOR_PANEL_TOP,
        )
    raise DatovizV04Unsupported(
        f"unsupported Datoviz colorbar placement: {placement.value}"
    )


def _configure_colorbar_layout(
    dvz: Any, desc: Any, guide: ColorbarGuide, width: int, height: int
) -> None:
    """Use a bounded colorbar placement for visual QA captures."""
    if hasattr(desc, "orientation"):
        desc.orientation = _colorbar_orientation_value(dvz, guide.orientation)
    if hasattr(desc, "placement_mode"):
        desc.placement_mode = _enum_value(
            dvz,
            "DvzColorbarPlacementMode",
            "DVZ_COLORBAR_PLACEMENT_DETACHED",
            DVZ_COLORBAR_PLACEMENT_DETACHED,
        )
    if hasattr(desc, "ramp_width_px"):
        desc.ramp_width_px = 18.0
    if hasattr(desc, "tick_length_px"):
        desc.tick_length_px = 6.0
    if hasattr(desc, "label_gap_px"):
        desc.label_gap_px = 6.0
    placement = getattr(desc, "placement", None)
    if placement is None:
        return
    if hasattr(placement, "space"):
        placement.space = _enum_value(
            dvz, "DvzPlacementSpace", "DVZ_PLACEMENT_SPACE_PANEL", DVZ_PLACEMENT_SPACE_PANEL
        )
    if hasattr(placement, "horizontal_anchor"):
        placement.horizontal_anchor = _enum_value(
            dvz,
            "DvzHorizontalAnchor",
            "DVZ_HORIZONTAL_ANCHOR_RIGHT",
            DVZ_HORIZONTAL_ANCHOR_RIGHT,
        )
    if hasattr(placement, "vertical_anchor"):
        placement.vertical_anchor = _enum_value(
            dvz,
            "DvzVerticalAnchor",
            "DVZ_VERTICAL_ANCHOR_CENTER",
            DVZ_VERTICAL_ANCHOR_CENTER,
        )
    if hasattr(placement, "offset_x_px"):
        placement.offset_x_px = -max(76.0, float(width) * 0.115)
    if hasattr(placement, "offset_y_px"):
        placement.offset_y_px = 0.0
    if hasattr(placement, "width_px"):
        placement.width_px = 18.0
    if hasattr(placement, "height_px"):
        placement.height_px = max(160.0, float(height) * 0.62)


def _configure_colorbar_format(dvz: Any, colorbar: Any) -> None:
    if not hasattr(dvz, "dvz_format_desc") or not hasattr(dvz, "dvz_colorbar_set_format"):
        return
    fmt = dvz.dvz_format_desc()
    if hasattr(fmt, "precision"):
        fmt.precision = 2
    if hasattr(fmt, "trim_trailing_zeros"):
        fmt.trim_trailing_zeros = True
    dvz.dvz_colorbar_set_format(colorbar, _ctypes_pointer_arg(fmt))


def _configure_colorbar_ticks(dvz: Any, colorbar: Any, guide: ColorbarGuide) -> None:
    if not guide.ticks:
        return
    setter = getattr(dvz, "dvz_colorbar_set_ticks", None)
    if setter is None:
        raise DatovizV04Unsupported(
            "Datoviz colorbar explicit ticks are unavailable: missing dvz_colorbar_set_ticks"
        )

    values = np.asarray(guide.ticks, dtype=np.float64)
    labels = list(guide.tick_labels) if guide.tick_labels else None
    result = setter(colorbar, values, labels)
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz colorbar explicit tick configuration failed")


def _image_sampling_value(dvz: Any, interpolation: ImageInterpolation) -> int:
    if interpolation == ImageInterpolation.NEAREST:
        name = "DVZ_IMAGE_SAMPLING_NEAREST"
        fallback = DVZ_IMAGE_SAMPLING_NEAREST
    elif interpolation == ImageInterpolation.LINEAR:
        name = "DVZ_IMAGE_SAMPLING_LINEAR"
        fallback = DVZ_IMAGE_SAMPLING_LINEAR
    else:
        raise DatovizV04Unsupported(
            f"unsupported Datoviz image interpolation: {interpolation}"
        )

    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzImageSampling", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _set_image_sampling(
    dvz: Any, visual: Any, interpolation: ImageInterpolation
) -> None:
    setter = getattr(dvz, "dvz_image_set_sampling", None)
    if setter is None:
        return
    result = setter(visual, _image_sampling_value(dvz, interpolation))
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz image sampling configuration failed")


def _set_query_capabilities(dvz: Any, visual: Any, capabilities: int) -> None:
    setter = getattr(dvz, "dvz_visual_set_query_capabilities", None)
    if setter is None:
        return
    setter(visual, capabilities)


def _set_panel_background_color(
    dvz: Any, panel: Any, rgba: tuple[int, int, int, int]
) -> None:
    setter = getattr(dvz, "dvz_panel_set_background_color", None)
    if setter is None:
        return
    color = _dvz_color(dvz, rgba)
    setter(panel, color)


def _dvz_color(dvz: Any, rgba: tuple[int, int, int, int]) -> Any:
    color_type = getattr(dvz, "DvzColor", None)
    if color_type is None:
        return rgba
    try:
        return color_type(*rgba)
    except TypeError:
        color = color_type()
        for channel, value in zip(("r", "g", "b", "a"), rgba, strict=True):
            setattr(color, channel, int(value))
        return color


def _set_visual_data(
    dvz: Any, visual: Any, attr_name: str, data: npt.NDArray[Any]
) -> None:
    result = dvz.dvz_visual_set_data(visual, attr_name, data)
    if result == 0:
        return
    for alias in _VISUAL_ATTRIBUTE_ALIASES.get(attr_name, ()):
        result = dvz.dvz_visual_set_data(visual, alias, data)
        if result == 0:
            return
    raise DatovizV04Unsupported(
        f"Datoviz visual attribute {attr_name!r} upload failed"
    )


def _set_visual_index_data(
    dvz: Any, visual: Any, indices: npt.NDArray[np.uint32]
) -> None:
    result = dvz.dvz_visual_set_index_data(visual, indices, int(indices.shape[0]))
    if result != 0:
        raise DatovizV04Unsupported("Datoviz visual index upload failed")


def _set_filled_point_style(dvz: Any, visual: Any) -> None:
    """Force the documented filled/no-stroke point style when the facade exposes it."""
    style_factory = getattr(dvz, "dvz_point_style_desc", None)
    style_setter = getattr(dvz, "dvz_point_set_style", None)
    if style_factory is None or style_setter is None:
        return
    style = style_factory()
    if hasattr(style, "stroke_width"):
        style.stroke_width = 0.0
    if hasattr(style, "aspect"):
        style.aspect = int(getattr(dvz, "DVZ_SHAPE_ASPECT_FILLED", 0))
    result = style_setter(visual, style)
    if result not in (0, None, True):
        raise DatovizV04Unsupported(
            "Datoviz point filled/no-stroke style configuration failed"
        )


def _set_alpha_mode_if_translucent(
    dvz: Any, visual: Any, colors: npt.NDArray[np.uint8]
) -> None:
    if not np.any(colors[:, 3] < 255):
        return
    setter = getattr(dvz, "dvz_visual_set_alpha_mode", None)
    if setter is None:
        raise DatovizV04Unsupported(
            "Datoviz translucent colors require dvz_visual_set_alpha_mode"
        )
    result = setter(
        visual, _alpha_mode_value(dvz, "DVZ_ALPHA_BLENDED", DVZ_ALPHA_BLENDED)
    )
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz alpha blending configuration failed")


def _alpha_mode_value(dvz: Any, name: str, fallback: int) -> int:
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzAlphaMode", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _datoviz_marker_diagnostics(dvz: Any) -> tuple[str, ...]:
    return tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_MARKER_FUNCTIONS
        if not hasattr(dvz, name)
    )


def _datoviz_segment_diagnostics(dvz: Any) -> tuple[str, ...]:
    return tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_SEGMENT_FUNCTIONS
        if not hasattr(dvz, name)
    )


def _datoviz_path_diagnostics(dvz: Any) -> tuple[str, ...]:
    return tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_PATH_FUNCTIONS
        if not hasattr(dvz, name)
    )


def _datoviz_colorbar_diagnostics(dvz: Any) -> tuple[str, ...]:
    required = (
        "dvz_scale_desc",
        "dvz_scale",
        "dvz_scale_set_domain",
        "dvz_scale_set_view_range",
        "dvz_scale_set_colormap",
        "dvz_colormap_builtin",
        "dvz_colorbar_desc",
        "dvz_colorbar",
        "dvz_colorbar_set_anchor",
        "dvz_colorbar_set_orientation",
        "dvz_colorbar_set_title",
    )
    return tuple(f"missing {name}" for name in required if not hasattr(dvz, name))


def _set_path_subpaths(
    dvz: Any, visual: Any, count: int, subpaths: npt.NDArray[np.uint32]
) -> Any:
    try:
        return dvz.dvz_path_set_subpaths(visual, count, subpaths)
    except (ctypes.ArgumentError, TypeError):
        pointer = subpaths.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
        return dvz.dvz_path_set_subpaths(visual, count, pointer)


def _set_marker_style(
    dvz: Any, visual: Any, stroke_color: npt.NDArray[Any], stroke_width: float
) -> None:
    style = dvz.dvz_marker_style()
    _assign_rgba_field(style, "edge_color", _rgba8_scalar(stroke_color))
    if hasattr(style, "stroke_width_px"):
        style.stroke_width_px = float(stroke_width)
    elif hasattr(style, "stroke_width"):
        style.stroke_width = float(stroke_width)
    if hasattr(style, "aspect"):
        if stroke_width > 0.0 and _rgba8_scalar(stroke_color)[3] > 0:
            style.aspect = int(
                getattr(dvz, "DVZ_SHAPE_ASPECT_OUTLINE", DVZ_SHAPE_ASPECT_OUTLINE)
            )
        else:
            style.aspect = int(
                getattr(dvz, "DVZ_SHAPE_ASPECT_FILLED", DVZ_SHAPE_ASPECT_FILLED)
            )
    result = dvz.dvz_marker_set_style(visual, style)
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz marker style configuration failed")


def _rgba8_scalar(color: npt.NDArray[Any]) -> npt.NDArray[np.uint8]:
    rgba = _rgba8(np.asarray(color).reshape(1, 4))[0]
    return np.ascontiguousarray(rgba)


def _assign_rgba_field(
    target: Any, field_name: str, rgba: npt.NDArray[np.uint8]
) -> None:
    values = [int(value) for value in rgba]
    field = getattr(target, field_name, None)
    if field is not None:
        if all(hasattr(field, channel) for channel in ("r", "g", "b", "a")):
            field.r = values[0]
            field.g = values[1]
            field.b = values[2]
            field.a = values[3]
            return
        try:
            field[:] = values
            return
        except (TypeError, ValueError):
            pass
    color_type = getattr(type(target), field_name, None)
    if color_type is not None:
        try:
            setattr(target, field_name, color_type(*values))
            return
        except TypeError:
            pass
    setattr(target, field_name, values)


def _marker_shapes(dvz: Any, shapes: tuple[MarkerShape, ...]) -> npt.NDArray[np.uint32]:
    return np.ascontiguousarray(
        np.array([_marker_shape_value(dvz, shape) for shape in shapes], dtype=np.uint32)
    )


def _marker_shape_value(dvz: Any, shape: MarkerShape) -> int:
    name = _MARKER_SHAPE_NAMES[shape]
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzMarkerShape", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return _MARKER_SHAPE_FALLBACKS[shape]


def _stroke_cap_value(dvz: Any, cap: StrokeCap) -> int:
    name = _STROKE_CAP_NAMES[cap]
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzSegmentCap", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return _STROKE_CAP_FALLBACKS[cap]


def _stroke_join_value(dvz: Any, join: StrokeJoin) -> int:
    name = _STROKE_JOIN_NAMES[join]
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzPathJoin", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return _STROKE_JOIN_FALLBACKS[join]


def _expand_path_colors(visual: PathVisual) -> npt.NDArray[np.uint8]:
    colors = _rgba8(visual.colors)
    return np.ascontiguousarray(np.repeat(colors, visual.path_lengths, axis=0))


def _expand_path_widths(visual: PathVisual) -> npt.NDArray[np.float32]:
    widths = visual.width_values()
    return np.ascontiguousarray(np.repeat(widths, visual.path_lengths, axis=0))


def _configure_ndc_panel_view2d(dvz: Any, panel: Any) -> None:
    """Configure the panel so NDC data keeps equal X/Y screen scale when possible."""
    view_factory = getattr(dvz, "dvz_panel_view2d", None)
    view_setter = getattr(dvz, "dvz_panel_set_view2d", None)
    if view_factory is None or view_setter is None:
        return
    if hasattr(dvz, "dvz_panel_set_domain"):
        _set_datoviz_panel_domains(dvz, panel, (-1.0, 1.0), (-1.0, 1.0))
    view = view_factory()
    if hasattr(view, "aspect"):
        view.aspect = int(getattr(dvz, "DVZ_PANEL_VIEW2D_ASPECT_EQUAL", 1))
    if hasattr(view, "padding"):
        view.padding = 0.0
    if not hasattr(dvz, "dvz_panel_set_domain"):
        for field_name in ("data_x", "data_y"):
            domain = getattr(view, field_name, None)
            if domain is None:
                continue
            if hasattr(domain, "min"):
                domain.min = -1.0
            if hasattr(domain, "max"):
                domain.max = 1.0
    result = view_setter(panel, view)
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz NDC equal-aspect panel setup failed")


def _query_frame_resolution_ready(dvz: Any) -> bool:
    if not hasattr(dvz, "dvz_app") or not hasattr(dvz, "dvz_view_offscreen"):
        return False
    return (
        hasattr(dvz, "dvz_view_render_once")
        or hasattr(dvz, "dvz_app_render_once")
        or hasattr(dvz, "dvz_app_run")
    )


def _panel_query(dvz: Any, panel: Any, x: float, y: float, request: Any) -> int:
    try:
        return int(dvz.dvz_panel_query(panel, x, y, ctypes.byref(request)))
    except TypeError:
        return int(dvz.dvz_panel_query(panel, x, y, request))


def _scene_poll_query(dvz: Any, scene: Any, out_result: Any) -> bool:
    try:
        return bool(dvz.dvz_scene_poll_query(scene, ctypes.byref(out_result)))
    except TypeError:
        return bool(dvz.dvz_scene_poll_query(scene, out_result))


def _datoviz_query_request_diagnostic(request: QueryRequest) -> str | None:
    if request.scope != QueryScope.DATA:
        if request.scope == QueryScope.GUIDES:
            return (
                "axis-guide-query-unsupported: Datoviz v0.4 query slice defers "
                "guide picking/query; guide rendering capability does not imply "
                "queryable ticks, labels, grids, or titles"
            )
        if request.scope == QueryScope.ALL_RENDERED:
            return (
                "all-rendered-guides-unsupported: Datoviz v0.4 query slice cannot "
                "merge data and guide contributions because guide query is deferred"
            )
        return f"Datoviz v0.4 query slice supports data scope only, got {request.scope.value!r}"
    if request.coordinate_space != QueryCoordinateSpace.PANEL:
        return f"Datoviz v0.4 query slice supports panel coordinates only, got {request.coordinate_space.value!r}"
    if request.hit_policy != QueryHitPolicy.FRONTMOST:
        return f"Datoviz v0.4 query slice supports frontmost hit policy only, got {request.hit_policy.value!r}"
    unsupported_payloads = tuple(
        kind
        for kind in request.requested_extension_payload_kinds
        if kind != SCALAR_COLOR_QUERY_PAYLOAD_KIND
    )
    if TRANSFORM_QUERY_PAYLOAD_KIND in unsupported_payloads:
        return (
            "GSP_QUERY_INVERSE_UNSUPPORTED: Datoviz v0.4 query slice does not "
            "support gsp.transform-query@0.1 inverse payloads"
        )
    if unsupported_payloads:
        return (
            "Datoviz v0.4 query slice does not support requested extension query "
            f"payloads: {unsupported_payloads}"
        )
    return None


def _unsupported_query_result(
    request: QueryRequest, diagnostic: str | None
) -> QueryResult | None:
    if diagnostic is None:
        return None
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.UNSUPPORTED,
        hit=False,
        panel_coordinate=request.coordinate,
        diagnostic=diagnostic,
    )


def _datoviz_request_id(request_id: str) -> int:
    return crc32(request_id.encode("utf-8")) or 1


def _image_positions(
    extent: tuple[float, float, float, float],
) -> npt.NDArray[np.float32]:
    left, right, bottom, top = extent
    return np.ascontiguousarray(
        np.array(
            [
                [left, bottom, 0.0],
                [left, top, 0.0],
                [right, bottom, 0.0],
                [right, top, 0.0],
            ],
            dtype=np.float32,
        )
    )


def _image_texcoords(origin: ImageOrigin) -> npt.NDArray[np.float32]:
    if origin == ImageOrigin.LOWER:
        values = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
    else:
        values = [[0.0, 1.0], [0.0, 0.0], [1.0, 1.0], [1.0, 0.0]]
    return np.ascontiguousarray(np.array(values, dtype=np.float32))
