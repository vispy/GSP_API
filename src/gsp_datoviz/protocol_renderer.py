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
import math
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
    AxisDimension,
    CanvasMetricsSource,
    CanvasSize,
    CapabilitySnapshot,
    ColorMapId,
    ColorScale,
    ColorbarGuide,
    ColorbarOrientation,
    ColorbarPlacement,
    DepthMode,
    ImageOrigin,
    ImageVisual,
    GUIDE_QUERY_PAYLOAD_KIND,
    GuideQueryPayload,
    LayoutAnchor,
    LayoutDiagnostic,
    LayoutDiagnosticStatus,
    LayoutLayer,
    LogicalPixelRect,
    MeshColorMode,
    MeshShading,
    MeshVisual,
    MarkerShape,
    MarkerVisual,
    NavigationDiagnosticCode,
    NavigationPointerEvent,
    NavigationPointerEventKind,
    NavigationResult,
    PathVisual,
    PanByAction,
    PointVisual,
    ResetViewAction,
    SegmentVisual,
    SetViewAction,
    TextVisual,
    Texture2D,
    TextureFilter,
    TextAnchorX,
    TextAnchorY,
    StrokeCap,
    StrokeJoin,
    View3D,
    OrthographicProjection3D,
    PerspectiveProjection3D,
    QueryCoordinateSpace,
    QueryDiagnostic,
    QueryDiagnosticSeverity,
    QueryHitPolicy,
    QueryPayload,
    QueryRequest,
    QueryResult,
    QueryScope,
    QueryStatus,
    RenderTarget,
    ResolvedCanvas,
    ResolvedGuideBox,
    ResolvedLayoutSnapshot,
    project_view3d_data_point,
    resolve_view3d_projection_snapshot,
    SCALAR_COLOR_QUERY_PAYLOAD_KIND,
    ScalarColorQueryPayload,
    ScalarColorSlot,
    TRANSFORM_QUERY_PAYLOAD_KIND,
    View2D,
    View2DNavigationController,
    View2DNavigationInputAdapter,
    View3DDiagnosticCode,
    View3DMeshPickDiagnosticCode,
    View3DMeshTrianglePickPayload,
    View3DMeshTrianglePickRequest,
    VisualFamily,
    VisualTransformBinding,
    ZoomAboutAction,
    pan_view2d,
    validate_mesh_visual_flat_lambert,
    validate_mesh_visual_texture2d_unlit,
    zoom_view2d_about,
)
from gsp.protocol.view3d import (
    Orbit3DPayload,
    Pan3DPayload,
    ResetView3DPayload,
    View3DNavigationAction,
    View3DNavigationActionKind,
    View3DNavigationResult,
    Zoom3DPayload,
    apply_view3d_navigation_action,
)
from gsp.protocol.color_mapping import (
    map_scalar_value,
    map_scalar_values,
    resolve_color_scale,
)
from gsp.protocol.visuals import CoordinateSpace, ImageInterpolation
from gsp_datoviz.v04_import import bootstrap_datoviz_v04_source
from gsp_datoviz.capabilities import (
    datoviz_v04_axis_provider_capability,
    datoviz_v04_capability_snapshot,
    datoviz_v04_capture_diagnostics,
    datoviz_v04_capture_ready,
)
from gsp_datoviz.latest_api_contract import (
    REQUIRED_DATOVIZ_V04_DEV_SYMBOLS,
    datoviz_current_api_contract_diagnostics,
)
from gsp_datoviz.query import (
    datoviz_query_view3d_ray_context,
    decode_dvz_query_result,
    datoviz_v04_query_binding_diagnostics,
    datoviz_v04_query_binding_ready,
)


_REQUIRED_DVZ_V04_FUNCTIONS = REQUIRED_DATOVIZ_V04_DEV_SYMBOLS

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

_REQUIRED_DVZ_TEXTURE2D_MESH_FUNCTIONS = (
    "dvz_field_sampling_desc",
    "dvz_visual_set_field_sampling",
    "dvz_material_desc",
    "dvz_visual_set_material",
    *_REQUIRED_DVZ_SAMPLED_FIELD_FUNCTIONS,
)

_OPTIONAL_UNVERIFIED_DVZ_MESH_FUNCTIONS: tuple[str, ...] = ()

_REQUIRED_DVZ_VIEW3D_CAMERA_FUNCTIONS = (
    "DvzCameraDesc",
    "DvzCameraView",
    "DvzCameraProjection",
    "dvz_camera_desc",
    "dvz_camera_set_orthographic_bounds",
    "dvz_panel_view3d_desc",
    "dvz_panel_set_view3d_desc",
    "dvz_panel_camera",
)

_REQUIRED_DVZ_VIEW3D_RETAINED_DATA_FUNCTIONS = (
    "DvzPanelView3DDesc",
    "DvzPanelView3DState",
    "dvz_panel_view3d_desc",
    "dvz_panel_set_view3d_desc",
    "dvz_panel_view3d_state",
    "dvz_panel_camera",
    "dvz_camera_set_view",
    "dvz_camera_get_view",
    "dvz_camera_get_projection",
    "dvz_camera_get_orthographic_bounds",
)

_REQUIRED_DVZ_PANEL_FRAME_SNAPSHOT_FUNCTIONS = (
    "DvzPanelFrameInfo",
    "DvzGuideLayout",
    "DvzRenderedContribution",
    "dvz_panel_resolve_frame",
    "dvz_panel_frame_info",
    "dvz_panel_frame_guide_count",
    "dvz_panel_frame_guide_layout",
    "dvz_panel_frame_contribution_count",
    "dvz_panel_frame_contribution",
)

_REQUIRED_DVZ_PANEL_FRAME_GUIDE_QUERY_FUNCTIONS = (
    "DvzGuideHit",
    "dvz_panel_frame_guide_hit",
)


_REQUIRED_DVZ_TEXT_FUNCTIONS = (
    "dvz_text",
    "dvz_text_set_string",
    "dvz_text_style",
    "dvz_text_set_style",
    "dvz_text_set_placement",
)

_OPTIONAL_UNVERIFIED_DVZ_TEXT_FUNCTIONS: tuple[str, ...] = ()

DVZ_POINTER_EVENT_RELEASE = 0
DVZ_POINTER_EVENT_PRESS = 1
DVZ_POINTER_EVENT_MOVE = 2
DVZ_POINTER_EVENT_DOUBLE_CLICK = 5
DVZ_POINTER_EVENT_DRAG = 11
DVZ_POINTER_EVENT_DRAG_STOP = 12
DVZ_POINTER_EVENT_WHEEL = 20
DVZ_POINTER_BUTTON_LEFT = 1
DVZ_POINTER_BUTTON_RIGHT = 3
DVZ_INPUT_EVENT_POINTER = 1
DVZ_INPUT_EVENT_RESIZE = 3
DVZ_INPUT_EVENT_SCALE = 4

DVZ_FIELD_DIM_2D = 0
DVZ_FIELD_FORMAT_RGBA8_UNORM = 22
DVZ_FIELD_SEMANTIC_COLOR = 4
DVZ_COLOR_ROLE_SRGB_COLOR = 1
DVZ_COLOR_ROLE_LINEAR_COLOR = 2
DVZ_FIELD_FILTER_LINEAR = 0
DVZ_FIELD_FILTER_NEAREST = 1
DVZ_MATERIAL_MODEL_UNLIT = 0
DVZ_SCENE_TARGET_NONE = 0
DVZ_SCENE_TARGET_ITEM = 2
DVZ_QUERY_HIT_FRONTMOST = 0
DVZ_QUERY_PROFILE_UNSUPPORTED = 0
DVZ_QUERY_CAPABILITY_ITEM = 0x02
DVZ_QUERY_CAPABILITY_PIXEL = 0x10
DVZ_CAMERA_PERSPECTIVE = 0
DVZ_CAMERA_ORTHOGRAPHIC = 1
DVZ_CONTROLLER_APPLY = 0
DVZ_CONTROLLER_FIXED = 1
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
DVZ_SCENE_ANCHOR_PANEL_CENTER = 5
DVZ_SCENE_ANCHOR_PANEL_RIGHT = 6
DVZ_SCENE_ANCHOR_PANEL_BOTTOM = 8
DVZ_SCENE_ANCHOR_DATA = 10
DVZ_TEXT_RENDERER_MSDF_ATLAS = 3
DEFAULT_BACKGROUND_RGBA8 = (255, 255, 255, 255)
DATOVIZ_REVIEW_PLOT_MARGINS = (0.0, 0.0, 0.0, 0.08)

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
    return not datoviz_current_api_contract_diagnostics(module)


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


def datoviz_v04_live_input_ready(module: ModuleType | Any) -> bool:
    """Return whether the Datoviz facade exposes the S035 live input substrate."""
    return not datoviz_v04_live_input_diagnostics(module)


def datoviz_v04_live_input_diagnostics(module: ModuleType | Any) -> tuple[str, ...]:
    """Return why Datoviz live pointer input is unavailable for GSP navigation."""
    diagnostics = [
        f"missing {name}"
        for name in (
            "dvz_view_input",
            "dvz_input_subscribe_event",
            "dvz_input_unsubscribe",
            "DvzPointerEvent",
            "DvzInputEvent",
            "DvzInputEventContent",
        )
        if not hasattr(module, name)
    ]
    pointer_event_type = getattr(module, "DvzPointerEvent", None)
    if pointer_event_type is not None:
        try:
            pointer_event = pointer_event_type()
        except TypeError:
            pointer_event = None
        if pointer_event is None or not hasattr(pointer_event, "window_size"):
            diagnostics.append("DvzPointerEvent missing window_size field")
    input_event_type = getattr(module, "DvzInputEvent", None)
    if input_event_type is not None:
        try:
            input_event = input_event_type()
        except TypeError:
            input_event = None
        if input_event is None or not hasattr(input_event, "content"):
            diagnostics.append("DvzInputEvent missing content union")
    input_event_content_type = getattr(module, "DvzInputEventContent", None)
    if input_event_content_type is not None and not hasattr(
        input_event_content_type, "pointer"
    ):
        diagnostics.append("DvzInputEventContent missing pointer field")
    return tuple(diagnostics)


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


def _datoviz_texture2d_mesh_diagnostics(module: ModuleType | Any) -> tuple[str, ...]:
    """Return missing public APIs for the strict Texture2D mesh slice."""
    return tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_TEXTURE2D_MESH_FUNCTIONS
        if not hasattr(module, name)
    )


def datoviz_v04_view3d_camera_diagnostics(module: ModuleType | Any) -> tuple[str, ...]:
    """Return why Datoviz View3D camera binding is unavailable."""
    return tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_VIEW3D_CAMERA_FUNCTIONS
        if not callable(getattr(module, name, None))
    )


def datoviz_v04_view3d_retained_data_diagnostics(
    module: ModuleType | Any,
) -> tuple[str, ...]:
    """Return why retained DATA-space View3D visual attachment is unavailable."""
    return (
        *datoviz_v04_view3d_camera_diagnostics(module),
        *(
            f"missing {name}"
            for name in _REQUIRED_DVZ_VIEW3D_RETAINED_DATA_FUNCTIONS
            if not callable(getattr(module, name, None))
        ),
    )


def datoviz_v04_view3d_retained_data_ready(module: ModuleType | Any) -> bool:
    """Return whether Datoviz can keep 3D vertices in DATA space under View3D."""
    return not datoviz_v04_view3d_retained_data_diagnostics(module)


def datoviz_v04_panel_frame_snapshot_diagnostics(
    module: ModuleType | Any,
) -> tuple[str, ...]:
    """Return why Datoviz panel frame snapshot readback is unavailable."""
    missing = tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_PANEL_FRAME_SNAPSHOT_FUNCTIONS
        if not hasattr(module, name)
    )
    return missing + _datoviz_incomplete_ctypes_records(
        module,
        ("DvzPanelFrameInfo", "DvzGuideLayout", "DvzRenderedContribution"),
    )


def datoviz_v04_panel_frame_snapshot_ready(module: ModuleType | Any) -> bool:
    """Return whether the facade exposes the bounded S043 snapshot readback path."""
    return not datoviz_v04_panel_frame_snapshot_diagnostics(module)


def datoviz_v04_panel_frame_guide_query_diagnostics(
    module: ModuleType | Any,
) -> tuple[str, ...]:
    """Return why Datoviz panel frame guide hit/readback is unavailable."""
    missing = tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_PANEL_FRAME_GUIDE_QUERY_FUNCTIONS
        if not callable(getattr(module, name, None))
    )
    return missing + _datoviz_incomplete_ctypes_records(module, ("DvzGuideHit",))


def _datoviz_incomplete_ctypes_records(
    module: ModuleType | Any, names: tuple[str, ...]
) -> tuple[str, ...]:
    """Reject generated ctypes forward declarations with no usable layout."""
    diagnostics: list[str] = []
    for name in names:
        record_type = getattr(module, name, None)
        if not isinstance(record_type, type):
            continue
        try:
            is_ctypes_record = issubclass(record_type, ctypes.Structure)
        except TypeError:
            continue
        if is_ctypes_record and ctypes.sizeof(record_type) == 0:
            diagnostics.append(f"incomplete ctypes layout for {name}")
    return tuple(diagnostics)


def datoviz_v04_panel_frame_guide_query_ready(module: ModuleType | Any) -> bool:
    """Return whether the facade exposes Datoviz guide hit/readback APIs."""
    return datoviz_v04_panel_frame_snapshot_ready(
        module
    ) and not datoviz_v04_panel_frame_guide_query_diagnostics(module)


def datoviz_v04_view3d_live_navigation_diagnostics(
    module: ModuleType | Any,
) -> tuple[str, ...]:
    """Return why Datoviz View3D live navigation is unavailable."""
    diagnostics = [
        *datoviz_v04_live_input_diagnostics(module),
    ]
    if os.environ.get("GSP_DATOVIZ_ENABLE_EXPERIMENTAL_VIEW3D_NAV") != "1":
        diagnostics.append(
            "Datoviz View3D live navigation is experimental and failed manual "
            "review; set GSP_DATOVIZ_ENABLE_EXPERIMENTAL_VIEW3D_NAV=1 to opt in"
        )
    retained_diagnostics = datoviz_v04_view3d_retained_data_diagnostics(module)
    if retained_diagnostics:
        diagnostics.extend(retained_diagnostics)
        diagnostics.append(
            "Datoviz View3D live navigation requires the retained DATA-space "
            "View3D visual path from the current generated binding"
        )
    return tuple(diagnostics)


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
    bootstrap_datoviz_v04_source()
    try:
        import datoviz as dvz

        diagnostics = datoviz_current_api_contract_diagnostics(dvz)
        if diagnostics:
            raise DatovizV04Unavailable("; ".join(diagnostics))
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
        if color_pipeline == "linear_srgb":
            return
        raise DatovizV04Unavailable(
            "Datoviz legacy sRGB blend mode is unavailable: "
            "missing dvz_figure_set_color_pipeline"
        )
    setter(figure, value)


def _configure_datoviz_view3d_camera(dvz: Any, panel: Any, view3d: View3D) -> Any:
    diagnostics = datoviz_v04_view3d_camera_diagnostics(dvz)
    if diagnostics:
        raise DatovizV04Unavailable(
            "Datoviz View3D camera binding is unavailable: " + "; ".join(diagnostics)
        )

    desc = dvz.dvz_panel_view3d_desc()
    _fill_datoviz_camera_desc(dvz, _panel_view3d_camera_desc(desc), view3d)
    _require_datoviz_success(
        dvz.dvz_panel_set_view3d_desc(panel, _ctypes_pointer_arg(desc)),
        "Datoviz retained View3D descriptor setup failed",
    )
    camera = dvz.dvz_panel_camera(panel)
    if _is_null_handle(camera):
        raise DatovizV04Unsupported(
            "Datoviz retained View3D panel camera is unavailable"
        )
    _set_datoviz_camera_projection_state(dvz, camera, view3d)
    return camera


def _fill_datoviz_camera_desc(dvz: Any, desc: Any, view3d: View3D) -> None:
    for index, value in enumerate(view3d.camera.eye):
        desc.view.eye[index] = float(value)
    for index, value in enumerate(view3d.camera.target):
        desc.view.target[index] = float(value)
    for index, value in enumerate(view3d.camera.up):
        desc.view.up[index] = float(value)
    near, far = view3d.projection.near_far
    desc.projection.near_clip = float(near)
    desc.projection.far_clip = float(far)
    if isinstance(view3d.projection, PerspectiveProjection3D):
        desc.projection.type = _enum_value(
            dvz, "DvzCameraType", "DVZ_CAMERA_PERSPECTIVE", DVZ_CAMERA_PERSPECTIVE
        )
        desc.projection.fov_y = float(math.radians(view3d.projection.fov_y_degrees))
    else:
        desc.projection.type = _enum_value(
            dvz, "DvzCameraType", "DVZ_CAMERA_ORTHOGRAPHIC", DVZ_CAMERA_ORTHOGRAPHIC
        )
        desc.projection.ortho_height = float(
            abs(view3d.projection.ylim[1] - view3d.projection.ylim[0])
        )


def _set_datoviz_camera_projection_state(dvz: Any, camera: Any, view3d: View3D) -> None:
    if isinstance(view3d.projection, OrthographicProjection3D):
        _set_datoviz_camera_orthographic_bounds(dvz, camera, view3d)


def _set_datoviz_camera_orthographic_bounds(
    dvz: Any, camera: Any, view3d: View3D
) -> None:
    if not isinstance(view3d.projection, OrthographicProjection3D):
        raise DatovizV04Unsupported(
            "Datoviz orthographic bounds require OrthographicProjection3D"
        )
    x0, x1 = view3d.projection.xlim
    y0, y1 = view3d.projection.ylim
    near, far = view3d.projection.near_far
    _require_datoviz_success(
        dvz.dvz_camera_set_orthographic_bounds(
            camera, float(x0), float(x1), float(y0), float(y1), float(near), float(far)
        ),
        "Datoviz View3D orthographic bounds setup failed",
    )


def _update_datoviz_view3d_camera(dvz: Any, panel: Any, view3d: View3D) -> Any:
    diagnostics = datoviz_v04_view3d_camera_diagnostics(dvz)
    if diagnostics:
        raise DatovizV04Unavailable(
            "Datoviz retained View3D descriptor binding is unavailable: "
            + "; ".join(diagnostics)
        )
    panel_desc = dvz.dvz_panel_view3d_desc()
    _fill_datoviz_camera_desc(dvz, _panel_view3d_camera_desc(panel_desc), view3d)
    _require_datoviz_success(
        dvz.dvz_panel_set_view3d_desc(panel, _ctypes_pointer_arg(panel_desc)),
        "Datoviz retained View3D panel camera descriptor update failed",
    )
    camera = dvz.dvz_panel_camera(panel)
    if _is_null_handle(camera):
        raise DatovizV04Unsupported(
            "Datoviz retained View3D panel camera update failed"
        )
    _set_datoviz_camera_projection_state(dvz, camera, view3d)
    return camera


def _panel_view3d_camera_desc(desc: Any) -> Any:
    """Return the camera-shaped payload inside a Datoviz View3D panel descriptor."""
    return getattr(desc, "camera", desc)


def _resolve_datoviz_canvas_size(dvz: Any, requested: CanvasSize) -> ResolvedCanvas:
    desc = _datoviz_view_size_desc(dvz, requested)
    resolver = getattr(dvz, "dvz_view_size_resolve", None)
    if desc is not None and resolver is not None:
        try:
            native = resolver(desc, _datoviz_view_kind_value(dvz, "glfw"))
        except (ctypes.ArgumentError, TypeError, ValueError):
            native = None
        if native is not None:
            return _resolved_canvas_from_datoviz(requested, native)

    scale = requested.requested_device_scale or 1.0
    output_dpi = requested.reference_dpi * scale
    return requested.resolve(
        output_dpi=output_dpi,
        device_scale=scale,
        metrics_source=CanvasMetricsSource.BACKEND_DEFAULT,
    )


def _datoviz_view_size_desc(dvz: Any, requested: CanvasSize) -> Any | None:
    factory_name = {
        "pixel_exact": "dvz_view_size_desc_framebuffer_px",
        "host_logical_px": "dvz_view_size_desc_host_logical_px",
        "reference_px": "dvz_view_size_desc_reference_px",
        "physical_mm": "dvz_view_size_desc_physical_mm",
    }[requested.policy.value]
    factory = getattr(dvz, factory_name, None)
    if factory is None:
        return None
    if requested.policy.value in {"reference_px", "physical_mm"}:
        desc = factory(requested.width, requested.height, requested.reference_dpi)
    else:
        desc = factory(requested.width, requested.height)
    if requested.requested_device_scale is not None and hasattr(
        desc, "requested_device_scale"
    ):
        desc.requested_device_scale = float(requested.requested_device_scale)
    if requested.monitor_dpi_override is not None:
        _set_datoviz_monitor_dpi_override(desc, float(requested.monitor_dpi_override))
    if hasattr(desc, "strict_framebuffer_size"):
        desc.strict_framebuffer_size = bool(requested.strict_framebuffer_size)
    return desc


def _datoviz_view_kind_value(dvz: Any, name: str) -> int:
    if name == "glfw":
        return int(getattr(dvz, "DVZ_VIEW_GLFW", 1))
    return int(getattr(dvz, "DVZ_VIEW_OFFSCREEN", 2))


def _set_datoviz_monitor_dpi_override(desc: Any, dpi: float) -> None:
    if hasattr(desc, "monitor_dpi_x_override"):
        desc.monitor_dpi_x_override = dpi
    if hasattr(desc, "monitor_dpi_y_override"):
        desc.monitor_dpi_y_override = dpi
    if hasattr(desc, "monitor_dpi_override"):
        desc.monitor_dpi_override = dpi


def _resolved_canvas_from_datoviz(requested: CanvasSize, native: Any) -> ResolvedCanvas:
    fallback = requested.resolve()
    framebuffer_per_canvas_px_x = float(
        getattr(native, "framebuffer_per_canvas_px_x", 1.0)
    )
    framebuffer_per_canvas_px_y = float(
        getattr(native, "framebuffer_per_canvas_px_y", 1.0)
    )
    target_width_mm = _positive_native_float(
        native, "target_width_mm", fallback.target_width_mm
    )
    target_height_mm = _positive_native_float(
        native, "target_height_mm", fallback.target_height_mm
    )
    estimated_width_mm = _positive_native_float(
        native, "estimated_width_mm", target_width_mm
    )
    estimated_height_mm = _positive_native_float(
        native, "estimated_height_mm", target_height_mm
    )
    return ResolvedCanvas(
        requested_size=requested,
        canvas_width_px=float(getattr(native, "canvas_width_px")),
        canvas_height_px=float(getattr(native, "canvas_height_px")),
        host_logical_width=int(getattr(native, "host_logical_width")),
        host_logical_height=int(getattr(native, "host_logical_height")),
        framebuffer_width=int(getattr(native, "framebuffer_width")),
        framebuffer_height=int(getattr(native, "framebuffer_height")),
        device_scale_x=float(getattr(native, "device_scale_x", 1.0)),
        device_scale_y=float(getattr(native, "device_scale_y", 1.0)),
        canvas_to_host_scale_x=float(getattr(native, "canvas_to_host_scale_x", 1.0)),
        canvas_to_host_scale_y=float(getattr(native, "canvas_to_host_scale_y", 1.0)),
        framebuffer_per_canvas_px_x=framebuffer_per_canvas_px_x,
        framebuffer_per_canvas_px_y=framebuffer_per_canvas_px_y,
        target_width_mm=target_width_mm,
        target_height_mm=target_height_mm,
        estimated_width_mm=estimated_width_mm,
        estimated_height_mm=estimated_height_mm,
        output_dpi=float(requested.reference_dpi * framebuffer_per_canvas_px_x),
        metrics_source=CanvasMetricsSource.BACKEND_REPORTED,
        exactness=fallback.exactness,
        strict_framebuffer_size=bool(requested.strict_framebuffer_size),
    )


def _positive_native_float(native: Any, field_name: str, fallback: float) -> float:
    value = float(getattr(native, field_name, fallback))
    return value if value > 0.0 else fallback


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
class _RetainedView2DPositionUpload:
    """Source positions for CPU-mapped DATA visuals that must follow View2D changes."""

    visual_id: str
    native_visual: Any
    attr_name: str
    positions: npt.NDArray[np.float32] | npt.NDArray[np.float64]
    transform: VisualTransformBinding | None
    coordinate_space: CoordinateSpace


@dataclass
class DatovizRetainedView3DUpdateStats:
    """Counters proving retained View3D updates avoid unchanged visual buffer writes."""

    vertex_uploads: int = 0
    index_uploads: int = 0
    visual_rebuilds: int = 0
    view_projection_uniform_updates: int = 0
    snapshot_resolves: int = 0


@dataclass
class _RetainedView3DMeshAttachment:
    """Native DATA-space 3D mesh attached to a retained Datoviz View3D."""

    visual_id: str
    native_visual: Any


@dataclass(frozen=True)
class _DatovizView2DAxisState:
    """Native Datoviz axis handles and semantic configuration for one View2D."""

    x_axis: Any
    y_axis: Any
    x_label: str | None
    y_label: str | None
    grid: bool
    backend_auto_ticks: bool
    x_tick_values: tuple[float, ...]
    x_tick_labels: tuple[str, ...] | None
    y_tick_values: tuple[float, ...]
    y_tick_labels: tuple[str, ...] | None


@dataclass
class DatovizV04ProtocolRenderer:
    """Minimal point/image renderer using Datoviz v0.4 top-level functions."""

    dvz: Any = None
    color_scales: Mapping[str, ColorScale] | None = None
    texture_resources: Mapping[str, Texture2D] | None = None
    width: int = 800
    height: int = 600
    canvas_size: CanvasSize | None = None
    background_rgba8: tuple[int, int, int, int] = DEFAULT_BACKGROUND_RGBA8
    color_pipeline: DatovizColorPipeline = "legacy_srgb_blend"
    view: View2D | None = None
    view3d: View3D | None = None
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None
    panel_bounds: tuple[float, float, float, float] | None = None
    scene: Any = field(init=False)
    figure: Any = field(init=False)
    panel: Any = field(init=False)
    app: Any | None = field(default=None, init=False)
    offscreen_view: Any | None = field(default=None, init=False)
    live_view: Any | None = field(default=None, init=False)
    native_panzoom: Any | None = field(default=None, init=False)
    native_arcball: Any | None = field(default=None, init=False)
    live_navigation: "_DatovizLiveView2DNavigation | None" = field(
        default=None, init=False
    )
    live_view3d_navigation: "_DatovizLiveView3DNavigation | None" = field(
        default=None, init=False
    )
    visuals: dict[str, Any] = field(default_factory=dict, init=False)
    sampled_fields: dict[str, Any] = field(default_factory=dict, init=False)
    native_scales: dict[str, Any] = field(default_factory=dict, init=False)
    native_colormaps: dict[str, Any] = field(default_factory=dict, init=False)
    colorbars: dict[str, Any] = field(default_factory=dict, init=False)
    resolved_canvas: ResolvedCanvas = field(init=False)
    scalar_visuals: dict[str, _ScalarVisualData] = field(
        default_factory=dict, init=False
    )
    retained_view2d_position_uploads: list[_RetainedView2DPositionUpload] = field(
        default_factory=list, init=False
    )
    retained_view3d_meshes: list[_RetainedView3DMeshAttachment] = field(
        default_factory=list, init=False
    )
    retained_view3d_update_stats: DatovizRetainedView3DUpdateStats = field(
        default_factory=DatovizRetainedView3DUpdateStats, init=False
    )
    view2d_axis_state: _DatovizView2DAxisState | None = field(default=None, init=False)
    native_view3d_camera: Any | None = field(default=None, init=False)
    transform_adaptations: dict[str, tuple[str, ...]] = field(
        default_factory=dict, init=False
    )
    last_view2d_carrier_diagnostics: dict[str, object] = field(
        default_factory=dict, init=False
    )
    _cpu_map_data_visuals_to_view: bool = field(default=False, init=False)
    _closed: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.view is not None and self.view3d is not None:
            raise ValueError("Datoviz renderer accepts either view or view3d, not both")
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

        requested_size = self.canvas_size or CanvasSize.pixel_exact(
            self.width, self.height
        )
        self.resolved_canvas = _resolve_datoviz_canvas_size(self.dvz, requested_size)
        self.width = self.resolved_canvas.framebuffer_width
        self.height = self.resolved_canvas.framebuffer_height

        self.scene = self.dvz.dvz_scene()
        self.figure = self.dvz.dvz_figure(self.scene, self.width, self.height, 0)
        _set_figure_color_pipeline(self.dvz, self.figure, self.color_pipeline)
        self.panel = _create_panel(self.dvz, self.figure, self.panel_bounds)
        _set_panel_background_color(self.dvz, self.panel, self.background_rgba8)
        _configure_ndc_panel_view2d(self.dvz, self.panel)
        if self.view is not None:
            self.apply_datoviz_data_view2d(self.view)
        if self.view3d is not None:
            self.native_view3d_camera = _configure_datoviz_view3d_camera(
                self.dvz, self.panel, self.view3d
            )
            self.retained_view3d_update_stats.view_projection_uniform_updates += 1

    def capabilities(self) -> CapabilitySnapshot:
        """Return the capability snapshot for this adapter slice."""
        return datoviz_v04_capability_snapshot(self.dvz)

    def resolve_partial_layout_snapshot(
        self, *, snapshot_id_prefix: str = "layout:datoviz"
    ) -> ResolvedLayoutSnapshot:
        """Map Datoviz-reported panel frame fields into a partial GSP snapshot.

        The adapter only copies geometry and identities reported by Datoviz. Missing guide/query
        semantics remain explicit diagnostics and are intentionally not synthesized here.
        """
        return _resolve_datoviz_partial_layout_snapshot(
            self.dvz,
            self.panel,
            resolved_canvas=self.resolved_canvas,
            view=self.view,
            snapshot_id_prefix=snapshot_id_prefix,
        )

    def _canvas_px_scale(self) -> float:
        return self.resolved_canvas.framebuffer_per_canvas_px

    def _scale_canvas_px_array(
        self, values: npt.NDArray[np.float32]
    ) -> npt.NDArray[np.float32]:
        return np.ascontiguousarray(
            values.astype(np.float32, copy=False) * np.float32(self._canvas_px_scale())
        )

    def _scale_canvas_px(self, value: float) -> float:
        return float(value * self._canvas_px_scale())

    def close(self) -> None:
        """Destroy the scene when the facade exposes a destroy helper."""
        if self._closed:
            return
        if self.live_navigation is not None:
            self.live_navigation.close()
            self.live_navigation = None
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
                cpu_map_data_to_view=self._cpu_map_data_visuals_to_view,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        colors = _point_colors(visual, color_scales=self.color_scales)
        diameters = self._scale_canvas_px_array(
            _diameters_from_pixel_diameters(visual.sizes, positions.shape[0])
        )

        dvz_visual = self.dvz.dvz_point(self.scene, 0)
        _set_filled_point_style(self.dvz, dvz_visual)
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, colors)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_data(self.dvz, dvz_visual, "diameter_px", diameters)
        _add_visual_to_panel(
            self.dvz,
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=self._visual_coord_space(visual.coordinate_space),
                z_layer=0,
            ),
        )
        self.visuals[visual.id] = dvz_visual
        self._retain_view2d_position_upload(
            visual.id,
            dvz_visual,
            "position",
            visual.positions,
            visual.transform,
            visual.coordinate_space,
        )
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

    def update_point_visual(self, visual: PointVisual) -> None:
        """Update one retained point visual from semantic GSP state.

        This is an adapter operation used by bounded lifecycle/conformance probes. It keeps native
        handles private and deliberately rejects updates after close or for unknown visual IDs.
        """
        if self._closed:
            raise RuntimeError("Datoviz renderer is closed")
        native_visual = self.visuals.get(visual.id)
        if native_visual is None:
            raise ValueError(f"unknown retained point visual {visual.id!r}")

        positions = _positions_3d(
            _adapt_visual_positions(
                visual.id,
                visual.positions,
                visual.transform,
                visual.coordinate_space,
                self.view,
                self.transform_resources,
                cpu_map_data_to_view=self._cpu_map_data_visuals_to_view,
            )
        )
        colors = _point_colors(visual, color_scales=self.color_scales)
        diameters = self._scale_canvas_px_array(
            _diameters_from_pixel_diameters(visual.sizes, positions.shape[0])
        )
        _set_visual_data(self.dvz, native_visual, "position", positions)
        _set_visual_data(self.dvz, native_visual, "color", colors)
        _set_visual_data(self.dvz, native_visual, "diameter_px", diameters)

        for upload in self.retained_view2d_position_uploads:
            if upload.visual_id == visual.id:
                upload.positions = visual.positions
                upload.transform = visual.transform
                upload.coordinate_space = visual.coordinate_space
                break

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
                cpu_map_data_to_view=self._cpu_map_data_visuals_to_view,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        fill_colors = _marker_fill_colors(visual, color_scales=self.color_scales)
        diameters = self._scale_canvas_px_array(
            _diameters_from_pixel_diameters(visual.sizes, positions.shape[0])
        )
        shape_values = visual.shape_values()
        angles = np.ascontiguousarray(visual.angle_values())
        shapes = _marker_shapes(self.dvz, shape_values)

        dvz_visual = self.dvz.dvz_marker(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz marker visual allocation failed")
        _set_marker_style(
            self.dvz,
            dvz_visual,
            visual.stroke_color,
            self._scale_canvas_px(visual.stroke_width),
        )
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, fill_colors)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", fill_colors)
        _set_visual_data(self.dvz, dvz_visual, "diameter_px", diameters)
        _set_visual_data(self.dvz, dvz_visual, "angle", angles)
        _set_visual_data(self.dvz, dvz_visual, "shape", shapes)
        _add_visual_to_panel(
            self.dvz,
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=self._visual_coord_space(visual.coordinate_space),
                z_layer=0,
            ),
        )
        self.visuals[visual.id] = dvz_visual
        self._retain_view2d_position_upload(
            visual.id,
            dvz_visual,
            "position",
            visual.positions,
            visual.transform,
            visual.coordinate_space,
        )
        if visual.fill_color_encoding is not None:
            scale = resolve_color_scale(
                self.color_scales, visual.fill_color_encoding.color_scale_id
            )
            self.scalar_visuals[visual.id] = _ScalarVisualData(
                visual_id=visual.id,
                visual_family="marker",
                item_kind="marker",
                color_slot=ScalarColorSlot.FILL,
                values=np.asarray(visual.fill_color_encoding.values, dtype=np.float64),
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
                cpu_map_data_to_view=self._cpu_map_data_visuals_to_view,
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
                cpu_map_data_to_view=self._cpu_map_data_visuals_to_view,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        colors = _rgba8(visual.colors)
        widths = self._scale_canvas_px_array(
            np.ascontiguousarray(visual.width_values())
        )

        dvz_visual = self.dvz.dvz_segment(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz segment visual allocation failed")
        cap = _stroke_cap_value(self.dvz, visual.cap)
        _require_datoviz_success(
            self.dvz.dvz_segment_set_caps(dvz_visual, cap, cap),
            "Datoviz segment cap configuration failed",
        )
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, colors)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position_start", start_positions)
        _set_visual_data(self.dvz, dvz_visual, "position_end", end_positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_data(self.dvz, dvz_visual, "stroke_width_px", widths)
        _add_visual_to_panel(
            self.dvz,
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=self._visual_coord_space(visual.coordinate_space),
                z_layer=0,
            ),
        )
        self.visuals[visual.id] = dvz_visual
        self._retain_view2d_position_upload(
            visual.id,
            dvz_visual,
            "position_start",
            visual.start_positions,
            visual.transform,
            visual.coordinate_space,
        )
        self._retain_view2d_position_upload(
            visual.id,
            dvz_visual,
            "position_end",
            visual.end_positions,
            visual.transform,
            visual.coordinate_space,
        )
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
                cpu_map_data_to_view=self._cpu_map_data_visuals_to_view,
            )
        )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        colors = _expand_path_colors(visual)
        widths = self._scale_canvas_px_array(_expand_path_widths(visual))
        subpaths = np.ascontiguousarray(np.array(visual.path_lengths, dtype=np.uint32))

        dvz_visual = self.dvz.dvz_path(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz path visual allocation failed")
        cap = _stroke_cap_value(self.dvz, visual.cap)
        _require_datoviz_success(
            self.dvz.dvz_path_set_caps(dvz_visual, cap, cap),
            "Datoviz path cap configuration failed",
        )
        _require_datoviz_success(
            self.dvz.dvz_path_set_join(
                dvz_visual,
                _stroke_join_value(self.dvz, visual.join),
                float(visual.miter_limit),
            ),
            "Datoviz path join configuration failed",
        )
        _require_datoviz_success(
            _set_path_subpaths(
                self.dvz, dvz_visual, len(visual.path_lengths), subpaths
            ),
            "Datoviz path subpath configuration failed",
        )
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, colors)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_data(self.dvz, dvz_visual, "stroke_width_px", widths)
        _add_visual_to_panel(
            self.dvz,
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=self._visual_coord_space(visual.coordinate_space),
                z_layer=0,
            ),
        )
        self.visuals[visual.id] = dvz_visual
        self._retain_view2d_position_upload(
            visual.id,
            dvz_visual,
            "position",
            visual.positions,
            visual.transform,
            visual.coordinate_space,
        )
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
            raise DatovizV04Unavailable(
                "Datoviz scalar/image field binding is unavailable: "
                + "; ".join(datoviz_v04_sampled_field_diagnostics(self.dvz))
            )
        _add_visual_to_panel(
            self.dvz,
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
        texture2d_unlit = visual.canonical_shading() is MeshShading.TEXTURE2D_UNLIT
        if texture2d_unlit:
            diagnostics = _datoviz_texture2d_mesh_diagnostics(self.dvz)
            if diagnostics:
                raise DatovizV04Unsupported(
                    "meshvisual_material_texture2d_unlit_unsupported: "
                    + "; ".join(diagnostics)
                )
            validate_mesh_visual_texture2d_unlit(
                visual, texture_resources=self.texture_resources or {}
            )
        is_3d_mesh = visual.positions.shape[1] == 3
        if is_3d_mesh:
            _validate_datoviz_mesh3d_visual(visual, self.view3d)
        diagnostics = datoviz_v04_mesh_diagnostics(self.dvz)
        if diagnostics:
            raise DatovizV04Unsupported(
                "Datoviz v0.4 MeshVisual support is unavailable: "
                + "; ".join(diagnostics)
            )

        face_order: npt.NDArray[np.int64] | None = None
        adapted_positions: npt.NDArray[np.float32] | npt.NDArray[np.float64]
        retained_view3d_data_path = (
            is_3d_mesh
            and visual.coordinate_space is CoordinateSpace.DATA
            and datoviz_v04_view3d_retained_data_ready(self.dvz)
        )
        if retained_view3d_data_path:
            adapted_positions = np.ascontiguousarray(
                np.asarray(visual.positions, dtype=np.float32)
            )
        elif is_3d_mesh:
            adapted_positions = _datoviz_mesh3d_panel_ndc_positions(
                visual,
                view3d=self.view3d,
                aspect_ratio=(
                    self.resolved_canvas.host_logical_width
                    / self.resolved_canvas.host_logical_height
                ),
            )
            if visual.depth_test is not DepthMode.DISABLED:
                face_order = _mesh3d_face_depth_order(
                    adapted_positions[:, 2], visual.faces
                )
        else:
            adapted_positions = _adapt_visual_positions(
                visual.id,
                visual.positions,
                visual.transform,
                visual.coordinate_space,
                self.view,
                self.transform_resources,
                cpu_map_data_to_view=self._cpu_map_data_visuals_to_view,
            )
        _record_transform_adaptation(
            self.transform_adaptations, visual.id, visual.transform
        )
        positions, colors, indices = _datoviz_mesh_payload(
            visual,
            adapted_positions,
            view3d=self.view3d,
            face_order=face_order,
        )
        dvz_visual = self.dvz.dvz_mesh(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz mesh visual allocation failed")
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_index_data(self.dvz, dvz_visual, indices)
        if texture2d_unlit:
            self._configure_texture2d_unlit_mesh(dvz_visual, visual, positions)
        if is_3d_mesh:
            self.retained_view3d_update_stats.vertex_uploads += 1
            self.retained_view3d_update_stats.index_uploads += 1
            self.retained_view3d_update_stats.visual_rebuilds += 1
        native_depth_test = (
            visual.depth_test is not DepthMode.DISABLED
            and visual.depth_write is not DepthMode.DISABLED
            if retained_view3d_data_path
            else False
            if is_3d_mesh
            else visual.depth_test is DepthMode.ENABLED
        )
        _require_datoviz_success(
            self.dvz.dvz_visual_set_depth_test(dvz_visual, native_depth_test),
            "Datoviz mesh depth-test configuration failed",
        )
        _set_alpha_mode_if_translucent(self.dvz, dvz_visual, colors)
        _add_visual_to_panel(
            self.dvz,
            self.panel,
            dvz_visual,
            _visual_attach_desc(
                self.dvz,
                coord_space=(
                    "data"
                    if retained_view3d_data_path
                    else "view"
                    if is_3d_mesh
                    else self._visual_coord_space(visual.coordinate_space)
                ),
                z_layer=round(visual.order),
                controller_mode=(
                    "apply"
                    if retained_view3d_data_path
                    else "fixed"
                    if is_3d_mesh
                    else "apply"
                ),
            ),
        )
        self.visuals[visual.id] = dvz_visual
        if retained_view3d_data_path:
            self.retained_view3d_meshes.append(
                _RetainedView3DMeshAttachment(
                    visual_id=visual.id,
                    native_visual=dvz_visual,
                )
            )
        return dvz_visual

    def _configure_texture2d_unlit_mesh(
        self,
        dvz_visual: Any,
        visual: MeshVisual,
        positions: npt.NDArray[np.float32],
    ) -> None:
        """Bind strict RGBA8 nearest-or-linear unlit Texture2D mesh state."""
        if visual.texture2d_id is None or visual.uvs is None:
            raise DatovizV04Unsupported(
                "texture2d_unlit mesh is missing texture or UV data"
            )
        texture = (self.texture_resources or {}).get(visual.texture2d_id)
        if texture is None:
            raise DatovizV04Unsupported(
                f"texture2d_unknown_id: unknown Texture2D id {visual.texture2d_id!r}"
            )

        texcoords = np.ascontiguousarray(np.asarray(visual.uvs, dtype=np.float32))
        texcoords = texcoords.copy()
        texcoords[:, 1] = 1.0 - texcoords[:, 1]
        normals = np.zeros((positions.shape[0], 3), dtype=np.float32)
        normals[:, 2] = 1.0
        _set_visual_data(self.dvz, dvz_visual, "normal", normals)
        _set_visual_data(self.dvz, dvz_visual, "texcoords", texcoords)

        height, width = texture.image.shape[:2]
        sampled_field = self._create_rgba8_sampled_field(
            texture.image,
            width,
            height,
            color_role=DVZ_COLOR_ROLE_LINEAR_COLOR,
        )
        if not _set_visual_field(self.dvz, dvz_visual, "texture", sampled_field):
            raise DatovizV04Unsupported("Datoviz textured-mesh field binding failed")

        sampling = self.dvz.dvz_field_sampling_desc()
        if visual.texture_filter is TextureFilter.LINEAR:
            filter_member = "DVZ_FIELD_FILTER_LINEAR"
            filter_fallback = DVZ_FIELD_FILTER_LINEAR
        else:
            filter_member = "DVZ_FIELD_FILTER_NEAREST"
            filter_fallback = DVZ_FIELD_FILTER_NEAREST
        sampling.min_filter = _enum_value(
            self.dvz, "DvzFieldFilter", filter_member, filter_fallback
        )
        sampling.mag_filter = sampling.min_filter
        _require_datoviz_success(
            _set_visual_field_sampling(self.dvz, dvz_visual, "texture", sampling),
            "Datoviz textured-mesh field-slot sampling configuration failed",
        )

        material = self.dvz.dvz_material_desc()
        material.model = _enum_value(
            self.dvz,
            "DvzMaterialModel",
            "DVZ_MATERIAL_MODEL_UNLIT",
            DVZ_MATERIAL_MODEL_UNLIT,
        )
        _require_datoviz_success(
            self.dvz.dvz_visual_set_material(dvz_visual, _ctypes_pointer_arg(material)),
            "Datoviz textured-mesh unlit material configuration failed",
        )
        self.sampled_fields[visual.id] = sampled_field

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
        sizes = self._scale_canvas_px_array(visual.font_size_values())
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
            _require_datoviz_success(
                self.dvz.dvz_text_set_style(text, style),
                "Datoviz text style configuration failed",
            )

            placement = _text_placement(self.dvz)
            placement.mode = mode
            placement.anchor = _text_anchor_value(self.dvz, visual.coordinate_space)
            if visual.coordinate_space is CoordinateSpace.NDC:
                position_x, position_y = _ndc_text_screen_position(
                    positions[index],
                    self.width,
                    self.height,
                    self.panel_bounds,
                )
            else:
                position_x = float(positions[index, 0])
                position_y = float(positions[index, 1])
            placement.position[0] = position_x
            placement.position[1] = position_y
            placement.position[2] = float(np.clip(visual.z_order, -1.0, 1.0))
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

    def _visual_coord_space(self, coordinate_space: CoordinateSpace) -> str:
        if (
            coordinate_space is CoordinateSpace.DATA
            and self._cpu_map_data_visuals_to_view
        ):
            return "view"
        return _datoviz_visual_coord_space(coordinate_space)

    def _retain_view2d_position_upload(
        self,
        visual_id: str,
        native_visual: Any,
        attr_name: str,
        positions: npt.NDArray[np.float32] | npt.NDArray[np.float64],
        transform: VisualTransformBinding | None,
        coordinate_space: CoordinateSpace,
    ) -> None:
        if (
            not self._cpu_map_data_visuals_to_view
            or coordinate_space is not CoordinateSpace.DATA
        ):
            return
        self.retained_view2d_position_uploads.append(
            _RetainedView2DPositionUpload(
                visual_id=visual_id,
                native_visual=native_visual,
                attr_name=attr_name,
                positions=np.ascontiguousarray(np.asarray(positions).copy()),
                transform=transform,
                coordinate_space=coordinate_space,
            )
        )

    def _reupload_retained_view2d_positions(self, view: View2D) -> None:
        for upload in self.retained_view2d_position_uploads:
            positions = _positions_3d(
                _adapt_visual_positions(
                    upload.visual_id,
                    upload.positions,
                    upload.transform,
                    upload.coordinate_space,
                    view,
                    self.transform_resources,
                    cpu_map_data_to_view=True,
                )
            )
            _set_visual_data(
                self.dvz, upload.native_visual, upload.attr_name, positions
            )

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
        _configure_colorbar_layout(
            self.dvz,
            desc,
            guide,
            self.width,
            self.height,
            canvas_px_scale=self._canvas_px_scale(),
        )
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
        _require_datoviz_success(
            self.dvz.dvz_colorbar_set_anchor(
                colorbar, _colorbar_anchor_value(self.dvz, guide.placement)
            ),
            "Datoviz colorbar anchor configuration failed",
        )
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

    def enable_native_panzoom(self) -> Any:
        """Enable Datoviz v0.4 native pan/zoom on the renderer's live panel."""
        view_panzoom = getattr(self.dvz, "dvz_view_panzoom", None)
        if view_panzoom is None:
            raise DatovizV04Unavailable(
                "Datoviz native panzoom is unavailable: missing dvz_view_panzoom"
            )
        live_view = self._ensure_live_view()
        desc = None
        desc_factory = getattr(self.dvz, "dvz_panzoom_desc", None)
        if desc_factory is not None:
            desc = desc_factory()
            if hasattr(desc, "width"):
                desc.width = float(self.resolved_canvas.host_logical_width)
            if hasattr(desc, "height"):
                desc.height = float(self.resolved_canvas.host_logical_height)
        self.native_panzoom = view_panzoom(
            live_view,
            self.panel,
            _ctypes_pointer_arg(desc) if desc is not None else None,
        )
        if _is_null_handle(self.native_panzoom):
            raise DatovizV04Unavailable("Datoviz native panzoom creation failed")
        return self.native_panzoom

    def enable_native_view3d_arcball(self) -> Any:
        """Enable Datoviz v0.4 native arcball on the renderer's live 3D panel."""
        view_arcball = getattr(self.dvz, "dvz_view_arcball", None)
        if view_arcball is None:
            raise DatovizV04Unavailable(
                "Datoviz native arcball is unavailable: missing dvz_view_arcball"
            )
        live_view = self._ensure_live_view()
        desc = None
        desc_factory = getattr(self.dvz, "dvz_arcball_desc", None)
        if desc_factory is not None:
            desc = desc_factory()
            if hasattr(desc, "width"):
                desc.width = float(self.resolved_canvas.host_logical_width)
            if hasattr(desc, "height"):
                desc.height = float(self.resolved_canvas.host_logical_height)
        self.native_arcball = view_arcball(
            live_view,
            self.panel,
            _ctypes_pointer_arg(desc) if desc is not None else None,
        )
        if _is_null_handle(self.native_arcball):
            raise DatovizV04Unavailable("Datoviz native arcball creation failed")
        return self.native_arcball

    def enable_gsp_view2d_navigation(
        self,
        view: View2D | None = None,
        *,
        controller_id: str = "nav:datoviz-live",
        layout_snapshot_id: str = "layout:datoviz-live",
    ) -> "_DatovizLiveView2DNavigation":
        """Enable Datoviz pointer input as canonical S035 View2D navigation."""
        diagnostics = datoviz_v04_live_input_diagnostics(self.dvz)
        if diagnostics:
            raise DatovizV04Unavailable(
                "Datoviz live input binding is unavailable: " + "; ".join(diagnostics)
            )
        target_view = view or self.view
        if target_view is None:
            raise DatovizV04Unavailable(
                "Datoviz GSP navigation requires an initial View2D"
            )
        live_view = self._ensure_live_view()
        router = self.dvz.dvz_view_input(live_view)
        if _is_null_handle(router):
            raise DatovizV04Unavailable("Datoviz live input router is unavailable")
        if self.live_navigation is not None:
            self.live_navigation.close()
        self.live_navigation = _DatovizLiveView2DNavigation(
            renderer=self,
            router=router,
            live_view=live_view,
            view=target_view,
            controller_id=controller_id,
            layout_snapshot_id=layout_snapshot_id,
        )
        self.live_navigation.subscription_id = self.dvz.dvz_input_subscribe_event(
            router, self.live_navigation.handle_input_event, None
        )
        return self.live_navigation

    def enable_gsp_view3d_navigation(
        self,
        view3d: View3D | None = None,
        *,
        controller_id: str = "nav:datoviz-live-3d",
        layout_snapshot_id: str = "layout:datoviz-live-3d",
    ) -> "_DatovizLiveView3DNavigation":
        """Enable Datoviz pointer input as canonical S037 View3D navigation."""
        target_view3d = view3d or self.view3d
        if target_view3d is None:
            raise DatovizV04Unavailable(
                "Datoviz GSP View3D navigation requires an initial View3D"
            )
        diagnostics = datoviz_v04_view3d_live_navigation_diagnostics(self.dvz)
        if diagnostics:
            raise DatovizV04Unavailable("; ".join(diagnostics))
        live_view = self._ensure_live_view()
        router = self.dvz.dvz_view_input(live_view)
        if _is_null_handle(router):
            raise DatovizV04Unavailable("Datoviz live input router is unavailable")
        if self.live_view3d_navigation is not None:
            self.live_view3d_navigation.close()
        self.live_view3d_navigation = _DatovizLiveView3DNavigation(
            renderer=self,
            router=router,
            live_view=live_view,
            view3d=target_view3d,
            controller_id=controller_id,
            layout_snapshot_id=layout_snapshot_id,
        )
        self.live_view3d_navigation.subscription_id = (
            self.dvz.dvz_input_subscribe_event(
                router, self.live_view3d_navigation.handle_input_event, None
            )
        )
        return self.live_view3d_navigation

    def _create_rgba8_sampled_field(
        self,
        pixels: npt.NDArray[np.uint8],
        width: int,
        height: int,
        *,
        color_role: int = DVZ_COLOR_ROLE_SRGB_COLOR,
    ) -> Any:
        """Create and upload a scene-owned RGBA8 sampled field."""
        desc = self.dvz.dvz_sampled_field_desc()
        desc.dim = DVZ_FIELD_DIM_2D
        desc.format = DVZ_FIELD_FORMAT_RGBA8_UNORM
        desc.semantic = DVZ_FIELD_SEMANTIC_COLOR
        desc.color_role = color_role
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
        _require_datoviz_success(
            self.dvz.dvz_sampled_field_set_data(sampled_field, view),
            "Datoviz sampled-field image upload failed",
        )
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
            _require_datoviz_success(
                self.dvz.dvz_view_capture_png(view, str(path).encode()),
                "Datoviz offscreen PNG capture failed",
            )
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
            self.app,
            self.figure,
            self.resolved_canvas.framebuffer_width,
            self.resolved_canvas.framebuffer_height,
        )
        if _is_null_handle(self.offscreen_view):
            raise DatovizV04Unavailable("Datoviz offscreen view creation failed")
        return self.offscreen_view

    def _ensure_live_view(self) -> Any:
        """Create the lazy interactive app/view pair used by show()."""
        if self.live_view is not None:
            return self.live_view

        self._ensure_app("interactive")
        view_window = getattr(self.dvz, "dvz_view_window", None)
        if view_window is not None:
            self.live_view = view_window(
                self.app,
                self.figure,
                self.resolved_canvas.host_logical_width,
                self.resolved_canvas.host_logical_height,
                b"GSP Datoviz review",
            )
            if _is_null_handle(self.live_view):
                raise DatovizV04Unavailable(
                    "Datoviz interactive window view creation failed"
                )
            return self.live_view

        view_glfw = getattr(self.dvz, "dvz_view_glfw", None)
        if view_glfw is not None:
            self.live_view = view_glfw(
                self.app,
                self.figure,
                self.resolved_canvas.host_logical_width,
                self.resolved_canvas.host_logical_height,
                b"GSP Datoviz review",
            )
            if _is_null_handle(self.live_view):
                raise DatovizV04Unavailable(
                    "Datoviz interactive GLFW view creation failed"
                )
            return self.live_view

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
        if request.scope in (QueryScope.GUIDES, QueryScope.ALL_RENDERED):
            return self._query_panel_guides(request)

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

    def _query_panel_guides(self, request: QueryRequest) -> QueryResult:
        if request.coordinate_space != QueryCoordinateSpace.PANEL:
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.UNSUPPORTED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic=(
                    "Datoviz guide query requires panel logical-pixel coordinates"
                ),
                layout_snapshot_id=request.layout_snapshot_id,
            )
        if request.hit_policy != QueryHitPolicy.FRONTMOST:
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.UNSUPPORTED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic="Datoviz guide query supports frontmost hit policy only",
                layout_snapshot_id=request.layout_snapshot_id,
            )
        unsupported_payloads = tuple(
            kind
            for kind in request.requested_extension_payload_kinds
            if kind != GUIDE_QUERY_PAYLOAD_KIND
        )
        if unsupported_payloads:
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.UNSUPPORTED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic=(
                    "Datoviz guide query does not support requested extension "
                    f"payloads: {unsupported_payloads}"
                ),
                layout_snapshot_id=request.layout_snapshot_id,
            )
        if not datoviz_v04_panel_frame_guide_query_ready(self.dvz):
            diagnostics = (
                *datoviz_v04_panel_frame_snapshot_diagnostics(self.dvz),
                *datoviz_v04_panel_frame_guide_query_diagnostics(self.dvz),
            )
            prefix = (
                "all-rendered-guides-unsupported"
                if request.scope == QueryScope.ALL_RENDERED
                else "axis-guide-query-unsupported"
            )
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.UNSUPPORTED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic=(
                    f"{prefix}: Datoviz panel frame guide hit/readback is "
                    "unavailable: " + "; ".join(diagnostics)
                ),
                layout_snapshot_id=request.layout_snapshot_id,
            )
        return _query_datoviz_panel_frame_guides(
            self.dvz,
            self.panel,
            request,
            all_rendered=request.scope == QueryScope.ALL_RENDERED,
        )

    def query_view3d_ray_context(
        self, request: QueryRequest, *, layout_snapshot_id: str
    ) -> QueryResult:
        """Return a canonical View3D ray-context payload for the current Datoviz panel."""
        if self.view3d is None:
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.UNSUPPORTED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic=(
                    f"{View3DDiagnosticCode.VIEW3D_NOT_SUPPORTED.value}: "
                    "Datoviz View3D ray readback requires a renderer View3D"
                ),
                layout_snapshot_id=request.layout_snapshot_id,
                view_snapshot_id=request.view_snapshot_id,
            )
        snapshot = resolve_view3d_projection_snapshot(
            self.view3d, layout_snapshot_id=layout_snapshot_id
        )
        return datoviz_query_view3d_ray_context(
            request,
            self.view3d,
            snapshot,
            panel_bounds=_datoviz_query_panel_bounds(
                self.resolved_canvas.framebuffer_width,
                self.resolved_canvas.framebuffer_height,
                self.panel_bounds,
            ),
        )

    def query_view3d_mesh_triangle_pick(
        self,
        request: View3DMeshTrianglePickRequest,
        *,
        layout_snapshot_id: str,
    ) -> QueryResult:
        """Return structured unsupported for S044 until Datoviz has strict pick evidence."""
        diagnostic = QueryDiagnostic(
            code=View3DMeshPickDiagnosticCode.UNSUPPORTED_NO_PUBLIC_PRIMITIVE_MAP,
            severity=QueryDiagnosticSeverity.ERROR,
            message=(
                "Datoviz S044 mesh triangle picking requires public visual_id and "
                "canonical primitive_index mapping plus synchronized pick-scene freshness"
            ),
        )
        payload = View3DMeshTrianglePickPayload(
            status=QueryStatus.UNSUPPORTED,
            hit=False,
            view_id=request.view_id,
            panel_id=request.panel_id
            or (self.view3d.panel_id if self.view3d else None),
            panel_xy=request.panel_xy,
            diagnostics=(diagnostic,),
        )
        view_snapshot_id = (
            resolve_view3d_projection_snapshot(
                self.view3d, layout_snapshot_id=layout_snapshot_id
            ).view_projection_snapshot_id
            if self.view3d is not None
            else None
        )
        return QueryResult(
            request_id=f"query:{request.view_id}:mesh-pick",
            status=QueryStatus.UNSUPPORTED,
            hit=False,
            panel_coordinate=request.panel_xy,
            extension_payload_kind=payload.kind,
            extension_payload=payload,
            diagnostic=(
                diagnostic.code.value
                if isinstance(diagnostic.code, View3DMeshPickDiagnosticCode)
                else diagnostic.code
            ),
            layout_snapshot_id=layout_snapshot_id,
            view_snapshot_id=view_snapshot_id,
        )

    def _decorate_scalar_query_result(
        self, result: QueryResult, request: QueryRequest
    ) -> QueryResult:
        """Attach exact S026 scalar payloads from retained protocol scene data."""
        if result.status != QueryStatus.HIT:
            return result

        wants_scalar_payload = (
            SCALAR_COLOR_QUERY_PAYLOAD_KIND in request.requested_extension_payload_kinds
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
        self.view = view
        self._cpu_map_data_visuals_to_view = False
        self.apply_datoviz_data_view2d(view)

        x_axis = self.dvz.dvz_panel_axis(self.panel, dim_x)
        y_axis = self.dvz.dvz_panel_axis(self.panel, dim_y)

        _configure_axis_review_style(self.dvz, x_axis)
        _configure_axis_review_style(self.dvz, y_axis)
        _configure_axis_review_plot_margins(self.dvz, x_axis)
        _configure_axis_review_plot_margins(self.dvz, y_axis)

        self.view2d_axis_state = _DatovizView2DAxisState(
            x_axis=x_axis,
            y_axis=y_axis,
            x_label=x_label,
            y_label=y_label,
            grid=grid,
            backend_auto_ticks=backend_auto_ticks,
            x_tick_values=x_tick_values,
            x_tick_labels=x_tick_labels,
            y_tick_values=y_tick_values,
            y_tick_labels=y_tick_labels,
        )
        self.update_view2d_axes(view)

    def apply_datoviz_data_view2d(self, view: View2D) -> Any:
        """Apply GSP ordered data ranges and Datoviz View2D policy."""
        has_panel_domain = hasattr(self.dvz, "dvz_panel_set_domain")
        if has_panel_domain:
            _set_datoviz_panel_domains(self.dvz, self.panel, view.x_range, view.y_range)
        panel_view = _datoviz_panel_view2d_desc(self.dvz)
        descriptor_has_data_domains = _datoviz_view2d_descriptor_has_data_domains(
            panel_view
        )
        if descriptor_has_data_domains:
            _set_datoviz_data_domain(panel_view, "data_x", view.x_range)
            _set_datoviz_data_domain(panel_view, "data_y", view.y_range)
        elif not has_panel_domain:
            raise DatovizV04Unsupported(
                "Datoviz View2D data-domain setup failed: missing ordered domain carrier"
            )
        if hasattr(panel_view, "padding"):
            panel_view.padding = 0.0
        _require_datoviz_success(
            self.dvz.dvz_panel_set_view2d(self.panel, panel_view),
            "Datoviz View2D data-domain setup failed",
        )
        carrier = (
            "DvzPanelView2D.data_x/data_y"
            if descriptor_has_data_domains
            else "dvz_panel_set_domain+DvzPanelView2D policy"
        )
        self.last_view2d_carrier_diagnostics = {
            "datoviz_view2d_carrier": carrier,
            "ordered_ranges_preserved": True,
            "reversed_x": view.x_range[0] > view.x_range[1],
            "reversed_y": view.y_range[0] > view.y_range[1],
            "legacy_panel_domain_sync": has_panel_domain,
            "datoviz_visible_domain_readback": (
                "available"
                if hasattr(self.dvz, "dvz_panel_visible_domain")
                else "missing"
            ),
            "datoviz_transform_point": (
                "available"
                if hasattr(self.dvz, "dvz_panel_transform_point")
                else "missing"
            ),
        }
        return panel_view

    def apply_retained_view2d_navigation(self, view: View2D) -> Any:
        """Apply an accepted S035 navigation View2D as a retained panel update."""
        self.view = view
        panel_view = self.apply_datoviz_data_view2d(view)
        self.update_view2d_axes(view)
        return panel_view

    def apply_retained_view3d_navigation(
        self, view3d: View3D, *, layout_snapshot_id: str = "layout:datoviz"
    ) -> dict[str, object]:
        """Apply an accepted S037 View3D state as retained camera/projection updates."""
        diagnostics = datoviz_v04_view3d_retained_data_diagnostics(self.dvz)
        if diagnostics:
            raise DatovizV04Unavailable(
                "Datoviz retained View3D DATA-space visual path is unavailable: "
                + "; ".join(diagnostics)
            )
        self.native_view3d_camera = _update_datoviz_view3d_camera(
            self.dvz, self.panel, view3d
        )
        self.view3d = view3d
        self.retained_view3d_update_stats.view_projection_uniform_updates += 1
        return self.resolve_retained_view3d_state_snapshot(
            layout_snapshot_id=layout_snapshot_id
        )

    def apply_gsp_view3d_navigation_action(
        self,
        action: View3DNavigationAction,
        *,
        layout_snapshot_id: str = "layout:datoviz-live-3d",
    ) -> View3DNavigationResult:
        """Replay one canonical S037 View3D navigation action into retained Datoviz state."""
        if self.view3d is None:
            return View3DNavigationResult(
                accepted=False,
                view_id=action.view_id,
                action_kind=action.kind,
                old_revision=action.base_view_revision,
                diagnostics=(
                    f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_UNSUPPORTED.value}: "
                    "Datoviz GSP View3D navigation requires a renderer View3D",
                ),
                layout_snapshot_id=action.base_layout_snapshot_id,
            )
        result = apply_view3d_navigation_action(
            self.view3d, action, layout_snapshot_id=layout_snapshot_id
        )
        if not result.accepted or result.view is None:
            return result
        snapshot = self.apply_retained_view3d_navigation(
            result.view, layout_snapshot_id=layout_snapshot_id
        )
        state_diagnostics = _retained_view3d_state_mismatch_diagnostics(
            result.view, snapshot
        )
        if state_diagnostics:
            return View3DNavigationResult(
                accepted=False,
                view_id=result.view_id,
                action_kind=result.action_kind,
                old_revision=result.old_revision,
                diagnostics=state_diagnostics,
                layout_snapshot_id=result.layout_snapshot_id,
            )
        return result

    def resolve_retained_view3d_state_snapshot(
        self, *, layout_snapshot_id: str = "layout:datoviz"
    ) -> dict[str, object]:
        """Read back retained Datoviz View3D state and canonical GSP snapshot identity."""
        diagnostics = datoviz_v04_view3d_retained_data_diagnostics(self.dvz)
        if diagnostics:
            raise DatovizV04Unavailable(
                "Datoviz retained View3D state readback is unavailable: "
                + "; ".join(diagnostics)
            )
        if self.view3d is None:
            raise DatovizV04Unavailable(
                "Datoviz retained View3D state readback requires a renderer View3D"
            )
        state = self.dvz.DvzPanelView3DState()
        if not self.dvz.dvz_panel_view3d_state(self.panel, _ctypes_pointer_arg(state)):
            raise DatovizV04Unsupported("Datoviz retained View3D state copy failed")
        self.retained_view3d_update_stats.snapshot_resolves += 1
        projection_snapshot = resolve_view3d_projection_snapshot(
            self.view3d, layout_snapshot_id=layout_snapshot_id
        )
        view = getattr(state, "view", None)
        projection = getattr(state, "projection", None)
        return {
            "layout_snapshot_id": layout_snapshot_id,
            "view_projection_snapshot_id": (
                projection_snapshot.view_projection_snapshot_id
            ),
            "native_view_id": int(getattr(state, "view_id", 0)),
            "native_revision": int(getattr(state, "revision", 0)),
            "enabled": bool(getattr(state, "enabled", False)),
            "camera_eye": _datoviz_vec3_tuple(getattr(view, "eye", ())),
            "camera_target": _datoviz_vec3_tuple(getattr(view, "target", ())),
            "camera_up": _datoviz_vec3_tuple(getattr(view, "up", ())),
            "projection_type": int(getattr(projection, "type", 0)),
            "near_far": (
                float(getattr(projection, "near_clip", 0.0)),
                float(getattr(projection, "far_clip", 0.0)),
            ),
            "fov_y_radians": float(getattr(projection, "fov_y", 0.0)),
            "orthographic_bounds": _datoviz_orthographic_bounds_tuple(state),
        }

    def apply_adapted_view2d_navigation_cpu_remap(self, view: View2D) -> Any:
        """Apply View2D navigation for the adapted CPU-remapped DATA placement."""
        self.view = view
        panel_view = self.apply_datoviz_data_view2d(view)
        self.update_view2d_axes(view)
        self._reupload_retained_view2d_positions(view)
        return panel_view

    def update_view2d_axes(self, view: View2D) -> None:
        """Refresh native Datoviz axes from the committed canonical View2D."""
        del view
        state = self.view2d_axis_state
        if state is None:
            return
        tick_policy = self.dvz.dvz_axis_tick_policy()
        if state.backend_auto_ticks and hasattr(self.dvz, "dvz_axis_clear_ticks"):
            self.dvz.dvz_axis_clear_ticks(state.x_axis)
            self.dvz.dvz_axis_clear_ticks(state.y_axis)
        self.dvz.dvz_axis_set_tick_policy(state.x_axis, tick_policy)
        self.dvz.dvz_axis_set_tick_policy(state.y_axis, tick_policy)
        if state.x_tick_values and hasattr(self.dvz, "dvz_axis_set_ticks"):
            _set_axis_ticks(
                self.dvz, state.x_axis, state.x_tick_values, state.x_tick_labels
            )
        if state.y_tick_values and hasattr(self.dvz, "dvz_axis_set_ticks"):
            _set_axis_ticks(
                self.dvz, state.y_axis, state.y_tick_values, state.y_tick_labels
            )
        if hasattr(self.dvz, "dvz_axis_set_grid"):
            self.dvz.dvz_axis_set_grid(state.x_axis, state.grid)
            self.dvz.dvz_axis_set_grid(state.y_axis, state.grid)
        if state.x_label is not None:
            self.dvz.dvz_axis_set_label(state.x_axis, state.x_label.encode("utf-8"))
        if state.y_label is not None:
            self.dvz.dvz_axis_set_label(state.y_axis, state.y_label.encode("utf-8"))


NavigationAction = PanByAction | ZoomAboutAction | SetViewAction | ResetViewAction


class _DatovizLiveView2DNavigation:
    """Translate Datoviz pointer callbacks into S035 semantic navigation."""

    def __init__(
        self,
        *,
        renderer: DatovizV04ProtocolRenderer,
        router: Any,
        live_view: Any,
        view: View2D,
        controller_id: str,
        layout_snapshot_id: str,
    ) -> None:
        self.renderer = renderer
        self.router = router
        self.live_view = live_view
        self.view = view
        self.revision_index = 1
        self.layout_snapshot_id = layout_snapshot_id
        self.controller = View2DNavigationController(
            id=controller_id,
            panel_id=view.panel_id,
            view_id=view.id,
            current_view2d_revision="view-rev:datoviz-live-1",
            home_view=view,
        )
        self._panel_rect = self._initial_panel_rect()
        self.adapter = View2DNavigationInputAdapter(
            controller_id=self.controller.id,
            view2d_revision=self.controller.current_view2d_revision,
            panel_rect=self.panel_rect,
            layout_snapshot_id=layout_snapshot_id,
        )
        self.subscription_id: Any = None
        self._closed = False

    @property
    def panel_rect(self) -> LogicalPixelRect:
        """Return the live Datoviz panel rectangle in host logical pixels."""
        return self._panel_rect

    def _initial_panel_rect(self) -> LogicalPixelRect:
        """Return the initial live Datoviz panel rectangle in host logical pixels."""
        return LogicalPixelRect(
            x=0.0,
            y=0.0,
            width=float(self.renderer.resolved_canvas.host_logical_width),
            height=float(self.renderer.resolved_canvas.host_logical_height),
        )

    def close(self) -> None:
        """Unsubscribe from Datoviz pointer callbacks."""
        if self._closed:
            return
        unsubscribe = getattr(self.renderer.dvz, "dvz_input_unsubscribe", None)
        if unsubscribe is not None and self.subscription_id is not None:
            unsubscribe(self.router, self.subscription_id)
        else:
            unsubscribe_event = getattr(
                self.renderer.dvz, "dvz_input_unsubscribe_event", None
            )
            if unsubscribe_event is not None:
                unsubscribe_event(self.router, self.handle_input_event, None)
        self._closed = True

    def handle_input_event(self, _router: Any, event_ptr: Any, _user_data: Any) -> None:
        """Handle one routed Datoviz input callback."""
        input_event = getattr(event_ptr, "contents", event_ptr)
        input_event_type = int(getattr(input_event, "type"))
        if input_event_type == _enum_value(
            self.renderer.dvz,
            "DvzInputEventType",
            "DVZ_INPUT_EVENT_POINTER",
            DVZ_INPUT_EVENT_POINTER,
        ):
            pointer_event = getattr(input_event.content, "pointer")
            self.handle_pointer_event(_router, pointer_event, _user_data)
            return
        if input_event_type == _enum_value(
            self.renderer.dvz,
            "DvzInputEventType",
            "DVZ_INPUT_EVENT_RESIZE",
            DVZ_INPUT_EVENT_RESIZE,
        ):
            self.handle_resize_event(getattr(input_event.content, "resize"))
            return
        if input_event_type == _enum_value(
            self.renderer.dvz,
            "DvzInputEventType",
            "DVZ_INPUT_EVENT_SCALE",
            DVZ_INPUT_EVENT_SCALE,
        ):
            self._refresh_view_after_viewport_change()

    def handle_pointer_event(
        self, _router: Any, event_ptr: Any, _user_data: Any
    ) -> None:
        """Handle one raw Datoviz pointer callback."""
        event = getattr(event_ptr, "contents", event_ptr)
        pointer_event = _navigation_pointer_event_from_datoviz(self.renderer.dvz, event)
        if pointer_event is None:
            return
        self._apply_event(pointer_event)

    def handle_resize_event(self, event: Any) -> None:
        """Update the live logical panel size from one Datoviz resize event."""
        width, height = _datoviz_resize_logical_size(event)
        if width <= 0.0 or height <= 0.0:
            return
        self._panel_rect = LogicalPixelRect(x=0.0, y=0.0, width=width, height=height)
        self.adapter.set_panel_rect(self._panel_rect)
        self._refresh_view_after_viewport_change()

    def _apply_event(self, event: NavigationPointerEvent) -> None:
        self.adapter.set_panel_rect(self.panel_rect)
        action = self.adapter.handle_pointer_event(event)
        if action is None:
            return
        result = _apply_view2d_navigation_action(
            self.controller,
            self.view,
            self.adapter.panel_rect,
            action,
            next_view2d_revision=self._next_revision(),
            view_snapshot_id=f"view-snapshot:datoviz-live-{self.revision_index}",
            expected_layout_snapshot_id=self.layout_snapshot_id,
        )
        if (
            not result.accepted
            or result.view is None
            or result.new_view2d_revision is None
        ):
            return
        self.view = result.view
        self.controller = replace(
            self.controller, current_view2d_revision=result.new_view2d_revision
        )
        self.adapter.accept_navigation_result(result)
        self.renderer.apply_retained_view2d_navigation(result.view)
        request_frame = getattr(self.renderer.dvz, "dvz_view_request_frame", None)
        if request_frame is not None:
            request_frame(self.live_view)

    def _refresh_view_after_viewport_change(self) -> None:
        self.renderer.update_view2d_axes(self.view)
        request_frame = getattr(self.renderer.dvz, "dvz_view_request_frame", None)
        if request_frame is not None:
            request_frame(self.live_view)

    def _next_revision(self) -> str:
        self.revision_index += 1
        return f"view-rev:datoviz-live-{self.revision_index}"


class _DatovizLiveView3DNavigation:
    """Translate Datoviz pointer callbacks into S037 semantic View3D navigation."""

    def __init__(
        self,
        *,
        renderer: DatovizV04ProtocolRenderer,
        router: Any,
        live_view: Any,
        view3d: View3D,
        controller_id: str,
        layout_snapshot_id: str,
    ) -> None:
        self.renderer = renderer
        self.router = router
        self.live_view = live_view
        self.view3d = view3d
        self.home_view3d = view3d
        self.controller_id = controller_id
        self.layout_snapshot_id = layout_snapshot_id
        self._panel_rect = self._initial_panel_rect()
        self._drag_last_px: tuple[float, float] | None = None
        self._drag_mode: Literal["orbit", "pan"] | None = None
        self.subscription_id: Any = None
        self._closed = False

    @property
    def panel_rect(self) -> LogicalPixelRect:
        """Return the live Datoviz panel rectangle in host logical pixels."""
        return self._panel_rect

    def _initial_panel_rect(self) -> LogicalPixelRect:
        """Return the initial live Datoviz panel rectangle in host logical pixels."""
        return LogicalPixelRect(
            x=0.0,
            y=0.0,
            width=float(self.renderer.resolved_canvas.host_logical_width),
            height=float(self.renderer.resolved_canvas.host_logical_height),
        )

    def close(self) -> None:
        """Unsubscribe from Datoviz pointer callbacks."""
        if self._closed:
            return
        unsubscribe = getattr(self.renderer.dvz, "dvz_input_unsubscribe", None)
        if unsubscribe is not None and self.subscription_id is not None:
            unsubscribe(self.router, self.subscription_id)
        else:
            unsubscribe_event = getattr(
                self.renderer.dvz, "dvz_input_unsubscribe_event", None
            )
            if unsubscribe_event is not None:
                unsubscribe_event(self.router, self.handle_input_event, None)
        self._closed = True

    def handle_input_event(self, _router: Any, event_ptr: Any, _user_data: Any) -> None:
        """Handle one routed Datoviz input callback."""
        input_event = getattr(event_ptr, "contents", event_ptr)
        input_event_type = int(getattr(input_event, "type"))
        if input_event_type == _enum_value(
            self.renderer.dvz,
            "DvzInputEventType",
            "DVZ_INPUT_EVENT_POINTER",
            DVZ_INPUT_EVENT_POINTER,
        ):
            pointer_event = getattr(input_event.content, "pointer")
            self.handle_pointer_event(_router, pointer_event, _user_data)
            return
        if input_event_type == _enum_value(
            self.renderer.dvz,
            "DvzInputEventType",
            "DVZ_INPUT_EVENT_RESIZE",
            DVZ_INPUT_EVENT_RESIZE,
        ):
            self.handle_resize_event(getattr(input_event.content, "resize"))
            return
        if input_event_type == _enum_value(
            self.renderer.dvz,
            "DvzInputEventType",
            "DVZ_INPUT_EVENT_SCALE",
            DVZ_INPUT_EVENT_SCALE,
        ):
            self._request_frame()

    def handle_pointer_event(
        self, _router: Any, event_ptr: Any, _user_data: Any
    ) -> None:
        """Handle one raw Datoviz pointer callback."""
        event = getattr(event_ptr, "contents", event_ptr)
        pointer_event = _navigation_pointer_event_from_datoviz(self.renderer.dvz, event)
        if pointer_event is None:
            return
        self._apply_event(pointer_event)

    def handle_resize_event(self, event: Any) -> None:
        """Update the live logical panel size from one Datoviz resize event."""
        width, height = _datoviz_resize_logical_size(event)
        if width <= 0.0 or height <= 0.0:
            return
        self._panel_rect = LogicalPixelRect(x=0.0, y=0.0, width=width, height=height)
        self._request_frame()

    def _apply_event(self, event: NavigationPointerEvent) -> None:
        if event.kind is NavigationPointerEventKind.BUTTON_PRESS:
            if event.left_button:
                self._drag_mode = "orbit"
            elif event.right_button:
                self._drag_mode = "pan"
            else:
                return
            self._drag_last_px = (event.x_px, event.y_px)
            return
        if event.kind is NavigationPointerEventKind.BUTTON_RELEASE:
            self._drag_last_px = None
            self._drag_mode = None
            return
        if event.kind is NavigationPointerEventKind.MOUSE_MOVE:
            self._apply_drag_event(event)
            return
        if event.kind is NavigationPointerEventKind.WHEEL and event.scroll_steps != 0.0:
            self._apply_payload(
                View3DNavigationActionKind.ZOOM,
                Zoom3DPayload(scale=1.1**event.scroll_steps),
            )
            return
        if event.kind is NavigationPointerEventKind.DOUBLE_CLICK:
            self._apply_payload(
                View3DNavigationActionKind.RESET,
                ResetView3DPayload(
                    camera=self.home_view3d.camera,
                    projection=self.home_view3d.projection,
                ),
            )

    def _apply_drag_event(self, event: NavigationPointerEvent) -> None:
        if self._drag_last_px is None or self._drag_mode is None:
            return
        last_x, last_y = self._drag_last_px
        self._drag_last_px = (event.x_px, event.y_px)
        dx_px = event.x_px - last_x
        dy_px = event.y_px - last_y
        if dx_px == 0.0 and dy_px == 0.0:
            return
        if self._drag_mode == "orbit":
            self._apply_payload(
                View3DNavigationActionKind.ORBIT,
                self._orbit_payload_from_pixels(dx_px, dy_px),
            )
        else:
            self._apply_payload(
                View3DNavigationActionKind.PAN,
                self._pan_payload_from_pixels(dx_px, dy_px),
            )

    def _apply_payload(
        self,
        kind: View3DNavigationActionKind,
        payload: Orbit3DPayload | Pan3DPayload | Zoom3DPayload | ResetView3DPayload,
    ) -> None:
        snapshot = resolve_view3d_projection_snapshot(
            self.view3d, layout_snapshot_id=self.layout_snapshot_id
        )
        action = View3DNavigationAction(
            kind=kind,
            view_id=self.view3d.id,
            base_view_revision=self.view3d.revision,
            base_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
            payload=payload,
            base_layout_snapshot_id=self.layout_snapshot_id,
        )
        result = self.renderer.apply_gsp_view3d_navigation_action(
            action, layout_snapshot_id=self.layout_snapshot_id
        )
        if not result.accepted or result.view is None:
            return
        self.view3d = result.view
        self._request_frame()

    def _orbit_payload_from_pixels(self, dx_px: float, dy_px: float) -> Orbit3DPayload:
        rect = self.panel_rect
        return Orbit3DPayload(
            delta_yaw_radians=-dx_px / rect.width * np.pi,
            delta_pitch_radians=-dy_px / rect.height * np.pi,
        )

    def _pan_payload_from_pixels(self, dx_px: float, dy_px: float) -> Pan3DPayload:
        rect = self.panel_rect
        projection = self.view3d.projection
        if isinstance(projection, OrthographicProjection3D):
            x_span = projection.xlim[1] - projection.xlim[0]
            y_span = projection.ylim[1] - projection.ylim[0]
        else:
            basis = self.view3d.camera.basis()
            target_distance = max(
                sum(
                    (target - eye) * forward
                    for target, eye, forward in zip(
                        self.view3d.camera.target,
                        self.view3d.camera.eye,
                        basis.forward,
                        strict=True,
                    )
                ),
                projection.near_far[0],
            )
            aspect_ratio = projection.aspect_ratio or (rect.width / rect.height)
            half_height = target_distance * math.tan(
                math.radians(projection.fov_y_degrees) * 0.5
            )
            x_span = 2.0 * half_height * aspect_ratio
            y_span = 2.0 * half_height
        return Pan3DPayload(
            delta_view_right=-dx_px / rect.width * x_span,
            delta_view_up=-dy_px / rect.height * y_span,
        )

    def _request_frame(self) -> None:
        request_frame = getattr(self.renderer.dvz, "dvz_view_request_frame", None)
        if request_frame is not None:
            request_frame(self.live_view)


def _navigation_pointer_event_from_datoviz(
    dvz: Any, event: Any
) -> NavigationPointerEvent | None:
    event_type = int(getattr(event, "type"))
    x_px = float(event.pos[0])
    y_px = _datoviz_pointer_y_to_gsp_logical_px(event)
    if event_type == _enum_value(
        dvz,
        "DvzPointerEventType",
        "DVZ_POINTER_EVENT_PRESS",
        DVZ_POINTER_EVENT_PRESS,
    ):
        left_button = int(getattr(event, "button", 0)) == _enum_value(
            dvz,
            "DvzPointerButton",
            "DVZ_POINTER_BUTTON_LEFT",
            DVZ_POINTER_BUTTON_LEFT,
        )
        right_button = int(getattr(event, "button", 0)) == _enum_value(
            dvz,
            "DvzPointerButton",
            "DVZ_POINTER_BUTTON_RIGHT",
            DVZ_POINTER_BUTTON_RIGHT,
        )
        return NavigationPointerEvent(
            NavigationPointerEventKind.BUTTON_PRESS,
            x_px,
            y_px,
            left_button=left_button,
            right_button=right_button,
        )
    if event_type == _enum_value(
        dvz,
        "DvzPointerEventType",
        "DVZ_POINTER_EVENT_RELEASE",
        DVZ_POINTER_EVENT_RELEASE,
    ):
        return NavigationPointerEvent(
            NavigationPointerEventKind.BUTTON_RELEASE, x_px, y_px
        )
    if event_type == _enum_value(
        dvz,
        "DvzPointerEventType",
        "DVZ_POINTER_EVENT_MOVE",
        DVZ_POINTER_EVENT_MOVE,
    ):
        return None
    if event_type == _enum_value(
        dvz,
        "DvzPointerEventType",
        "DVZ_POINTER_EVENT_DRAG",
        DVZ_POINTER_EVENT_DRAG,
    ):
        return NavigationPointerEvent(NavigationPointerEventKind.MOUSE_MOVE, x_px, y_px)
    if event_type == _enum_value(
        dvz,
        "DvzPointerEventType",
        "DVZ_POINTER_EVENT_DRAG_STOP",
        DVZ_POINTER_EVENT_DRAG_STOP,
    ):
        return NavigationPointerEvent(
            NavigationPointerEventKind.BUTTON_RELEASE, x_px, y_px
        )
    if event_type == _enum_value(
        dvz,
        "DvzPointerEventType",
        "DVZ_POINTER_EVENT_WHEEL",
        DVZ_POINTER_EVENT_WHEEL,
    ):
        return NavigationPointerEvent(
            NavigationPointerEventKind.WHEEL,
            x_px,
            y_px,
            scroll_steps=float(event.content.w.dir[1]),
        )
    if event_type == _enum_value(
        dvz,
        "DvzPointerEventType",
        "DVZ_POINTER_EVENT_DOUBLE_CLICK",
        DVZ_POINTER_EVENT_DOUBLE_CLICK,
    ):
        return NavigationPointerEvent(
            NavigationPointerEventKind.DOUBLE_CLICK,
            x_px,
            y_px,
        )
    return None


def _datoviz_pointer_y_to_gsp_logical_px(event: Any) -> float:
    window_size = getattr(event, "window_size", None)
    if window_size is not None:
        height = float(window_size[1])
        if height > 0.0:
            return height - float(event.pos[1])
    return float(event.pos[1])


def _datoviz_resize_logical_size(event: Any) -> tuple[float, float]:
    width = float(getattr(event, "window_width", 0))
    height = float(getattr(event, "window_height", 0))
    if width > 0.0 and height > 0.0:
        return width, height

    framebuffer_width = float(getattr(event, "framebuffer_width", 0))
    framebuffer_height = float(getattr(event, "framebuffer_height", 0))
    scale_x = float(getattr(event, "content_scale_x", 1.0))
    scale_y = float(getattr(event, "content_scale_y", 1.0))
    if (
        framebuffer_width > 0.0
        and framebuffer_height > 0.0
        and scale_x > 0.0
        and scale_y > 0.0
    ):
        return framebuffer_width / scale_x, framebuffer_height / scale_y
    return 0.0, 0.0


def _apply_view2d_navigation_action(
    controller: View2DNavigationController,
    current_view: View2D,
    panel_rect: LogicalPixelRect,
    action: NavigationAction,
    *,
    next_view2d_revision: str,
    view_snapshot_id: str | None,
    expected_layout_snapshot_id: str,
) -> NavigationResult:
    if action.controller_id != controller.id:
        return _reject_navigation_action(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_UNSUPPORTED,
            "navigation action targets a different controller",
        )
    if action.view2d_revision != controller.current_view2d_revision:
        return _reject_navigation_action(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_STALE_VIEW,
            "navigation action references a stale View2D revision",
        )
    if action.layout_snapshot_id not in (None, expected_layout_snapshot_id):
        return _reject_navigation_action(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_STALE_LAYOUT,
            "navigation action references a stale layout snapshot",
        )
    if isinstance(action, PanByAction):
        next_view = pan_view2d(current_view, panel_rect, action.dx_px, action.dy_px)
    elif isinstance(action, ZoomAboutAction):
        next_view = zoom_view2d_about(
            current_view,
            panel_rect,
            action.anchor_px,
            action.factor_x,
            action.factor_y,
        )
    elif isinstance(action, SetViewAction):
        next_view = action.view
    elif isinstance(action, ResetViewAction) and controller.home_view is not None:
        next_view = controller.home_view
    else:
        return _reject_navigation_action(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_UNSUPPORTED,
            "unsupported navigation action",
        )
    return NavigationResult(
        accepted=True,
        controller_id=controller.id,
        old_view2d_revision=controller.current_view2d_revision,
        new_view2d_revision=next_view2d_revision,
        view=next_view,
        view_snapshot_id=view_snapshot_id,
        layout_snapshot_id=action.layout_snapshot_id or expected_layout_snapshot_id,
    )


def _reject_navigation_action(
    controller: View2DNavigationController,
    action: NavigationAction,
    code: NavigationDiagnosticCode,
    message: str,
) -> NavigationResult:
    return NavigationResult(
        accepted=False,
        controller_id=controller.id,
        old_view2d_revision=action.view2d_revision,
        diagnostics=(f"{code.value}: {message}",),
        layout_snapshot_id=action.layout_snapshot_id,
    )


def _configure_axis_review_style(dvz: Any, axis: Any) -> None:
    style_factory = getattr(dvz, "dvz_axis_style", None)
    style_setter = getattr(dvz, "dvz_axis_set_style", None)
    if style_factory is None or style_setter is None:
        return
    style = style_factory()
    if hasattr(style, "spine_width"):
        style.spine_width = 1.75
    if hasattr(style, "major_tick_width"):
        style.major_tick_width = 1.5
    if hasattr(style, "minor_tick_width"):
        style.minor_tick_width = 1.0
    if hasattr(style, "grid_width"):
        style.grid_width = 1.0
    if hasattr(style, "major_tick_length"):
        style.major_tick_length = 7.0
    if hasattr(style, "minor_tick_length"):
        style.minor_tick_length = 4.0
    if hasattr(style, "tick_gap_px"):
        style.tick_gap_px = 5.0
    if hasattr(style, "label_gap_px"):
        style.label_gap_px = 9.0
    if hasattr(style, "tick_size_px"):
        style.tick_size_px = 15.0
    if hasattr(style, "label_size_px"):
        style.label_size_px = 17.0
    if hasattr(style, "plot_margin_left"):
        style.plot_margin_left = DATOVIZ_REVIEW_PLOT_MARGINS[0]
    if hasattr(style, "plot_margin_right"):
        style.plot_margin_right = DATOVIZ_REVIEW_PLOT_MARGINS[1]
    if hasattr(style, "plot_margin_bottom"):
        style.plot_margin_bottom = DATOVIZ_REVIEW_PLOT_MARGINS[2]
    if hasattr(style, "plot_margin_top"):
        style.plot_margin_top = DATOVIZ_REVIEW_PLOT_MARGINS[3]
    if hasattr(style, "show_spine"):
        style.show_spine = True
    if hasattr(style, "show_major_ticks"):
        style.show_major_ticks = True
    if hasattr(style, "show_minor_ticks"):
        style.show_minor_ticks = True
    _assign_style_color(style, "spine_color", (32, 32, 32, 255))
    _assign_style_color(style, "major_tick_color", (32, 32, 32, 255))
    _assign_style_color(style, "minor_tick_color", (90, 90, 90, 220))
    _assign_style_color(style, "grid_color", (150, 150, 150, 190))
    _require_datoviz_success(
        style_setter(axis, style),
        "Datoviz axis style configuration failed",
    )


def _configure_axis_review_plot_margins(dvz: Any, axis: Any) -> None:
    margin_setter = getattr(dvz, "dvz_axis_set_plot_margins", None)
    if margin_setter is None:
        return
    _require_datoviz_success(
        margin_setter(axis, *DATOVIZ_REVIEW_PLOT_MARGINS),
        "Datoviz axis plot margin configuration failed",
    )


def _assign_style_color(
    style: Any, field_name: str, color: tuple[int, int, int, int]
) -> None:
    target = getattr(style, field_name, None)
    if target is None:
        return
    for index, channel in enumerate(color):
        target[index] = channel


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


def _datoviz_view2d_descriptor_has_data_domains(panel_view: Any) -> bool:
    for field_name in ("data_x", "data_y"):
        domain = getattr(panel_view, field_name, None)
        if domain is None or not hasattr(domain, "min") or not hasattr(domain, "max"):
            return False
    return True


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
        _require_datoviz_success(
            setter(panel, dim, float(limits[0]), float(limits[1])),
            "Datoviz panel data-domain setup failed",
        )


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
    _require_datoviz_success(
        result,
        "Datoviz explicit axis tick configuration failed",
    )


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
    *,
    cpu_map_data_to_view: bool = False,
) -> npt.NDArray[np.float32] | npt.NDArray[np.float64]:
    transformed = _cpu_adapt_affine_positions(
        visual_id, positions, transform, transform_resources
    )
    if coordinate_space is CoordinateSpace.NDC:
        return transformed
    if coordinate_space is CoordinateSpace.DATA:
        if cpu_map_data_to_view:
            if view is None:
                raise DatovizV04Unsupported(
                    "Datoviz data-to-view CPU adaptation requires View2D limits"
                )
            return _map_view2d_data_positions_to_view(transformed, view)
        return transformed
    raise DatovizV04Unsupported(
        f"Datoviz visual coordinate space is unsupported: {coordinate_space.value}"
    )


def _map_view2d_data_positions_to_view(
    positions: npt.NDArray[np.float32] | npt.NDArray[np.float64], view: View2D
) -> npt.NDArray[np.float32] | npt.NDArray[np.float64]:
    array = np.asarray(positions)
    mapped = array.astype(np.float64, copy=True)
    x0, x1 = view.x_range
    y0, y1 = view.y_range
    mapped[:, 0] = ((mapped[:, 0] - x0) / (x1 - x0)) * 2.0 - 1.0
    mapped[:, 1] = ((mapped[:, 1] - y0) / (y1 - y0)) * 2.0 - 1.0
    return np.ascontiguousarray(mapped.astype(array.dtype, copy=False))


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


def _validate_datoviz_mesh3d_visual(visual: MeshVisual, view3d: View3D | None) -> None:
    if visual.canonical_shading() is MeshShading.FLAT_LAMBERT:
        try:
            validate_mesh_visual_flat_lambert(visual, view3d=view3d)
        except ValueError as exc:
            raise DatovizV04Unsupported(str(exc)) from exc
    if visual.transform is not None:
        raise DatovizV04Unsupported(
            f"{View3DDiagnosticCode.MESH3D_TRANSFORM_UNSUPPORTED.value}: "
            "Datoviz MeshVisual 3D path does not apply 2D affine transforms"
        )
    if visual.coordinate_space is CoordinateSpace.DATA and view3d is None:
        raise DatovizV04Unsupported(
            f"{View3DDiagnosticCode.MESH3D_REQUIRES_VIEW3D.value}: "
            "Datoviz MeshVisual DATA positions3d require View3D"
        )
    if visual.coordinate_space not in {CoordinateSpace.DATA, CoordinateSpace.NDC}:
        raise DatovizV04Unsupported(
            f"{View3DDiagnosticCode.MESH3D_COORDINATE_SPACE_UNSUPPORTED.value}: "
            f"unsupported MeshVisual 3D coordinate_space {visual.coordinate_space!r}"
        )
    if visual.color is None:
        return
    colors = _rgba8(np.asarray(visual.color))
    if bool(np.any(colors.reshape(-1, 4)[:, 3] < 255)):
        raise DatovizV04Unsupported(
            f"{View3DDiagnosticCode.MESH3D_ALPHA_NOT_STRICT.value}: "
            "Datoviz MeshVisual 3D depth path requires opaque colors"
        )


def _datoviz_mesh3d_panel_ndc_positions(
    visual: MeshVisual, *, view3d: View3D | None, aspect_ratio: float
) -> npt.NDArray[np.float64]:
    source = np.asarray(visual.positions, dtype=np.float64)
    if visual.coordinate_space is CoordinateSpace.DATA:
        if view3d is None:
            raise DatovizV04Unsupported(
                f"{View3DDiagnosticCode.MESH3D_REQUIRES_VIEW3D.value}: "
                "Datoviz MeshVisual DATA positions3d require View3D"
            )
        return np.asarray(
            [
                project_view3d_data_point(
                    view3d, tuple(point), aspect_ratio=aspect_ratio
                )
                for point in source
            ],
            dtype=np.float64,
        )
    if visual.coordinate_space is CoordinateSpace.NDC:
        return source
    raise DatovizV04Unsupported(
        f"{View3DDiagnosticCode.MESH3D_COORDINATE_SPACE_UNSUPPORTED.value}: "
        f"unsupported MeshVisual 3D coordinate_space {visual.coordinate_space!r}"
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
    *,
    view3d: View3D | None = None,
    face_order: npt.NDArray[np.int64] | None = None,
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

    if visual.canonical_shading() is MeshShading.FLAT_LAMBERT:
        colors = _resolve_datoviz_flat_lambert_facecolors(
            visual,
            np.asarray(visual.color),
            color_mode=color_mode,
            view3d=view3d,
        )
        color_mode = MeshColorMode.FACE

    if face_order is not None:
        faces = faces[face_order]
        if color_mode is MeshColorMode.FACE:
            colors = colors.reshape(visual.faces.shape[0], 4)[face_order]

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


def _mesh3d_face_depth_order(
    vertex_depth: npt.NDArray[np.float64], faces: npt.NDArray[np.integer]
) -> npt.NDArray[np.int64]:
    face_depth = np.mean(vertex_depth[np.asarray(faces, dtype=np.uint32)], axis=1)
    return np.argsort(-face_depth, kind="stable")


def _resolve_datoviz_flat_lambert_facecolors(
    visual: MeshVisual,
    colors: npt.NDArray[Any],
    *,
    color_mode: MeshColorMode,
    view3d: View3D | None,
) -> npt.NDArray[np.uint8]:
    try:
        validate_mesh_visual_flat_lambert(visual, view3d=view3d)
    except ValueError as exc:
        raise DatovizV04Unsupported(str(exc)) from exc
    if view3d is None:
        raise DatovizV04Unsupported(
            "flat_lambert_requires_view3d: flat_lambert requires a View3D"
        )
    if color_mode is MeshColorMode.UNIFORM:
        facecolors = np.repeat(
            np.asarray(colors).reshape(1, 4),
            visual.faces.shape[0],
            axis=0,
        )
    elif color_mode is MeshColorMode.FACE:
        facecolors = np.asarray(colors).reshape(visual.faces.shape[0], 4)
    else:
        raise DatovizV04Unsupported(
            "flat_lambert_unsupported: Datoviz S040 flat Lambert requires "
            "uniform or per-face RGBA base colors"
        )

    if facecolors.dtype == np.dtype(np.uint8):
        base = np.asarray(facecolors, dtype=np.float64) / 255.0
    else:
        base = np.clip(np.asarray(facecolors, dtype=np.float64), 0.0, 1.0)
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
    return np.ascontiguousarray(np.rint(resolved * 255.0).clip(0, 255).astype(np.uint8))


def _diameters_from_pixel_diameters(
    sizes: npt.NDArray[np.float32] | npt.NDArray[np.float64] | float,
    count: int,
) -> npt.NDArray[np.float32]:
    if isinstance(sizes, np.ndarray):
        diameters = np.asarray(sizes, dtype=np.float32)
    else:
        diameters = np.full((count,), float(sizes), dtype=np.float32)
    return np.ascontiguousarray(diameters.reshape(-1))


def _visual_attach_desc(
    dvz: Any, *, coord_space: str, z_layer: int, controller_mode: str = "apply"
) -> Any:
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

    _validate_visual_attach_desc_binding(desc)
    desc.z_layer = z_layer
    if controller_mode == "apply":
        desc.controller_mode = _controller_mode_value(
            dvz, "DVZ_CONTROLLER_APPLY", DVZ_CONTROLLER_APPLY
        )
    elif controller_mode == "fixed":
        desc.controller_mode = _controller_mode_value(
            dvz, "DVZ_CONTROLLER_FIXED", DVZ_CONTROLLER_FIXED
        )
    else:
        raise ValueError(f"unsupported Datoviz controller mode: {controller_mode}")
    if coord_space == "data":
        desc.coord_space = int(dvz.DVZ_VISUAL_COORD_DATA)
    elif coord_space == "view":
        desc.coord_space = int(dvz.DVZ_VISUAL_COORD_VIEW)
    else:
        raise ValueError(f"unsupported Datoviz coordinate space: {coord_space}")
    if hasattr(desc, "clip_rect"):
        desc.clip_rect = _enum_value(
            dvz, "DvzVisualClipRect", "DVZ_VISUAL_CLIP_AUTO", 0
        )
    if hasattr(desc, "viewport_rect"):
        desc.viewport_rect = _enum_value(
            dvz, "DvzVisualViewportRect", "DVZ_VISUAL_VIEWPORT_AUTO", 0
        )
    return desc


def _validate_visual_attach_desc_binding(desc: Any) -> None:
    missing = [
        name for name in ("clip_rect", "viewport_rect") if not hasattr(desc, name)
    ]
    if missing:
        raise DatovizV04Unavailable(
            "Datoviz Python binding is stale: DvzVisualAttachDesc is missing "
            f"{', '.join(missing)}. Regenerate Datoviz bindings with `just ctypes`."
        )


def _add_visual_to_panel(dvz: Any, panel: Any, visual: Any, attach_desc: Any) -> None:
    _require_datoviz_success(
        dvz.dvz_panel_add_visual(panel, visual, attach_desc),
        "Datoviz visual panel attachment failed",
    )


def _datoviz_visual_coord_space(coordinate_space: CoordinateSpace) -> str:
    if coordinate_space is CoordinateSpace.NDC:
        return "view"
    if coordinate_space is CoordinateSpace.DATA:
        return "data"
    raise DatovizV04Unsupported(
        f"Datoviz visual coordinate space is unsupported: {coordinate_space.value}"
    )


def _controller_mode_value(dvz: Any, name: str, fallback: int) -> int:
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzControllerMode", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _text_placement_mode_value(dvz: Any, coordinate_space: CoordinateSpace) -> int:
    if coordinate_space == CoordinateSpace.NDC:
        name = "DVZ_TEXT_PLACEMENT_SCREEN"
        fallback = DVZ_TEXT_PLACEMENT_SCREEN
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
    if coordinate_space == CoordinateSpace.NDC:
        name = "DVZ_SCENE_ANCHOR_PANEL_CENTER"
        fallback = DVZ_SCENE_ANCHOR_PANEL_CENTER
    elif coordinate_space == CoordinateSpace.DATA:
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
    if enum_type is not None and hasattr(enum_type, name):
        return int(getattr(enum_type, name))
    return fallback


def _ndc_text_screen_position(
    position: npt.NDArray[np.float32] | npt.NDArray[np.float64],
    width: int,
    height: int,
    panel_bounds: tuple[float, float, float, float] | None,
) -> tuple[float, float]:
    panel_width, panel_height = _panel_pixel_size(width, height, panel_bounds)
    scale = 0.5 * min(panel_width, panel_height)
    return float(position[0]) * scale, -float(position[1]) * scale


def _panel_pixel_size(
    width: int,
    height: int,
    panel_bounds: tuple[float, float, float, float] | None,
) -> tuple[float, float]:
    if panel_bounds is None:
        return float(width), float(height)
    _x, _y, panel_width, panel_height = panel_bounds
    if 0.0 < panel_width <= 1.0 and 0.0 < panel_height <= 1.0:
        return float(width) * panel_width, float(height) * panel_height
    return panel_width, panel_height


def _datoviz_query_panel_bounds(
    width: int,
    height: int,
    panel_bounds: tuple[float, float, float, float] | None,
) -> tuple[float, float, float, float]:
    panel_width, panel_height = _panel_pixel_size(width, height, panel_bounds)
    return (0.0, panel_width, 0.0, panel_height)


def _resolve_datoviz_partial_layout_snapshot(
    dvz: Any,
    panel: Any,
    *,
    resolved_canvas: ResolvedCanvas,
    view: View2D | None,
    snapshot_id_prefix: str,
) -> ResolvedLayoutSnapshot:
    diagnostics = datoviz_v04_panel_frame_snapshot_diagnostics(dvz)
    if diagnostics:
        raise DatovizV04Unavailable(
            "Datoviz panel frame snapshot binding is unavailable: "
            + "; ".join(diagnostics)
        )

    snapshot = dvz.dvz_panel_resolve_frame(panel)
    if _is_null_handle(snapshot):
        raise DatovizV04Unsupported("Datoviz panel frame snapshot resolution failed")
    try:
        info = dvz.DvzPanelFrameInfo()
        if not dvz.dvz_panel_frame_info(snapshot, _ctypes_pointer_arg(info)):
            raise DatovizV04Unsupported("Datoviz panel frame info copy failed")
        frame_snapshot_id = _native_uint_id(getattr(info, "snapshot_id", 0))
        if frame_snapshot_id == 0 and hasattr(dvz, "dvz_panel_frame_id"):
            frame_snapshot_id = _native_uint_id(dvz.dvz_panel_frame_id(snapshot))
        snapshot_id = f"{snapshot_id_prefix}:{frame_snapshot_id:x}"

        device_scale = _datoviz_frame_device_scale(info)
        render_target = RenderTarget(
            logical_width_px=_positive_or_fallback(
                getattr(info, "logical_width_px", 0),
                resolved_canvas.canvas_width_px,
            ),
            logical_height_px=_positive_or_fallback(
                getattr(info, "logical_height_px", 0),
                resolved_canvas.canvas_height_px,
            ),
            device_scale=device_scale,
            dpi=resolved_canvas.output_dpi,
        )
        _validate_datoviz_frame_units(info, render_target)

        guide_boxes, guide_diagnostics = _datoviz_frame_guide_boxes(
            dvz, snapshot, frame_snapshot_id
        )
        z_layers, contribution_diagnostics = _datoviz_frame_contribution_layers(
            dvz, snapshot, frame_snapshot_id
        )
        transform, transform_diagnostics = _datoviz_frame_data_to_screen_transform(info)
        grid_clip_rect = _optional_dvz_rect(getattr(info, "grid_clip_rect_px", None))

        guide_query_supported = datoviz_v04_panel_frame_guide_query_ready(dvz)
        guide_query_diagnostics = (
            (
                LayoutDiagnostic(
                    code="guide_query_native_verified",
                    status=LayoutDiagnosticStatus.RESOLVED,
                    message=(
                        "Datoviz panel frame guide hit/readback uses the same "
                        "snapshot id as guide layout records."
                    ),
                ),
                LayoutDiagnostic(
                    code="all_rendered_guides_native_verified",
                    status=LayoutDiagnosticStatus.RESOLVED,
                    message=(
                        "Datoviz panel frame contribution enumeration reports "
                        "guide contributions with snapshot ids."
                    ),
                ),
            )
            if guide_query_supported
            else (
                LayoutDiagnostic(
                    code="guide_query_missing",
                    status=LayoutDiagnosticStatus.MISSING,
                    message=(
                        "Datoviz guide hit/readback is not yet wired into GSP "
                        "query results."
                    ),
                ),
                LayoutDiagnostic(
                    code="all_rendered_guides_unsupported",
                    status=LayoutDiagnosticStatus.UNSUPPORTED,
                    message=(
                        "Rendered contributions are diagnostic snapshot evidence "
                        "only until guide hit/readback is available."
                    ),
                ),
            )
        )

        snapshot_diagnostics = (
            LayoutDiagnostic(
                code="layout_snapshot_partial",
                status=LayoutDiagnosticStatus.RESOLVED,
                message=(
                    "Datoviz panel, plot, grid clip, guide layout, and contribution "
                    "records were mapped from the native panel frame snapshot."
                ),
            ),
            *guide_query_diagnostics,
            *guide_diagnostics,
            *contribution_diagnostics,
            *transform_diagnostics,
        )
        return ResolvedLayoutSnapshot(
            snapshot_id=snapshot_id,
            render_target=render_target,
            panel_rect_px=_required_dvz_rect(info.panel_rect_px, "panel_rect_px"),
            plot_rect_px=_required_dvz_rect(info.plot_rect_px, "plot_rect_px"),
            view_id=view.id if view is not None else None,
            data_to_screen_transform=transform,
            guide_boxes=guide_boxes,
            tick_label_boxes=tuple(
                box for box in guide_boxes if box.kind == "tick_label"
            ),
            axis_label_boxes=tuple(
                box for box in guide_boxes if box.kind == "axis_label"
            ),
            title_boxes=tuple(box for box in guide_boxes if box.kind == "title"),
            legend_boxes=tuple(box for box in guide_boxes if box.kind == "legend"),
            colorbar_boxes=tuple(box for box in guide_boxes if box.kind == "colorbar"),
            grid_clip_rect_px=grid_clip_rect,
            z_layers=z_layers,
            diagnostics=snapshot_diagnostics,
        )
    finally:
        frame_unref = getattr(dvz, "dvz_panel_frame_unref", None)
        if frame_unref is not None:
            frame_unref(snapshot)


def _query_datoviz_panel_frame_guides(
    dvz: Any,
    panel: Any,
    request: QueryRequest,
    *,
    all_rendered: bool,
) -> QueryResult:
    snapshot = dvz.dvz_panel_resolve_frame(panel)
    if _is_null_handle(snapshot):
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.FAILED,
            hit=False,
            panel_coordinate=request.coordinate,
            diagnostic="Datoviz panel frame snapshot resolution failed",
            layout_snapshot_id=request.layout_snapshot_id,
        )
    try:
        info = dvz.DvzPanelFrameInfo()
        if not dvz.dvz_panel_frame_info(snapshot, _ctypes_pointer_arg(info)):
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.FAILED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic="Datoviz panel frame info copy failed",
                layout_snapshot_id=request.layout_snapshot_id,
            )
        frame_snapshot_id = _native_uint_id(getattr(info, "snapshot_id", 0))
        if frame_snapshot_id == 0 and hasattr(dvz, "dvz_panel_frame_id"):
            frame_snapshot_id = _native_uint_id(dvz.dvz_panel_frame_id(snapshot))
        native_layout_snapshot_id = f"layout:datoviz:{frame_snapshot_id:x}"
        layout_snapshot_id = request.layout_snapshot_id or native_layout_snapshot_id
        if not _datoviz_layout_snapshot_id_matches(
            layout_snapshot_id, frame_snapshot_id
        ):
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.STALE,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic=(
                    "Datoviz guide query resolved a different layout snapshot id: "
                    f"{native_layout_snapshot_id}"
                ),
                layout_snapshot_id=native_layout_snapshot_id,
            )

        x, y = request.coordinate
        hit_record = dvz.DvzGuideHit()
        if not dvz.dvz_panel_frame_guide_hit(
            snapshot, float(x), float(y), _ctypes_pointer_arg(hit_record)
        ) or not bool(getattr(hit_record, "hit", False)):
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.MISS,
                hit=False,
                panel_coordinate=request.coordinate,
                layout_snapshot_id=layout_snapshot_id,
            )
        guide_id = _native_uint_id(getattr(hit_record, "guide_id", 0))
        if guide_id == 0:
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.FAILED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic="Datoviz guide hit omitted guide_id",
                layout_snapshot_id=layout_snapshot_id,
            )
        if frame_snapshot_id and _native_uint_id(
            getattr(hit_record, "snapshot_id", 0)
        ) not in (0, frame_snapshot_id):
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.FAILED,
                hit=False,
                panel_coordinate=request.coordinate,
                diagnostic="Datoviz guide hit snapshot id did not match frame snapshot id",
                layout_snapshot_id=layout_snapshot_id,
            )

        role = _datoviz_guide_role(dvz, int(getattr(hit_record, "role", 0)))
        label = _datoviz_label(getattr(hit_record, "label", b""))
        has_data_value = bool(getattr(hit_record, "has_data_value", False))
        data_value = (
            float(getattr(hit_record, "data_value")) if has_data_value else None
        )
        item_id = (
            int(getattr(hit_record, "item_index"))
            if bool(getattr(hit_record, "has_item_index", False))
            else None
        )
        payload = GuideQueryPayload(
            guide_id=_datoviz_protocol_id("guide", guide_id),
            role=role,
            axis_dimension=_datoviz_axis_dimension_for_role(role),
            tick_value=data_value,
            text_value=label,
        )
        diagnostic = (
            "datoviz_all_rendered_guide_contribution_verified" if all_rendered else None
        )
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.HIT,
            hit=True,
            panel_coordinate=request.coordinate,
            visual_id=payload.guide_id,
            item_id=item_id,
            value=label if label is not None else data_value,
            extension_payload_kind=GUIDE_QUERY_PAYLOAD_KIND,
            extension_payload=payload,
            diagnostic=diagnostic,
            layout_snapshot_id=layout_snapshot_id,
        )
    finally:
        frame_unref = getattr(dvz, "dvz_panel_frame_unref", None)
        if frame_unref is not None:
            frame_unref(snapshot)


def _datoviz_frame_device_scale(info: Any) -> float:
    scale_x = float(getattr(info, "device_scale_x", 1.0))
    scale_y = float(getattr(info, "device_scale_y", scale_x))
    if scale_x <= 0.0 or scale_y <= 0.0:
        raise DatovizV04Unsupported(
            "Datoviz panel frame reported non-positive device scale"
        )
    if not np.isclose(scale_x, scale_y, rtol=1e-6, atol=1e-6):
        raise DatovizV04Unsupported(
            "Datoviz panel frame reported asymmetric device_scale_x/device_scale_y; "
            "GSP RenderTarget currently requires one device_scale value"
        )
    return scale_x


def _validate_datoviz_frame_units(info: Any, render_target: RenderTarget) -> None:
    framebuffer_width = float(
        getattr(info, "framebuffer_width_px", render_target.framebuffer_width_px)
    )
    framebuffer_height = float(
        getattr(info, "framebuffer_height_px", render_target.framebuffer_height_px)
    )
    if not np.isclose(framebuffer_width, render_target.framebuffer_width_px, atol=1.0):
        raise DatovizV04Unsupported(
            "Datoviz panel frame framebuffer width disagrees with logical width/device scale"
        )
    if not np.isclose(
        framebuffer_height, render_target.framebuffer_height_px, atol=1.0
    ):
        raise DatovizV04Unsupported(
            "Datoviz panel frame framebuffer height disagrees with logical height/device scale"
        )


def _datoviz_frame_guide_boxes(
    dvz: Any, snapshot: Any, frame_snapshot_id: int
) -> tuple[tuple[ResolvedGuideBox, ...], tuple[LayoutDiagnostic, ...]]:
    boxes: list[ResolvedGuideBox] = []
    diagnostics: list[LayoutDiagnostic] = []
    count = int(dvz.dvz_panel_frame_guide_count(snapshot))
    for index in range(count):
        record = dvz.DvzGuideLayout()
        if not dvz.dvz_panel_frame_guide_layout(
            snapshot, index, _ctypes_pointer_arg(record)
        ):
            diagnostics.append(
                LayoutDiagnostic(
                    code="datoviz_guide_layout_copy_failed",
                    status=LayoutDiagnosticStatus.MISSING,
                    message=f"Datoviz did not copy guide layout record {index}.",
                )
            )
            continue
        if frame_snapshot_id and _native_uint_id(
            getattr(record, "snapshot_id", 0)
        ) not in (
            0,
            frame_snapshot_id,
        ):
            diagnostics.append(
                LayoutDiagnostic(
                    code="datoviz_guide_snapshot_id_mismatch",
                    status=LayoutDiagnosticStatus.DEGRADED,
                    message=f"Guide layout record {index} did not match the frame snapshot id.",
                )
            )
        if not bool(getattr(record, "has_box", False)):
            diagnostics.append(
                LayoutDiagnostic(
                    code="datoviz_guide_box_missing",
                    status=LayoutDiagnosticStatus.MISSING,
                    message=f"Datoviz guide layout record {index} has no box.",
                )
            )
            continue
        guide_id = _native_uint_id(getattr(record, "guide_id", 0))
        if guide_id == 0:
            diagnostics.append(
                LayoutDiagnostic(
                    code="datoviz_guide_id_missing",
                    status=LayoutDiagnosticStatus.MISSING,
                    message=f"Datoviz guide layout record {index} has no guide id.",
                )
            )
            continue
        anchor = None
        if bool(getattr(record, "has_anchor", False)):
            anchor_values = getattr(record, "anchor_px", None)
            if anchor_values is not None:
                anchor = LayoutAnchor(
                    x=float(anchor_values[0]), y=float(anchor_values[1])
                )
        role = _datoviz_guide_role(dvz, int(getattr(record, "role", 0)))
        boxes.append(
            ResolvedGuideBox(
                guide_id=_datoviz_protocol_id("guide", guide_id),
                kind=cast(Any, _datoviz_guide_box_kind(dvz, record)),
                rect_px=_required_dvz_rect(record.box_px, "guide.box_px"),
                anchor_px=anchor,
                role=role,
                diagnostics=(
                    LayoutDiagnostic(
                        code="datoviz_guide_layout_snapshot_first_slice",
                        status=LayoutDiagnosticStatus.ADAPTED,
                        message=(
                            "Datoviz reports retained logical-pixel guide boxes; "
                            "text boxes may be coarse and are not strict glyph extents."
                        ),
                    ),
                ),
            )
        )
    return tuple(boxes), tuple(diagnostics)


def _datoviz_frame_contribution_layers(
    dvz: Any, snapshot: Any, frame_snapshot_id: int
) -> tuple[tuple[LayoutLayer, ...], tuple[LayoutDiagnostic, ...]]:
    layers: list[LayoutLayer] = []
    diagnostics: list[LayoutDiagnostic] = []
    count = int(dvz.dvz_panel_frame_contribution_count(snapshot))
    for index in range(count):
        record = dvz.DvzRenderedContribution()
        if not dvz.dvz_panel_frame_contribution(
            snapshot, index, _ctypes_pointer_arg(record)
        ):
            diagnostics.append(
                LayoutDiagnostic(
                    code="datoviz_contribution_copy_failed",
                    status=LayoutDiagnosticStatus.MISSING,
                    message=f"Datoviz did not copy rendered contribution record {index}.",
                )
            )
            continue
        if frame_snapshot_id and _native_uint_id(
            getattr(record, "snapshot_id", 0)
        ) not in (
            0,
            frame_snapshot_id,
        ):
            diagnostics.append(
                LayoutDiagnostic(
                    code="datoviz_contribution_snapshot_id_mismatch",
                    status=LayoutDiagnosticStatus.DEGRADED,
                    message=f"Rendered contribution record {index} did not match the frame snapshot id.",
                )
            )
        contribution_id = _native_uint_id(getattr(record, "contribution_id", 0))
        if contribution_id == 0:
            diagnostics.append(
                LayoutDiagnostic(
                    code="datoviz_contribution_id_missing",
                    status=LayoutDiagnosticStatus.MISSING,
                    message=f"Datoviz rendered contribution record {index} has no contribution id.",
                )
            )
            continue
        layers.append(
            LayoutLayer(
                object_id=_datoviz_protocol_id("contribution", contribution_id),
                layer=_datoviz_contribution_layer(dvz, int(getattr(record, "kind", 0))),
                z_order=float(index),
            )
        )
    if count:
        diagnostics.append(
            LayoutDiagnostic(
                code="datoviz_rendered_contributions_reported",
                status=LayoutDiagnosticStatus.NATIVE,
                message=f"Datoviz reported {count} rendered contribution records.",
            )
        )
    return tuple(layers), tuple(diagnostics)


def _datoviz_frame_data_to_screen_transform(
    info: Any,
) -> tuple[tuple[float, ...], tuple[LayoutDiagnostic, ...]]:
    if not (
        bool(getattr(info, "has_valid_visible_x", False))
        and bool(getattr(info, "has_valid_visible_y", False))
    ):
        return (
            (1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
            (
                LayoutDiagnostic(
                    code="datoviz_data_to_screen_transform_missing",
                    status=LayoutDiagnosticStatus.MISSING,
                    message="Datoviz did not report valid visible data ranges for a 2D transform.",
                ),
            ),
        )
    x0, x1 = (float(value) for value in getattr(info, "visible_data_x"))
    y0, y1 = (float(value) for value in getattr(info, "visible_data_y"))
    if np.isclose(x0, x1) or np.isclose(y0, y1):
        return (
            (1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
            (
                LayoutDiagnostic(
                    code="datoviz_data_to_screen_transform_degenerate",
                    status=LayoutDiagnosticStatus.DEGRADED,
                    message="Datoviz reported a degenerate visible data range.",
                ),
            ),
        )
    plot = _required_dvz_rect(info.plot_rect_px, "plot_rect_px")
    sx = plot.width / (x1 - x0)
    sy = plot.height / (y1 - y0)
    tx = plot.x - sx * x0
    ty = plot.y - sy * y0
    return (sx, 0.0, tx, 0.0, sy, ty), ()


def _datoviz_guide_box_kind(dvz: Any, record: Any) -> str:
    role = int(getattr(record, "role", 0))
    if role in _datoviz_enum_values(
        dvz,
        "DvzGuideRole",
        {
            "DVZ_GUIDE_ROLE_AXIS_TICK_LABEL": 4,
            "DVZ_GUIDE_ROLE_COLORBAR_TICK_LABEL": 8,
        },
    ):
        return "tick_label"
    if role in _datoviz_enum_values(
        dvz,
        "DvzGuideRole",
        {
            "DVZ_GUIDE_ROLE_AXIS_LABEL": 5,
        },
    ):
        return "axis_label"
    if role in _datoviz_enum_values(
        dvz,
        "DvzGuideRole",
        {
            "DVZ_GUIDE_ROLE_AXIS_GRID": 3,
        },
    ):
        return "grid"
    if role in _datoviz_enum_values(
        dvz,
        "DvzGuideRole",
        {
            "DVZ_GUIDE_ROLE_COLORBAR": 6,
            "DVZ_GUIDE_ROLE_COLORBAR_RAMP": 7,
            "DVZ_GUIDE_ROLE_COLORBAR_TITLE": 9,
        },
    ):
        return "colorbar"
    if role in _datoviz_enum_values(
        dvz,
        "DvzGuideRole",
        {
            "DVZ_GUIDE_ROLE_LEGEND": 10,
            "DVZ_GUIDE_ROLE_LEGEND_ENTRY": 11,
            "DVZ_GUIDE_ROLE_LEGEND_TITLE": 12,
        },
    ):
        return "legend"
    if role in _datoviz_enum_values(
        dvz,
        "DvzGuideRole",
        {
            "DVZ_GUIDE_ROLE_GUIDE_LABEL": 15,
        },
    ):
        return "title"
    return "axis"


def _datoviz_guide_role(dvz: Any, role: int) -> str:
    names = {
        "DVZ_GUIDE_ROLE_X_AXIS": 1,
        "DVZ_GUIDE_ROLE_Y_AXIS": 2,
        "DVZ_GUIDE_ROLE_AXIS_GRID": 3,
        "DVZ_GUIDE_ROLE_AXIS_TICK_LABEL": 4,
        "DVZ_GUIDE_ROLE_AXIS_LABEL": 5,
        "DVZ_GUIDE_ROLE_COLORBAR": 6,
        "DVZ_GUIDE_ROLE_COLORBAR_RAMP": 7,
        "DVZ_GUIDE_ROLE_COLORBAR_TICK_LABEL": 8,
        "DVZ_GUIDE_ROLE_COLORBAR_TITLE": 9,
        "DVZ_GUIDE_ROLE_LEGEND": 10,
        "DVZ_GUIDE_ROLE_LEGEND_ENTRY": 11,
        "DVZ_GUIDE_ROLE_LEGEND_TITLE": 12,
        "DVZ_GUIDE_ROLE_GUIDE_LINE": 13,
        "DVZ_GUIDE_ROLE_GUIDE_SPAN": 14,
        "DVZ_GUIDE_ROLE_GUIDE_LABEL": 15,
    }
    for name, fallback in names.items():
        if role == _datoviz_enum_value(dvz, "DvzGuideRole", name, fallback):
            return name.removeprefix("DVZ_GUIDE_ROLE_").lower()
    return f"datoviz_role_{role}"


def _datoviz_axis_dimension_for_role(role: str) -> AxisDimension | None:
    if role.startswith("x_axis") or role == "axis_x":
        return AxisDimension.X
    if role.startswith("y_axis") or role == "axis_y":
        return AxisDimension.Y
    return None


def _datoviz_contribution_layer(dvz: Any, kind: int) -> str:
    if kind == _datoviz_enum_value(
        dvz,
        "DvzRenderedContributionKind",
        "DVZ_RENDERED_CONTRIBUTION_GUIDE",
        2,
    ):
        return "guide"
    if kind == _datoviz_enum_value(
        dvz,
        "DvzRenderedContributionKind",
        "DVZ_RENDERED_CONTRIBUTION_VISUAL",
        1,
    ):
        return "visual"
    return "datoviz"


def _datoviz_enum_values(
    dvz: Any, enum_type_name: str, values: Mapping[str, int]
) -> set[int]:
    return {
        _datoviz_enum_value(dvz, enum_type_name, name, fallback)
        for name, fallback in values.items()
    }


def _datoviz_enum_value(dvz: Any, enum_type_name: str, name: str, fallback: int) -> int:
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, enum_type_name, None)
    if enum_type is not None and hasattr(enum_type, name):
        return int(getattr(enum_type, name))
    return fallback


def _required_dvz_rect(rect: Any, field_name: str) -> LogicalPixelRect:
    logical_rect = _optional_dvz_rect(rect)
    if logical_rect is None:
        raise DatovizV04Unsupported(f"Datoviz panel frame missing {field_name}")
    return logical_rect


def _optional_dvz_rect(rect: Any | None) -> LogicalPixelRect | None:
    if rect is None:
        return None
    return LogicalPixelRect(
        x=float(getattr(rect, "x")),
        y=float(getattr(rect, "y")),
        width=float(getattr(rect, "width")),
        height=float(getattr(rect, "height")),
    )


def _positive_or_fallback(value: object, fallback: float) -> float:
    number = float(cast(Any, value))
    return number if number > 0.0 else float(fallback)


def _native_uint_id(value: object) -> int:
    return int(cast(Any, value))


def _datoviz_protocol_id(prefix: str, value: int) -> str:
    return f"datoviz:{prefix}:{value:x}"


def _datoviz_layout_snapshot_id_matches(snapshot_id: str, native_id: int) -> bool:
    if native_id == 0:
        return True
    return snapshot_id.endswith(f":{native_id:x}")


def _datoviz_vec3_tuple(value: object) -> tuple[float, float, float] | None:
    try:
        raw = cast(Any, value)
        return (float(raw[0]), float(raw[1]), float(raw[2]))
    except (TypeError, ValueError, IndexError):
        return None


def _datoviz_orthographic_bounds_tuple(
    state: object,
) -> tuple[float, float, float, float, float, float] | None:
    if not bool(getattr(state, "has_explicit_orthographic_bounds", False)):
        return None
    bounds = getattr(state, "orthographic_bounds", ())
    try:
        raw = cast(Any, bounds)
        return (
            float(raw[0]),
            float(raw[1]),
            float(raw[2]),
            float(raw[3]),
            float(raw[4]),
            float(raw[5]),
        )
    except (TypeError, ValueError, IndexError):
        return None


def _retained_view3d_state_mismatch_diagnostics(
    view3d: View3D, snapshot: Mapping[str, object]
) -> tuple[str, ...]:
    diagnostics: list[str] = []
    if not bool(snapshot.get("enabled", False)):
        diagnostics.append(
            f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_RESULT.value}: "
            "Datoviz retained View3D state readback is disabled"
        )
    camera = view3d.camera
    expected_vectors = {
        "camera_eye": camera.eye,
        "camera_target": camera.target,
        "camera_up": camera.up,
    }
    for key, expected in expected_vectors.items():
        observed = snapshot.get(key)
        if observed is None or not np.allclose(
            np.asarray(observed, dtype=np.float64),
            np.asarray(expected, dtype=np.float64),
        ):
            diagnostics.append(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_RESULT.value}: "
                f"Datoviz retained View3D {key} does not match canonical state"
            )
    observed_near_far = snapshot.get("near_far")
    if observed_near_far is None or not np.allclose(
        np.asarray(observed_near_far, dtype=np.float64),
        np.asarray(view3d.projection.near_far, dtype=np.float64),
    ):
        diagnostics.append(
            f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_RESULT.value}: "
            "Datoviz retained View3D near/far bounds do not match canonical state"
        )
    if isinstance(view3d.projection, OrthographicProjection3D):
        expected_bounds = (
            *view3d.projection.xlim,
            *view3d.projection.ylim,
            *view3d.projection.near_far,
        )
        observed_bounds = snapshot.get("orthographic_bounds")
        if observed_bounds is None or not np.allclose(
            np.asarray(observed_bounds, dtype=np.float64),
            np.asarray(expected_bounds, dtype=np.float64),
        ):
            diagnostics.append(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_RESULT.value}: "
                "Datoviz retained View3D orthographic bounds do not match canonical state"
            )
    elif isinstance(view3d.projection, PerspectiveProjection3D):
        observed_fov_y = snapshot.get("fov_y_radians")
        expected_fov_y = math.radians(view3d.projection.fov_y_degrees)
        if not isinstance(observed_fov_y, (int, float)) or not np.isclose(
            float(observed_fov_y), expected_fov_y
        ):
            diagnostics.append(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_RESULT.value}: "
                "Datoviz retained View3D perspective fov_y does not match canonical state"
            )
    return tuple(diagnostics)


def _datoviz_label(value: object) -> str | None:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, bytearray):
        raw = bytes(value)
    elif isinstance(value, str):
        return value or None
    else:
        try:
            raw = bytes(cast(Any, value))
        except (TypeError, ValueError):
            return None
    text = raw.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
    return text or None


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
    _require_datoviz_success(
        dvz.dvz_text_set_placement(text, placement),
        "Datoviz text placement configuration failed",
    )


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
    return np.ascontiguousarray(np.rint(mapped * 255.0).clip(0, 255).astype(np.uint8))


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


def _datoviz_call_succeeded(result: Any) -> bool:
    """Accept both old bool-returning mutators and pre-RC DvzResult returns."""
    if result is None:
        return True
    if isinstance(result, bool):
        return result
    value = getattr(result, "value", None)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 0
    if isinstance(result, int):
        return result == 0
    return bool(result)


def _require_datoviz_success(result: Any, message: str) -> None:
    if not _datoviz_call_succeeded(result):
        raise DatovizV04Unsupported(message)


def _set_visual_field(
    dvz: Any, visual: Any, slot_name: str, sampled_field: Any
) -> bool:
    try:
        return _datoviz_call_succeeded(
            dvz.dvz_visual_set_field(visual, slot_name, sampled_field)
        )
    except (ctypes.ArgumentError, TypeError):
        return _datoviz_call_succeeded(
            dvz.dvz_visual_set_field(visual, slot_name.encode("utf-8"), sampled_field)
        )


def _set_visual_field_sampling(
    dvz: Any, visual: Any, slot_name: str, sampling: Any
) -> Any:
    """Call the slot-sampling setter across direct and ctypes facades."""
    sampling_arg = _ctypes_pointer_arg(sampling)
    try:
        return dvz.dvz_visual_set_field_sampling(visual, slot_name, sampling_arg)
    except (ctypes.ArgumentError, TypeError):
        return dvz.dvz_visual_set_field_sampling(
            visual, slot_name.encode("utf-8"), sampling_arg
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


def _colorbar_orientation_value(dvz: Any, orientation: ColorbarOrientation) -> int:
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


def _colorbar_anchor_value(dvz: Any, placement: ColorbarPlacement | None) -> int:
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
    dvz: Any,
    desc: Any,
    guide: ColorbarGuide,
    width: int,
    height: int,
    *,
    canvas_px_scale: float,
) -> None:
    """Use a bounded colorbar placement for visual QA captures."""
    ramp_width_px = float(guide.style.ramp_width_px * canvas_px_scale)
    tick_length_px = float(guide.style.tick_length_px * canvas_px_scale)
    label_gap_px = float(guide.style.label_gap_px * canvas_px_scale)
    min_length_px = float(guide.style.min_length_px * canvas_px_scale)
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
        desc.ramp_width_px = ramp_width_px
    if hasattr(desc, "tick_length_px"):
        desc.tick_length_px = tick_length_px
    if hasattr(desc, "label_gap_px"):
        desc.label_gap_px = label_gap_px
    placement = getattr(desc, "placement", None)
    if placement is None:
        return
    if hasattr(placement, "space"):
        placement.space = _enum_value(
            dvz,
            "DvzPlacementSpace",
            "DVZ_PLACEMENT_SPACE_PANEL",
            DVZ_PLACEMENT_SPACE_PANEL,
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
        placement.offset_x_px = -max(48.0, float(width) * 0.060)
    if hasattr(placement, "offset_y_px"):
        placement.offset_y_px = 0.0
    if hasattr(placement, "width_px"):
        placement.width_px = ramp_width_px
    if hasattr(placement, "height_px"):
        placement.height_px = max(
            min_length_px, float(height) * guide.style.length_fraction
        )


def _configure_colorbar_format(dvz: Any, colorbar: Any) -> None:
    if not hasattr(dvz, "dvz_format_desc") or not hasattr(
        dvz, "dvz_colorbar_set_format"
    ):
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
    _require_datoviz_success(
        setter(colorbar, values, labels),
        "Datoviz colorbar explicit tick configuration failed",
    )


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
    _require_datoviz_success(
        setter(visual, _image_sampling_value(dvz, interpolation)),
        "Datoviz image sampling configuration failed",
    )


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


def _create_panel(
    dvz: Any, figure: Any, bounds: tuple[float, float, float, float] | None
) -> Any:
    if bounds is None:
        return dvz.dvz_panel_full(figure)
    panel_factory = getattr(dvz, "dvz_panel", None)
    desc_type = getattr(dvz, "DvzPanelDesc", None)
    if panel_factory is None or desc_type is None:
        return dvz.dvz_panel_full(figure)

    x, y, width, height = bounds
    desc = desc_type()
    desc.x = float(x)
    desc.y = float(y)
    desc.width = float(width)
    desc.height = float(height)
    panel = panel_factory(figure, desc)
    if _is_null_handle(panel):
        raise DatovizV04Unavailable("Datoviz custom panel creation failed")
    return panel


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
    if _datoviz_call_succeeded(result):
        return
    for alias in _VISUAL_ATTRIBUTE_ALIASES.get(attr_name, ()):
        result = dvz.dvz_visual_set_data(visual, alias, data)
        if _datoviz_call_succeeded(result):
            return
    raise DatovizV04Unsupported(f"Datoviz visual attribute {attr_name!r} upload failed")


def _set_visual_index_data(
    dvz: Any, visual: Any, indices: npt.NDArray[np.uint32]
) -> None:
    _require_datoviz_success(
        dvz.dvz_visual_set_index_data(visual, indices, int(indices.shape[0])),
        "Datoviz visual index upload failed",
    )


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
    _require_datoviz_success(
        style_setter(visual, style),
        "Datoviz point filled/no-stroke style configuration failed",
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
    _require_datoviz_success(
        setter(visual, _alpha_mode_value(dvz, "DVZ_ALPHA_BLENDED", DVZ_ALPHA_BLENDED)),
        "Datoviz alpha blending configuration failed",
    )


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
    _require_datoviz_success(
        dvz.dvz_marker_set_style(visual, style),
        "Datoviz marker style configuration failed",
    )


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
    view_setter = getattr(dvz, "dvz_panel_set_view2d", None)
    if view_setter is None:
        return
    if hasattr(dvz, "dvz_panel_set_domain"):
        _set_datoviz_panel_domains(dvz, panel, (-1.0, 1.0), (-1.0, 1.0))
    try:
        view = _datoviz_panel_view2d_desc(dvz)
    except DatovizV04Unavailable:
        return
    if hasattr(view, "aspect"):
        view.aspect = int(getattr(dvz, "DVZ_PANEL_VIEW2D_ASPECT_EQUAL", 1))
    if hasattr(view, "padding"):
        view.padding = 0.0
    if _datoviz_view2d_descriptor_has_data_domains(view):
        _set_datoviz_data_domain(view, "data_x", (-1.0, 1.0))
        _set_datoviz_data_domain(view, "data_y", (-1.0, 1.0))
    _require_datoviz_success(
        view_setter(panel, view),
        "Datoviz NDC equal-aspect panel setup failed",
    )


def _datoviz_panel_view2d_desc(dvz: Any) -> Any:
    """Create a View2D descriptor across Datoviz pre-RC factory renames."""
    factory = getattr(dvz, "dvz_panel_view2d_desc", None)
    if factory is None:
        factory = getattr(dvz, "dvz_panel_view2d", None)
    if factory is None:
        raise DatovizV04Unavailable(
            "Datoviz View2D descriptor factory is unavailable: missing "
            "dvz_panel_view2d_desc/dvz_panel_view2d"
        )
    return factory()


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
        return int(dvz.dvz_panel_query_px(panel, x, y, ctypes.byref(request)))
    except TypeError:
        return int(dvz.dvz_panel_query_px(panel, x, y, request))


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
    if SCALAR_COLOR_QUERY_PAYLOAD_KIND not in request.requested_extension_payload_kinds:
        unsupported_standard_payloads = tuple(
            payload
            for payload in request.requested_payload
            if payload != QueryPayload.IDENTITY
        )
        if unsupported_standard_payloads:
            return (
                "Datoviz v0.4 live data query currently supports identity payloads "
                f"only; unsupported requested payloads: {tuple(p.value for p in unsupported_standard_payloads)}"
            )
    unsupported_extension_payloads = tuple(
        kind
        for kind in request.requested_extension_payload_kinds
        if kind != SCALAR_COLOR_QUERY_PAYLOAD_KIND
    )
    if TRANSFORM_QUERY_PAYLOAD_KIND in unsupported_extension_payloads:
        return (
            "GSP_QUERY_INVERSE_UNSUPPORTED: Datoviz v0.4 query slice does not "
            "support gsp.transform-query@0.1 inverse payloads"
        )
    if unsupported_extension_payloads:
        return (
            "Datoviz v0.4 query slice does not support requested extension query "
            f"payloads: {unsupported_extension_payloads}"
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
