"""Datoviz v0.4 protocol adapter slice.

This module targets the C-shaped top-level Datoviz facade exposed by the local
v0.4 checkout, for example ``dvz_scene`` and ``dvz_visual_set_data``. It does
not use the older ``datoviz.App`` or ``datoviz.visuals`` wrapper APIs.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass, field
from dataclasses import replace
import os
from pathlib import Path
import tempfile
from types import ModuleType
from typing import Any, cast
from zlib import crc32

import numpy as np
import numpy.typing as npt

from gsp.protocol import (
    CapabilitySnapshot,
    ImageOrigin,
    ImageVisual,
    MarkerShape,
    MarkerVisual,
    PointVisual,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryRequest,
    QueryResult,
    QueryScope,
    QueryStatus,
    View2D,
)
from gsp.protocol.visuals import CoordinateSpace, ImageInterpolation
from gsp_datoviz.capabilities import (
    datoviz_v04_axis_provider_capability,
    datoviz_v04_capability_snapshot,
    datoviz_v04_capture_diagnostics,
    datoviz_v04_capture_ready,
)
from gsp_datoviz.query import decode_dvz_query_result, datoviz_v04_query_binding_diagnostics, datoviz_v04_query_binding_ready


_REQUIRED_DVZ_V04_FUNCTIONS = (
    "dvz_scene",
    "dvz_figure",
    "dvz_panel_full",
    "dvz_panel_add_visual",
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
DVZ_IMAGE_SAMPLING_LINEAR = 0
DVZ_IMAGE_SAMPLING_NEAREST = 1
DEFAULT_BACKGROUND_RGBA8 = (255, 255, 255, 255)

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
    return tuple(f"missing {name}" for name in _REQUIRED_DVZ_SAMPLED_FIELD_FUNCTIONS if not hasattr(module, name))


def import_datoviz_v04() -> ModuleType:
    """Import Datoviz and validate the C-shaped v0.4 facade."""
    try:
        import datoviz as dvz
    except ModuleNotFoundError as exc:
        raise DatovizV04Unavailable("Datoviz is not importable") from exc

    if not is_datoviz_v04_facade(dvz):
        missing = [name for name in _REQUIRED_DVZ_V04_FUNCTIONS if not hasattr(dvz, name)]
        raise DatovizV04Unavailable(f"Datoviz facade is missing v0.4 functions: {missing}")
    return cast(ModuleType, dvz)


def capability_snapshot() -> CapabilitySnapshot:
    """Return the GSP capability surface for the current bounded adapter slice."""
    return datoviz_v04_capability_snapshot()


@dataclass
class DatovizV04ProtocolRenderer:
    """Minimal point/image renderer using Datoviz v0.4 top-level functions."""

    dvz: Any = None
    width: int = 800
    height: int = 600
    background_rgba8: tuple[int, int, int, int] = DEFAULT_BACKGROUND_RGBA8
    scene: Any = field(init=False)
    figure: Any = field(init=False)
    panel: Any = field(init=False)
    app: Any | None = field(default=None, init=False)
    offscreen_view: Any | None = field(default=None, init=False)
    live_view: Any | None = field(default=None, init=False)
    visuals: dict[str, Any] = field(default_factory=dict, init=False)
    sampled_fields: dict[str, Any] = field(default_factory=dict, init=False)
    _closed: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.dvz is None:
            self.dvz = import_datoviz_v04()
        elif not is_datoviz_v04_facade(self.dvz):
            missing = [name for name in _REQUIRED_DVZ_V04_FUNCTIONS if not hasattr(self.dvz, name)]
            raise DatovizV04Unavailable(f"Datoviz facade is missing v0.4 functions: {missing}")

        self.scene = self.dvz.dvz_scene()
        self.figure = self.dvz.dvz_figure(self.scene, self.width, self.height, 0)
        self.panel = self.dvz.dvz_panel_full(self.figure)
        _set_panel_background_color(self.dvz, self.panel, self.background_rgba8)
        _configure_ndc_panel_view2d(self.dvz, self.panel)

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
        if visual.coordinate_space != CoordinateSpace.NDC:
            raise DatovizV04Unsupported("Datoviz v0.4 slice currently supports NDC point positions only")

        positions = _positions_3d(visual.positions)
        colors = _rgba8(visual.colors)
        diameters = _diameters_from_pixel_diameters(visual.sizes, positions.shape[0])

        dvz_visual = self.dvz.dvz_point(self.scene, 0)
        _set_filled_point_style(self.dvz, dvz_visual)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", colors)
        _set_visual_data(self.dvz, dvz_visual, "diameter_px", diameters)
        self.dvz.dvz_panel_add_visual(self.panel, dvz_visual, _visual_attach_desc(self.dvz, coord_space="data", z_layer=0))
        self.visuals[visual.id] = dvz_visual
        return dvz_visual

    def add_marker_visual(self, visual: MarkerVisual) -> Any:
        """Create and attach a Datoviz marker visual."""
        if visual.coordinate_space != CoordinateSpace.NDC:
            raise DatovizV04Unsupported("Datoviz v0.4 slice currently supports NDC marker positions only")
        marker_diagnostics = _datoviz_marker_diagnostics(self.dvz)
        if marker_diagnostics:
            raise DatovizV04Unsupported(f"Datoviz v0.4 marker facade is unavailable: {', '.join(marker_diagnostics)}")

        positions = _positions_3d(visual.positions)
        fill_colors = _rgba8(visual.fill_colors)
        diameters = _diameters_from_pixel_diameters(visual.sizes, positions.shape[0])
        angles = visual.angle_values()
        shapes = _marker_shapes(self.dvz, visual.shape_values())

        dvz_visual = self.dvz.dvz_marker(self.scene, 0)
        if dvz_visual is None:
            raise DatovizV04Unsupported("Datoviz marker visual allocation failed")
        _set_marker_style(self.dvz, dvz_visual, visual.stroke_color, visual.stroke_width)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "color", fill_colors)
        _set_visual_data(self.dvz, dvz_visual, "diameter_px", diameters)
        _set_visual_data(self.dvz, dvz_visual, "angle", angles)
        _set_visual_data(self.dvz, dvz_visual, "shape", shapes)
        self.dvz.dvz_panel_add_visual(self.panel, dvz_visual, _visual_attach_desc(self.dvz, coord_space="data", z_layer=0))
        self.visuals[visual.id] = dvz_visual
        return dvz_visual

    def add_image_visual(self, visual: ImageVisual) -> Any:
        """Create and attach a Datoviz image visual for RGBA/RGB uint8 images."""
        if visual.coordinate_space != CoordinateSpace.NDC:
            raise DatovizV04Unsupported("Datoviz v0.4 slice currently supports NDC image extents only")
        pixels = _rgba8_image(visual.image)
        positions = _image_positions(visual.extent)
        texcoords = _image_texcoords(visual.origin)
        height, width = pixels.shape[:2]

        dvz_visual = self.dvz.dvz_image(self.scene, 0)
        _set_image_sampling(self.dvz, dvz_visual, visual.interpolation)
        _set_query_capabilities(self.dvz, dvz_visual, DVZ_QUERY_CAPABILITY_ITEM | DVZ_QUERY_CAPABILITY_PIXEL)
        _set_visual_data(self.dvz, dvz_visual, "position", positions)
        _set_visual_data(self.dvz, dvz_visual, "texcoords", texcoords)
        if datoviz_v04_sampled_field_ready(self.dvz):
            sampled_field = self._create_rgba8_sampled_field(pixels, width, height)
            if not _set_visual_field(self.dvz, dvz_visual, "field", sampled_field):
                raise DatovizV04Unsupported("Datoviz sampled-field image binding failed")
            self.sampled_fields[visual.id] = sampled_field
        else:
            self.dvz.dvz_visual_set_texture(dvz_visual, pixels, width, height)
        self.dvz.dvz_panel_add_visual(self.panel, dvz_visual, _visual_attach_desc(self.dvz, coord_space="data", z_layer=0))
        self.visuals[visual.id] = dvz_visual
        return dvz_visual

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
            raise DatovizV04Unavailable("Datoviz interactive app run is unavailable: missing dvz_app_run")
        app_run(self.app, frame_count)

    def _create_rgba8_sampled_field(self, pixels: npt.NDArray[np.uint8], width: int, height: int) -> Any:
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
            raise DatovizV04Unavailable(f"Datoviz offscreen PNG capture is unavailable: {diagnostics}")

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
        self.offscreen_view = self.dvz.dvz_view_offscreen(self.app, self.figure, self.width, self.height)
        if self.offscreen_view is None:
            raise DatovizV04Unavailable("Datoviz offscreen view creation failed")
        return self.offscreen_view

    def _ensure_live_view(self) -> Any:
        """Create the lazy interactive app/view pair used by show()."""
        if self.live_view is not None:
            return self.live_view

        self._ensure_app("interactive")
        view = getattr(self.dvz, "dvz_view", None)
        if view is None:
            raise DatovizV04Unavailable("Datoviz interactive view is unavailable: missing dvz_view")
        self.live_view = view(self.app, self.figure, None)
        if self.live_view is None:
            raise DatovizV04Unavailable("Datoviz interactive view creation failed")
        return self.live_view

    def _ensure_app(self, purpose: str) -> Any:
        """Create the lazy Datoviz app shared by live and offscreen views."""
        if self.app is not None:
            return self.app
        app = getattr(self.dvz, "dvz_app", None)
        if app is None:
            raise DatovizV04Unavailable(f"Datoviz {purpose} app creation is unavailable: missing dvz_app")
        self.app = app(self.scene)
        if self.app is None:
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
            unsupported = _unsupported_query_result(request, f"Datoviz query binding is unavailable: {diagnostics}")
            if unsupported is not None:
                return unsupported

        dvz_request = self.dvz.dvz_query_request()
        dvz_request.request_id = _datoviz_request_id(request.id)
        dvz_request.target = getattr(self.dvz, "DVZ_SCENE_TARGET_ITEM", DVZ_SCENE_TARGET_ITEM)
        dvz_request.hit_policy = getattr(self.dvz, "DVZ_QUERY_HIT_FRONTMOST", DVZ_QUERY_HIT_FRONTMOST)
        dvz_request.profile = getattr(self.dvz, "DVZ_QUERY_PROFILE_UNSUPPORTED", DVZ_QUERY_PROFILE_UNSUPPORTED)

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

        return replace(decode_dvz_query_result(raw_result), request_id=request.id)

    def configure_view2d_axes(
        self,
        view: View2D,
        *,
        x_label: str | None = None,
        y_label: str | None = None,
        grid: bool = False,
        backend_auto_ticks: bool = True,
    ) -> None:
        """Configure Datoviz v0.4-dev native panel domains and panel-owned axes.

        This is a capability-gated proof. It uses only the local v0.4-dev C ABI names
        verified in ``include/datoviz/scene.h`` and exposed by the supplied Python facade.
        """
        provider = datoviz_v04_axis_provider_capability(self.dvz)
        if provider.provider_status == "unsupported":
            diagnostic = provider.diagnostics[0] if provider.diagnostics else "Datoviz native axis provider is unavailable"
            raise DatovizV04Unavailable(diagnostic)
        if not backend_auto_ticks:
            raise DatovizV04Unsupported("Datoviz native axis provider cannot realize explicit GSP ticks in this slice")

        dim_x = getattr(self.dvz, "DVZ_DIM_X", 0)
        dim_y = getattr(self.dvz, "DVZ_DIM_Y", 1)
        self.dvz.dvz_panel_set_domain(self.panel, dim_x, view.x_range[0], view.x_range[1])
        self.dvz.dvz_panel_set_domain(self.panel, dim_y, view.y_range[0], view.y_range[1])

        panel_view = self.dvz.dvz_panel_view2d()
        self.dvz.dvz_panel_set_view2d(self.panel, panel_view)

        x_axis = self.dvz.dvz_panel_axis(self.panel, dim_x)
        y_axis = self.dvz.dvz_panel_axis(self.panel, dim_y)

        tick_policy = self.dvz.dvz_axis_tick_policy()
        self.dvz.dvz_axis_set_tick_policy(x_axis, tick_policy)
        self.dvz.dvz_axis_set_tick_policy(y_axis, tick_policy)

        if hasattr(self.dvz, "dvz_axis_set_grid"):
            self.dvz.dvz_axis_set_grid(x_axis, grid)
            self.dvz.dvz_axis_set_grid(y_axis, grid)

        if x_label is not None:
            self.dvz.dvz_axis_set_label(x_axis, x_label)
        if y_label is not None:
            self.dvz.dvz_axis_set_label(y_axis, y_label)


def _positions_3d(positions: npt.NDArray[np.float32] | npt.NDArray[np.float64]) -> npt.NDArray[np.float32]:
    array = np.asarray(positions, dtype=np.float32)
    if array.shape[1] == 3:
        return np.ascontiguousarray(array)
    zeros = np.zeros((array.shape[0], 1), dtype=np.float32)
    return np.ascontiguousarray(np.column_stack([array, zeros]))


def _rgba8(colors: npt.NDArray[Any]) -> npt.NDArray[np.uint8]:
    if colors.dtype == np.dtype(np.uint8):
        return np.ascontiguousarray(colors)
    return np.ascontiguousarray(np.rint(np.asarray(colors) * 255.0).clip(0, 255).astype(np.uint8))


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


def _coord_space_value(dvz: Any, name: str, fallback: int) -> int:
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzVisualCoordSpace", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _rgba8_image(image: npt.NDArray[Any]) -> npt.NDArray[np.uint8]:
    if image.dtype != np.dtype(np.uint8):
        raise DatovizV04Unsupported("Datoviz v0.4 slice only supports uint8 RGB/RGBA images")
    if image.ndim != 3 or image.shape[2] not in (3, 4):
        raise DatovizV04Unsupported("Datoviz v0.4 slice only supports uint8 RGB/RGBA images")
    if image.shape[2] == 4:
        return np.ascontiguousarray(image)
    alpha = np.full((*image.shape[:2], 1), 255, dtype=np.uint8)
    return np.ascontiguousarray(np.concatenate([image, alpha], axis=2))


def _set_data_view_payload(view: Any, pixels: npt.NDArray[np.uint8]) -> None:
    try:
        view.data = pixels
    except TypeError:
        view.data = pixels.ctypes.data


def _set_visual_field(dvz: Any, visual: Any, slot_name: str, sampled_field: Any) -> bool:
    try:
        return bool(dvz.dvz_visual_set_field(visual, slot_name, sampled_field))
    except (ctypes.ArgumentError, TypeError):
        return bool(dvz.dvz_visual_set_field(visual, slot_name.encode("utf-8"), sampled_field))


def _image_sampling_value(dvz: Any, interpolation: ImageInterpolation) -> int:
    if interpolation == ImageInterpolation.NEAREST:
        name = "DVZ_IMAGE_SAMPLING_NEAREST"
        fallback = DVZ_IMAGE_SAMPLING_NEAREST
    elif interpolation == ImageInterpolation.LINEAR:
        name = "DVZ_IMAGE_SAMPLING_LINEAR"
        fallback = DVZ_IMAGE_SAMPLING_LINEAR
    else:
        raise DatovizV04Unsupported(f"unsupported Datoviz image interpolation: {interpolation}")

    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzImageSampling", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return fallback


def _set_image_sampling(dvz: Any, visual: Any, interpolation: ImageInterpolation) -> None:
    setter = getattr(dvz, "dvz_image_set_sampling", None)
    if setter is None:
        raise DatovizV04Unsupported(
            "Datoviz v0.4 image facade is missing dvz_image_set_sampling; "
            "nearest image rendering would silently use linear sampling"
        )
    result = setter(visual, _image_sampling_value(dvz, interpolation))
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz image sampling configuration failed")


def _set_query_capabilities(dvz: Any, visual: Any, capabilities: int) -> None:
    setter = getattr(dvz, "dvz_visual_set_query_capabilities", None)
    if setter is None:
        return
    setter(visual, capabilities)


def _set_panel_background_color(dvz: Any, panel: Any, rgba: tuple[int, int, int, int]) -> None:
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


def _set_visual_data(dvz: Any, visual: Any, attr_name: str, data: npt.NDArray[Any]) -> None:
    result = dvz.dvz_visual_set_data(visual, attr_name, data)
    if result != 0:
        raise DatovizV04Unsupported(f"Datoviz visual attribute {attr_name!r} upload failed")


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
        raise DatovizV04Unsupported("Datoviz point filled/no-stroke style configuration failed")


def _datoviz_marker_diagnostics(dvz: Any) -> tuple[str, ...]:
    return tuple(f"missing {name}" for name in _REQUIRED_DVZ_MARKER_FUNCTIONS if not hasattr(dvz, name))


def _set_marker_style(dvz: Any, visual: Any, stroke_color: npt.NDArray[Any], stroke_width: float) -> None:
    style = dvz.dvz_marker_style()
    _assign_rgba_field(style, "edge_color", _rgba8_scalar(stroke_color))
    if hasattr(style, "stroke_width_px"):
        style.stroke_width_px = float(stroke_width)
    elif hasattr(style, "stroke_width"):
        style.stroke_width = float(stroke_width)
    if hasattr(style, "aspect"):
        if stroke_width > 0.0 and _rgba8_scalar(stroke_color)[3] > 0:
            style.aspect = int(getattr(dvz, "DVZ_SHAPE_ASPECT_OUTLINE", DVZ_SHAPE_ASPECT_OUTLINE))
        else:
            style.aspect = int(getattr(dvz, "DVZ_SHAPE_ASPECT_FILLED", DVZ_SHAPE_ASPECT_FILLED))
    result = dvz.dvz_marker_set_style(visual, style)
    if result not in (0, None, True):
        raise DatovizV04Unsupported("Datoviz marker style configuration failed")


def _rgba8_scalar(color: npt.NDArray[Any]) -> npt.NDArray[np.uint8]:
    rgba = _rgba8(np.asarray(color).reshape(1, 4))[0]
    return np.ascontiguousarray(rgba)


def _assign_rgba_field(target: Any, field_name: str, rgba: npt.NDArray[np.uint8]) -> None:
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
    return np.ascontiguousarray(np.array([_marker_shape_value(dvz, shape) for shape in shapes], dtype=np.uint32))


def _marker_shape_value(dvz: Any, shape: MarkerShape) -> int:
    name = _MARKER_SHAPE_NAMES[shape]
    value = getattr(dvz, name, None)
    if value is not None:
        return int(value)
    enum_type = getattr(dvz, "DvzMarkerShape", None)
    if enum_type is not None:
        return int(getattr(enum_type, name))
    return _MARKER_SHAPE_FALLBACKS[shape]


def _configure_ndc_panel_view2d(dvz: Any, panel: Any) -> None:
    """Configure the panel so NDC data keeps equal X/Y screen scale when possible."""
    view_factory = getattr(dvz, "dvz_panel_view2d", None)
    view_setter = getattr(dvz, "dvz_panel_set_view2d", None)
    if view_factory is None or view_setter is None:
        return
    view = view_factory()
    if hasattr(view, "aspect"):
        view.aspect = int(getattr(dvz, "DVZ_PANEL_VIEW2D_ASPECT_EQUAL", 1))
    if hasattr(view, "padding"):
        view.padding = 0.0
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
    return hasattr(dvz, "dvz_view_render_once") or hasattr(dvz, "dvz_app_render_once") or hasattr(dvz, "dvz_app_run")


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
        return f"Datoviz v0.4 query slice supports data scope only, got {request.scope.value!r}"
    if request.coordinate_space != QueryCoordinateSpace.PANEL:
        return f"Datoviz v0.4 query slice supports panel coordinates only, got {request.coordinate_space.value!r}"
    if request.hit_policy != QueryHitPolicy.FRONTMOST:
        return f"Datoviz v0.4 query slice supports frontmost hit policy only, got {request.hit_policy.value!r}"
    if request.requested_extension_payload_kinds:
        return "Datoviz v0.4 query slice does not support extension query payloads"
    return None


def _unsupported_query_result(request: QueryRequest, diagnostic: str | None) -> QueryResult | None:
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


def _image_positions(extent: tuple[float, float, float, float]) -> npt.NDArray[np.float32]:
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
