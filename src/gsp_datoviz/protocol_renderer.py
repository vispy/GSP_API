"""Datoviz v0.4 protocol adapter slice.

This module targets the C-shaped top-level Datoviz facade exposed by the local
v0.4 checkout, for example ``dvz_scene`` and ``dvz_visual_set_data``. It does
not use the older ``datoviz.App`` or ``datoviz.visuals`` wrapper APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import pi
from pathlib import Path
import tempfile
from types import ModuleType
from typing import Any, cast

import numpy as np
import numpy.typing as npt

from gsp.protocol import CapabilitySnapshot, ImageOrigin, ImageVisual, PointVisual, View2D
from gsp.protocol.visuals import CoordinateSpace, ImageInterpolation
from gsp_datoviz.capabilities import (
    datoviz_v04_axis_provider_capability,
    datoviz_v04_capability_snapshot,
    datoviz_v04_capture_diagnostics,
    datoviz_v04_capture_ready,
)


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

DVZ_FIELD_DIM_2D = 0
DVZ_FIELD_FORMAT_RGBA8_UNORM = 22
DVZ_FIELD_SEMANTIC_COLOR = 4
DVZ_COLOR_ROLE_SRGB_COLOR = 1


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
    scene: Any = field(init=False)
    figure: Any = field(init=False)
    panel: Any = field(init=False)
    app: Any | None = field(default=None, init=False)
    offscreen_view: Any | None = field(default=None, init=False)
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
        diameters = _diameters_from_marker_area(visual.sizes, positions.shape[0])

        dvz_visual = self.dvz.dvz_point(self.scene, 0)
        self.dvz.dvz_visual_set_data(dvz_visual, "position", positions)
        self.dvz.dvz_visual_set_data(dvz_visual, "color", colors)
        self.dvz.dvz_visual_set_data(dvz_visual, "diameter", diameters)
        self.dvz.dvz_panel_add_visual(self.panel, dvz_visual, None)
        self.visuals[visual.id] = dvz_visual
        return dvz_visual

    def add_image_visual(self, visual: ImageVisual) -> Any:
        """Create and attach a Datoviz image visual for RGBA/RGB uint8 images."""
        if visual.coordinate_space != CoordinateSpace.NDC:
            raise DatovizV04Unsupported("Datoviz v0.4 slice currently supports NDC image extents only")
        if visual.interpolation != ImageInterpolation.NEAREST:
            raise DatovizV04Unsupported("Datoviz v0.4 texture convenience path has no locked interpolation mapping")

        pixels = _rgba8_image(visual.image)
        positions = _image_positions(visual.extent)
        texcoords = _image_texcoords(visual.origin)
        height, width = pixels.shape[:2]

        dvz_visual = self.dvz.dvz_image(self.scene, 0)
        self.dvz.dvz_visual_set_data(dvz_visual, "position", positions)
        self.dvz.dvz_visual_set_data(dvz_visual, "texcoords", texcoords)
        if datoviz_v04_sampled_field_ready(self.dvz):
            sampled_field = self._create_rgba8_sampled_field(pixels, width, height)
            if not self.dvz.dvz_visual_set_field(dvz_visual, "field", sampled_field):
                raise DatovizV04Unsupported("Datoviz sampled-field image binding failed")
            self.sampled_fields[visual.id] = sampled_field
        else:
            self.dvz.dvz_visual_set_texture(dvz_visual, pixels, width, height)
        self.dvz.dvz_panel_add_visual(self.panel, dvz_visual, None)
        self.visuals[visual.id] = dvz_visual
        return dvz_visual

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
            result = self.dvz.dvz_view_capture_png(view, str(path))
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

        self.app = self.dvz.dvz_app(self.scene)
        if self.app is None:
            raise DatovizV04Unavailable("Datoviz offscreen app creation failed")
        self.offscreen_view = self.dvz.dvz_view_offscreen(self.app, self.figure, self.width, self.height)
        if self.offscreen_view is None:
            raise DatovizV04Unavailable("Datoviz offscreen view creation failed")
        return self.offscreen_view

    def _render_offscreen_frame(self) -> None:
        render_once = getattr(self.dvz, "dvz_app_render_once", None)
        if render_once is not None:
            result = render_once(self.app)
        else:
            result = self.dvz.dvz_app_run(self.app, 1)
        if result not in (0, None):
            raise DatovizV04Unsupported("Datoviz offscreen frame render failed")

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


def _diameters_from_marker_area(
    sizes: npt.NDArray[np.float32] | npt.NDArray[np.float64] | float,
    count: int,
) -> npt.NDArray[np.float32]:
    if isinstance(sizes, np.ndarray):
        area = np.asarray(sizes, dtype=np.float32)
    else:
        area = np.full((count,), float(sizes), dtype=np.float32)
    return np.ascontiguousarray(2.0 * np.sqrt(area / np.float32(pi), dtype=np.float32))


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
