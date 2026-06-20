"""Datoviz v0.4 protocol adapter slice.

This module targets the C-shaped top-level Datoviz facade exposed by the local
v0.4 checkout, for example ``dvz_scene`` and ``dvz_visual_set_data``. It does
not use the older ``datoviz.App`` or ``datoviz.visuals`` wrapper APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import pi
from types import ModuleType
from typing import Any

import numpy as np
import numpy.typing as npt

from gsp.protocol import CapabilitySnapshot, ImageOrigin, ImageVisual, PointVisual, TransportKind
from gsp.protocol.visuals import CoordinateSpace, ImageInterpolation


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


class DatovizV04Unavailable(RuntimeError):
    """Raised when the imported Datoviz facade is not the expected v0.4 shape."""


class DatovizV04Unsupported(ValueError):
    """Raised when a GSP v0.1 visual asks for semantics this slice does not support."""


def is_datoviz_v04_facade(module: ModuleType | Any) -> bool:
    """Return whether a module-like object exposes the required v0.4 facade."""
    return all(hasattr(module, name) for name in _REQUIRED_DVZ_V04_FUNCTIONS)


def import_datoviz_v04() -> ModuleType:
    """Import Datoviz and validate the C-shaped v0.4 facade."""
    try:
        import datoviz as dvz
    except ModuleNotFoundError as exc:
        raise DatovizV04Unavailable("Datoviz is not importable") from exc

    if not is_datoviz_v04_facade(dvz):
        missing = [name for name in _REQUIRED_DVZ_V04_FUNCTIONS if not hasattr(dvz, name)]
        raise DatovizV04Unavailable(f"Datoviz facade is missing v0.4 functions: {missing}")
    return dvz


def capability_snapshot() -> CapabilitySnapshot:
    """Return the GSP capability surface for the current bounded adapter slice."""
    return CapabilitySnapshot(
        server_name="datoviz-v0.4-protocol-slice",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        buffer_dtypes=("float32", "uint8", "rgba8"),
        texture_formats=("rgba8",),
        visual_families=("point", "image"),
        query_modes=(),
        output_formats=(),
        deterministic=False,
        metadata={
            "datoviz_api": "v0.4 dvz_* facade",
            "image_path": "dvz_visual_set_texture RGBA8 convenience path",
            "query_support": "deferred until DvzQueryResult is decodable from Python",
        },
    )


@dataclass
class DatovizV04ProtocolRenderer:
    """Minimal point/image renderer using Datoviz v0.4 top-level functions."""

    dvz: ModuleType | Any | None = None
    width: int = 800
    height: int = 600
    scene: Any = field(init=False)
    figure: Any = field(init=False)
    panel: Any = field(init=False)
    visuals: dict[str, Any] = field(default_factory=dict, init=False)
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
        """Return the static capability snapshot for this first adapter slice."""
        return capability_snapshot()

    def close(self) -> None:
        """Destroy the scene when the facade exposes a destroy helper."""
        if self._closed:
            return
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
        self.dvz.dvz_visual_set_texture(dvz_visual, pixels, width, height)
        self.dvz.dvz_panel_add_visual(self.panel, dvz_visual, None)
        self.visuals[visual.id] = dvz_visual
        return dvz_visual


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
