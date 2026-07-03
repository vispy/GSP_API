"""Datoviz v0.4 API audit probe for visual QA."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
import importlib.util
from pathlib import Path
import subprocess
import sys
import traceback
from types import ModuleType
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


REQUIRED_CAPABILITIES: Mapping[str, tuple[str, str]] = {
    "scene.create.dvz_scene": ("facade", "dvz_scene"),
    "scene.figure.dvz_figure": ("facade", "dvz_figure"),
    "scene.panel.dvz_panel_full": ("facade", "dvz_panel_full"),
    "panel.add_visual.dvz_panel_add_visual": ("facade", "dvz_panel_add_visual"),
    "visual.data.dvz_visual_set_data": ("facade", "dvz_visual_set_data"),
    "visual.data_many.dvz_visual_set_data_many": ("facade", "dvz_visual_set_data_many"),
    "visual.data_range.dvz_visual_set_data_range": (
        "facade",
        "dvz_visual_set_data_range",
    ),
    "visual.point.constructor.dvz_point": ("facade", "dvz_point"),
    "visual.marker.constructor.dvz_marker": ("facade", "dvz_marker"),
    "visual.segment.constructor.dvz_segment": ("facade", "dvz_segment"),
    "visual.path.constructor.dvz_path": ("facade", "dvz_path"),
    "visual.image.constructor.dvz_image": ("facade", "dvz_image"),
    "visual.path.style.dvz_path_set_subpaths": ("facade", "dvz_path_set_subpaths"),
    "visual.path.style.dvz_path_set_caps": ("facade", "dvz_path_set_caps"),
    "visual.path.style.dvz_path_set_join": ("facade", "dvz_path_set_join"),
    "visual.image.field.dvz_sampled_field": ("facade", "dvz_sampled_field"),
    "visual.image.field.dvz_sampled_field_set_data": (
        "facade",
        "dvz_sampled_field_set_data",
    ),
    "visual.image.field.dvz_visual_set_field": ("facade", "dvz_visual_set_field"),
    "capture.top_level.datoviz_capture": ("facade", "capture"),
    "attach.desc.DvzVisualAttachDesc": ("facade", "DvzVisualAttachDesc"),
    "attach.coord_space.DVZ_VISUAL_COORD_VIEW": ("raw", "DVZ_VISUAL_COORD_VIEW"),
    "attach.coord_space.DVZ_VISUAL_COORD_DATA": ("raw", "DVZ_VISUAL_COORD_DATA"),
    "attach.coord_space.DVZ_VISUAL_COORD_PANEL": ("raw", "DVZ_VISUAL_COORD_PANEL"),
}

RAW_MIRROR_SYMBOLS: tuple[str, ...] = tuple(
    sorted(
        {
            symbol
            for _, symbol in REQUIRED_CAPABILITIES.values()
            if symbol.startswith("dvz_")
            or symbol.startswith("Dvz")
            or symbol.startswith("DVZ_")
        }
    )
)

ENUM_AND_STYLE_SYMBOLS: tuple[str, ...] = (
    "DvzDimMaskFlag",
    "DvzVisualAttachDesc",
    "DvzVisualCoordSpace",
    "DVZ_VISUAL_COORD_DATA",
    "DVZ_VISUAL_COORD_PANEL",
    "DVZ_VISUAL_COORD_VIEW",
    "DVZ_PATH_JOIN_BEVEL",
    "DVZ_PATH_JOIN_MITER",
    "DVZ_PATH_JOIN_ROUND",
    "DVZ_SEGMENT_CAP_BUTT",
    "DVZ_SEGMENT_CAP_ROUND",
    "DVZ_SEGMENT_CAP_SQUARE",
    "DVZ_MARKER_SHAPE_CIRCLE",
    "DVZ_MARKER_SHAPE_DISC",
    "DVZ_MARKER_SHAPE_SQUARE",
    "DVZ_BLEND_ALPHA",
    "dvz_marker_set_style",
    "dvz_marker_style",
    "dvz_point_set_style",
    "dvz_point_style_desc",
    "dvz_segment_set_caps",
)

BANNED_V03_SYMBOLS: tuple[str, ...] = (
    "dvz_path_alloc",
    "dvz_point_alloc",
    "dvz_marker_alloc",
    "dvz_segment_alloc",
    "dvz_image_alloc",
    "dvz_point_position",
    "dvz_marker_color",
    "dvz_segment_linewidth",
)


TEXT_SYMBOLS: tuple[str, ...] = (
    "DvzText",
    "DvzTextAtlas",
    "DvzTextAtlasGlyph",
    "DvzTextAtlasInfo",
    "DvzTextAtlasSpec",
    "DvzTextPlacement",
    "DvzTextPlacementMode",
    "DvzTextRenderer",
    "DvzTextStyle",
    "DVZ_SCENE_VISUAL_FAMILY_LABELS",
    "DVZ_SCENE_VISUAL_FAMILY_TEXT",
    "DVZ_TEXT_ANCHOR_CENTER",
    "DVZ_TEXT_ANCHOR_LEFT",
    "DVZ_TEXT_ANCHOR_RIGHT",
    "DVZ_TEXT_BASELINE_ALPHABETIC",
    "DVZ_TEXT_RENDERER_BITMAP",
    "DVZ_TEXT_RENDERER_SDF",
    "dvz_font",
    "dvz_font_atlas",
    "dvz_font_atlas_ensure_string",
    "dvz_font_atlas_ensure_strings",
    "dvz_font_desc",
    "dvz_glyph",
    "dvz_glyph_set_atlas",
    "dvz_labels",
    "dvz_text",
    "dvz_text_atlas_field",
    "dvz_text_atlas_glyph",
    "dvz_text_atlas_info",
    "dvz_text_atlas_spec",
    "dvz_text_destroy",
    "dvz_text_id",
    "dvz_text_placement",
    "dvz_text_set_placement",
    "dvz_text_set_style",
    "dvz_text_set_string",
    "dvz_text_style",
)

TEXT_RENDERER_CAPABILITIES: Mapping[str, tuple[str, ...]] = {
    "text.visual.constructor": ("dvz_text",),
    "text.visual.string": ("dvz_text_set_string",),
    "text.style": ("dvz_text_style", "dvz_text_set_style"),
    "text.placement": ("dvz_text_placement", "dvz_text_set_placement"),
    "text.font.create": ("dvz_font", "dvz_font_desc"),
    "text.font.atlas": (
        "dvz_text_atlas_spec",
        "dvz_font_atlas_ensure_strings",
        "dvz_font_atlas",
        "dvz_text_atlas_field",
    ),
    "text.glyph.visual": ("dvz_glyph", "dvz_glyph_set_atlas"),
}

BANNED_TEXT_SYMBOLS: tuple[str, ...] = (
    "dvz_label_desc",
    "DvzLabelDesc",
    "DVZ_WASM_VISUAL_GLYPH",
)


MESH_SYMBOLS: tuple[str, ...] = (
    "DvzGeometry",
    "DvzIndex",
    "DvzMaterial",
    "DVZ_SCENE_VISUAL_FAMILY_MESH",
    "dvz_mesh",
    "dvz_mesh_set_geometry",
    "dvz_visual_set_data",
    "dvz_visual_set_index_data",
    "dvz_visual_set_material",
    "dvz_visual_set_depth_test",
    "dvz_visual_set_texture_rgba8",
)

MESH_RENDERER_CAPABILITIES: Mapping[str, tuple[str, ...]] = {
    "mesh.visual.constructor": ("dvz_mesh",),
    "mesh.geometry.upload": ("dvz_mesh_set_geometry",),
    "mesh.attribute.upload": ("dvz_visual_set_data",),
    "mesh.index.upload": ("dvz_visual_set_index_data",),
    "mesh.material.helper": ("dvz_visual_set_material",),
    "mesh.depth_test.helper": ("dvz_visual_set_depth_test",),
    "mesh.texture.rgba8.evidence": ("dvz_visual_set_texture_rgba8",),
}


COLOR_MAPPING_SYMBOLS: tuple[str, ...] = (
    "DvzColorbar",
    "DvzColorbarDesc",
    "DvzColorbarOrientation",
    "DvzColormap",
    "DvzColormapDesc",
    "DvzColormapStop",
    "DvzFieldDataView",
    "DvzQueryResult",
    "DvzSampledField",
    "DvzSampledFieldDesc",
    "DvzScale",
    "DvzScaleDesc",
    "DVZ_BUILTIN_COLORMAP_CIVIDIS",
    "DVZ_BUILTIN_COLORMAP_GRAY",
    "DVZ_BUILTIN_COLORMAP_INFERNO",
    "DVZ_BUILTIN_COLORMAP_MAGMA",
    "DVZ_BUILTIN_COLORMAP_PLASMA",
    "DVZ_BUILTIN_COLORMAP_VIRIDIS",
    "DVZ_COLOR_ROLE_DATA",
    "DVZ_COLORBAR_ORIENTATION_HORIZONTAL",
    "DVZ_COLORBAR_ORIENTATION_VERTICAL",
    "DVZ_FIELD_DIM_2D",
    "DVZ_FIELD_FORMAT_R32_FLOAT",
    "DVZ_FIELD_SEMANTIC_SCALAR",
    "DVZ_SCALE_CONTINUOUS",
    "dvz_colorbar",
    "dvz_colorbar_desc",
    "dvz_colorbar_set_format",
    "dvz_colorbar_set_layout",
    "dvz_colorbar_set_orientation",
    "dvz_colorbar_set_title",
    "dvz_colormap",
    "dvz_colormap_builtin",
    "dvz_colormap_custom",
    "dvz_colormap_sample",
    "dvz_colormap_set_stops",
    "dvz_panel_query",
    "dvz_panel_query_now",
    "dvz_sampled_field",
    "dvz_sampled_field_desc",
    "dvz_sampled_field_set_data",
    "dvz_scene_poll_query",
    "dvz_scale",
    "dvz_scale_desc",
    "dvz_scale_set_colormap",
    "dvz_scale_set_domain",
    "dvz_scale_set_view_range",
    "dvz_visual_set_field",
    "dvz_visual_set_scale",
)

COLOR_MAPPING_CAPABILITIES: Mapping[str, tuple[str, ...]] = {
    "color.scale.continuous": (
        "dvz_scale",
        "dvz_scale_set_domain",
        "DVZ_SCALE_CONTINUOUS",
    ),
    "color.colormap.accepted_named": (
        "dvz_colormap_builtin",
        "DVZ_BUILTIN_COLORMAP_GRAY",
        "DVZ_BUILTIN_COLORMAP_VIRIDIS",
        "DVZ_BUILTIN_COLORMAP_MAGMA",
        "DVZ_BUILTIN_COLORMAP_PLASMA",
        "DVZ_BUILTIN_COLORMAP_INFERNO",
        "DVZ_BUILTIN_COLORMAP_CIVIDIS",
    ),
    "color.colormap.custom_lut": (
        "dvz_colormap_custom",
        "dvz_colormap_set_stops",
    ),
    "color.image.scalar_field": (
        "dvz_sampled_field",
        "dvz_sampled_field_set_data",
        "dvz_visual_set_field",
        "dvz_visual_set_scale",
        "DVZ_FIELD_DIM_2D",
        "DVZ_FIELD_FORMAT_R32_FLOAT",
        "DVZ_FIELD_SEMANTIC_SCALAR",
    ),
    "color.point.scalar_attribute": (
        "dvz_point",
        "dvz_visual_set_data",
        "dvz_visual_set_scale",
        "dvz_scale",
    ),
    "color.colorbar.semantic": (
        "dvz_colorbar",
        "DvzColorbarDesc",
        "DVZ_COLORBAR_ORIENTATION_VERTICAL",
        "DVZ_COLORBAR_ORIENTATION_HORIZONTAL",
    ),
    "color.query.scalar_readback": (
        "DvzQueryResult",
        "dvz_panel_query",
        "dvz_panel_query_now",
        "dvz_scene_poll_query",
    ),
}

COLOR_MAPPING_UNVERIFIED_CAPABILITY_REASONS: Mapping[str, str] = {
    "color.marker.scalar_fill": (
        "No retained-scene symbol or source contract was found for MarkerVisual scalar fill "
        "colors; S026 should keep this Datoviz path unsupported or CPU-map to RGBA until verified."
    ),
    "color.mesh.face_scalar": (
        "S026 marks MeshVisual face scalar color as capability-gated and this probe does not "
        "verify a Datoviz face-scalar readback/rendering contract."
    ),
}

ENUM_CONTAINER_SYMBOLS: tuple[str, ...] = (
    "DvzBuiltinColormap",
    "DvzColorbarOrientation",
    "DvzFieldDim",
    "DvzFieldFormat",
    "DvzFieldSemantic",
    "DvzScaleKind",
    "DvzVisualCoordSpace",
)


@dataclass(frozen=True)
class ImportProbe:
    """JSON-safe import result."""

    module: str
    imported: bool
    path: str | None
    error_type: str | None
    error_message: str | None
    traceback: str | None

    def to_json(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {
            "module": self.module,
            "imported": self.imported,
            "path": self.path,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "traceback": self.traceback,
        }


@dataclass(frozen=True)
class SymbolProbe:
    """JSON-safe symbol availability result."""

    symbol: str
    available: bool
    source: str

    def to_json(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {
            "symbol": self.symbol,
            "available": self.available,
            "source": self.source,
        }


@dataclass(frozen=True)
class CapabilityProbe:
    """JSON-safe capability result."""

    capability: str
    source: str
    symbol: str
    supported: bool
    reason: str | None = None

    def to_json(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {
            "capability": self.capability,
            "source": self.source,
            "symbol": self.symbol,
            "supported": self.supported,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class SourceSymbolHit:
    """A text hit in the sibling Datoviz source checkout."""

    path: str
    line: int

    def to_json(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {"path": self.path, "line": self.line}


@dataclass(frozen=True)
class BannedSymbolHit:
    """A banned v0.3-style symbol occurrence."""

    symbol: str
    path: str
    line: int
    allowed_context: bool

    def to_json(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {
            "symbol": self.symbol,
            "path": self.path,
            "line": self.line,
            "allowed_context": self.allowed_context,
        }


@dataclass(frozen=True)
class MinimalPointProbe:
    """Result of a non-rendering retained point scene construction attempt."""

    attempted: bool
    supported: bool
    reason: str | None
    calls_completed: tuple[str, ...]

    def to_json(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {
            "attempted": self.attempted,
            "supported": self.supported,
            "reason": self.reason,
            "calls_completed": list(self.calls_completed),
        }


@dataclass(frozen=True)
class DatovizV04ProbeReport:
    """JSON-safe Datoviz v0.4 API probe report."""

    installed_package: dict[str, object]
    sibling_source: dict[str, object]
    imports: dict[str, ImportProbe]
    generated_files: dict[str, bool | None]
    facade_symbols: dict[str, SymbolProbe]
    raw_symbols: dict[str, SymbolProbe]
    capability_matrix: dict[str, CapabilityProbe]
    enum_style_symbols: dict[str, SymbolProbe]
    text_symbols: dict[str, SymbolProbe]
    text_capability_matrix: dict[str, CapabilityProbe]
    mesh_symbols: dict[str, SymbolProbe]
    mesh_capability_matrix: dict[str, CapabilityProbe]
    color_mapping_symbols: dict[str, SymbolProbe]
    color_mapping_capability_matrix: dict[str, CapabilityProbe]
    source_symbol_matrix: dict[str, list[SourceSymbolHit]]
    minimal_point_scene: MinimalPointProbe
    capture: dict[str, object]
    banned_symbol_check: dict[str, object]

    def to_json(self) -> dict[str, object]:
        """Return a JSON-safe representation."""
        return {
            "installed_package": self.installed_package,
            "sibling_source": self.sibling_source,
            "imports": {
                name: result.to_json() for name, result in self.imports.items()
            },
            "generated_files": dict(self.generated_files),
            "facade_symbols": {
                name: result.to_json() for name, result in self.facade_symbols.items()
            },
            "raw_symbols": {
                name: result.to_json() for name, result in self.raw_symbols.items()
            },
            "capability_matrix": {
                name: result.to_json()
                for name, result in self.capability_matrix.items()
            },
            "enum_style_symbols": {
                name: result.to_json()
                for name, result in self.enum_style_symbols.items()
            },
            "text_symbols": {
                name: result.to_json() for name, result in self.text_symbols.items()
            },
            "text_capability_matrix": {
                name: result.to_json()
                for name, result in self.text_capability_matrix.items()
            },
            "mesh_symbols": {
                name: result.to_json() for name, result in self.mesh_symbols.items()
            },
            "mesh_capability_matrix": {
                name: result.to_json()
                for name, result in self.mesh_capability_matrix.items()
            },
            "color_mapping_symbols": {
                name: result.to_json()
                for name, result in self.color_mapping_symbols.items()
            },
            "color_mapping_capability_matrix": {
                name: result.to_json()
                for name, result in self.color_mapping_capability_matrix.items()
            },
            "source_symbol_matrix": {
                name: [hit.to_json() for hit in hits]
                for name, hits in self.source_symbol_matrix.items()
            },
            "minimal_point_scene": self.minimal_point_scene.to_json(),
            "capture": dict(self.capture),
            "banned_symbol_check": dict(self.banned_symbol_check),
        }


def probe_datoviz_v04(
    *,
    source_path: Path | str = Path("../datoviz"),
    banned_scan_paths: Sequence[Path | str] | None = None,
    facade_module: Any | None = None,
    raw_module: Any | None = None,
) -> DatovizV04ProbeReport:
    """Probe the installed Datoviz package and local v0.4 checkout."""
    source = Path(source_path)
    source_import_path = source if source.exists() else None
    with _temporary_sys_path(source_import_path):
        facade_import = _import_probe("datoviz", injected_module=facade_module)
        raw_import = _import_probe("datoviz.raw", injected_module=raw_module)
        facade = (
            facade_module
            if facade_module is not None
            else _imported_module_or_none("datoviz")
        )
        raw = (
            raw_module
            if raw_module is not None
            else _imported_module_or_none("datoviz.raw")
        )

    installed_path = facade_import.path
    generated_files = _generated_files(installed_path)
    facade_symbols = _probe_symbols(facade, _facade_symbol_names(), "facade")
    raw_symbols = _probe_symbols(
        raw,
        RAW_MIRROR_SYMBOLS
        + ENUM_AND_STYLE_SYMBOLS
        + TEXT_SYMBOLS
        + MESH_SYMBOLS
        + COLOR_MAPPING_SYMBOLS,
        "raw",
    )
    capability_matrix = _capability_matrix(
        facade_symbols, raw_symbols, facade_import, raw_import
    )
    enum_style_symbols = _enum_style_matrix(facade, raw)
    text_symbols = _text_symbol_matrix(facade, raw)
    text_capability_matrix = _text_capability_matrix(text_symbols)
    mesh_symbols = _mesh_symbol_matrix(facade, raw)
    mesh_capability_matrix = _mesh_capability_matrix(mesh_symbols)
    color_mapping_symbols = _color_mapping_symbol_matrix(facade, raw)
    color_mapping_capability_matrix = _color_mapping_capability_matrix(
        color_mapping_symbols, facade_symbols, raw_symbols
    )
    source_symbol_matrix = _source_symbol_matrix(
        source,
        tuple(
            sorted(
                set(_facade_symbol_names())
                | set(RAW_MIRROR_SYMBOLS)
                | set(ENUM_AND_STYLE_SYMBOLS)
                | set(TEXT_SYMBOLS)
                | set(MESH_SYMBOLS)
                | set(COLOR_MAPPING_SYMBOLS)
                | set(BANNED_TEXT_SYMBOLS)
            )
        ),
    )
    minimal_point_scene = _probe_minimal_point_scene(facade, capability_matrix)
    banned_paths = (
        tuple(Path(path) for path in banned_scan_paths)
        if banned_scan_paths is not None
        else _default_banned_scan_paths()
    )
    banned_hits = scan_banned_symbols(
        banned_paths, banned_symbols=BANNED_V03_SYMBOLS + BANNED_TEXT_SYMBOLS
    )

    return DatovizV04ProbeReport(
        installed_package={
            "path": installed_path,
            "imported": facade_import.imported,
            "version": _string_attr(facade, "__version__"),
        },
        sibling_source={
            "path": str(source),
            "exists": source.exists(),
            "revision": _git_revision(source),
        },
        imports={"datoviz": facade_import, "datoviz.raw": raw_import},
        generated_files=generated_files,
        facade_symbols=facade_symbols,
        raw_symbols=raw_symbols,
        capability_matrix=capability_matrix,
        enum_style_symbols=enum_style_symbols,
        text_symbols=text_symbols,
        text_capability_matrix=text_capability_matrix,
        mesh_symbols=mesh_symbols,
        mesh_capability_matrix=mesh_capability_matrix,
        color_mapping_symbols=color_mapping_symbols,
        color_mapping_capability_matrix=color_mapping_capability_matrix,
        source_symbol_matrix=source_symbol_matrix,
        minimal_point_scene=minimal_point_scene,
        capture={
            "top_level_capture_available": _has_symbol(facade, "capture"),
            "offscreen_symbols_available": all(
                _has_symbol(facade, name) or _has_symbol(raw, name)
                for name in ("dvz_app", "dvz_view_offscreen", "dvz_view_capture_png")
            ),
            "run_symbols_available": any(
                _has_symbol(facade, name) or _has_symbol(raw, name)
                for name in (
                    "dvz_view_render_once",
                    "dvz_app_render_once",
                    "dvz_app_run",
                )
            ),
        },
        banned_symbol_check={
            "symbols": list(BANNED_V03_SYMBOLS),
            "text_symbols": list(BANNED_TEXT_SYMBOLS),
            "paths": [str(path) for path in banned_paths],
            "hits": [hit.to_json() for hit in banned_hits],
            "unexpected_hits": [
                hit.to_json() for hit in banned_hits if not hit.allowed_context
            ],
        },
    )


def scan_banned_symbols(
    paths: Sequence[Path | str], *, banned_symbols: Sequence[str] = BANNED_V03_SYMBOLS
) -> tuple[BannedSymbolHit, ...]:
    """Scan files for banned Datoviz v0.3 visual API symbols."""
    hits: list[BannedSymbolHit] = []
    for root in paths:
        path = Path(root)
        files = _iter_scan_files(path)
        for file_path in files:
            try:
                text = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                for symbol in banned_symbols:
                    if symbol in line:
                        hits.append(
                            BannedSymbolHit(
                                symbol=symbol,
                                path=str(file_path),
                                line=line_number,
                                allowed_context=_is_allowed_banned_context(file_path),
                            )
                        )
    return tuple(hits)


def _import_probe(
    module_name: str, *, injected_module: Any | None = None
) -> ImportProbe:
    if injected_module is not None:
        return ImportProbe(
            module=module_name,
            imported=True,
            path=_module_path(injected_module),
            error_type=None,
            error_message=None,
            traceback=None,
        )
    try:
        module = import_module(module_name)
    except Exception as exc:  # noqa: BLE001 - this is an audit probe.
        return ImportProbe(
            module=module_name,
            imported=False,
            path=_spec_origin(module_name),
            error_type=type(exc).__name__,
            error_message=str(exc),
            traceback=traceback.format_exc(),
        )
    return ImportProbe(
        module=module_name,
        imported=True,
        path=_module_path(module),
        error_type=None,
        error_message=None,
        traceback=None,
    )


def _imported_module_or_none(module_name: str) -> ModuleType | None:
    try:
        module = import_module(module_name)
    except Exception:  # noqa: BLE001 - import status is already captured separately.
        return None
    return module


class _temporary_sys_path:
    def __init__(self, path: Path | None) -> None:
        self._path = str(path.resolve()) if path is not None else None
        self._inserted = False

    def __enter__(self) -> None:
        if self._path is None or self._path in sys.path:
            return
        sys.path.insert(0, self._path)
        self._inserted = True

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._inserted and self._path in sys.path:
            sys.path.remove(self._path)


def _spec_origin(module_name: str) -> str | None:
    try:
        spec = importlib.util.find_spec(module_name)
    except ModuleNotFoundError:
        return None
    if spec is None:
        return None
    return spec.origin


def _module_path(module: Any) -> str | None:
    path = getattr(module, "__file__", None)
    if isinstance(path, str):
        return path
    return None


def _generated_files(installed_path: str | None) -> dict[str, bool | None]:
    if installed_path is None:
        return {"_array_facade.py": None, "_ctypes.py": None}
    package_dir = Path(installed_path).parent
    return {
        "_array_facade.py": (package_dir / "_array_facade.py").exists(),
        "_ctypes.py": (package_dir / "_ctypes.py").exists(),
    }


def _facade_symbol_names() -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                symbol
                for source, symbol in REQUIRED_CAPABILITIES.values()
                if source == "facade"
            }
            | set(ENUM_AND_STYLE_SYMBOLS)
        )
    )


def _probe_symbols(
    module: Any | None, symbols: Iterable[str], source: str
) -> dict[str, SymbolProbe]:
    return {
        symbol: SymbolProbe(
            symbol=symbol, available=_has_symbol(module, symbol), source=source
        )
        for symbol in sorted(set(symbols))
    }


def _has_symbol(module: Any | None, symbol: str) -> bool:
    if module is None:
        return False
    try:
        getattr(module, symbol)
    except Exception:  # noqa: BLE001 - getattr on Datoviz can trigger generated binding import.
        return _has_enum_member(module, symbol)
    else:
        return True


def _has_enum_member(module: Any, symbol: str) -> bool:
    if not symbol.startswith("DVZ_"):
        return False
    for container_name in ENUM_CONTAINER_SYMBOLS:
        try:
            container = getattr(module, container_name)
        except Exception:  # noqa: BLE001 - generated bindings can raise during getattr.
            continue
        if hasattr(container, symbol):
            return True
    return False


def _capability_matrix(
    facade_symbols: Mapping[str, SymbolProbe],
    raw_symbols: Mapping[str, SymbolProbe],
    facade_import: ImportProbe,
    raw_import: ImportProbe,
) -> dict[str, CapabilityProbe]:
    matrix: dict[str, CapabilityProbe] = {
        "datoviz.facade.import": CapabilityProbe(
            capability="datoviz.facade.import",
            source="facade",
            symbol="datoviz",
            supported=facade_import.imported,
            reason=None if facade_import.imported else facade_import.error_message,
        ),
        "datoviz.raw.import": CapabilityProbe(
            capability="datoviz.raw.import",
            source="raw",
            symbol="datoviz.raw",
            supported=raw_import.imported,
            reason=None if raw_import.imported else raw_import.error_message,
        ),
    }
    for capability, (source, symbol) in REQUIRED_CAPABILITIES.items():
        symbols = facade_symbols if source == "facade" else raw_symbols
        available = symbols.get(
            symbol, SymbolProbe(symbol=symbol, available=False, source=source)
        ).available
        matrix[capability] = CapabilityProbe(
            capability=capability,
            source=source,
            symbol=symbol,
            supported=available,
            reason=None if available else f"missing {source} symbol {symbol}",
        )
    return dict(sorted(matrix.items()))


def _enum_style_matrix(facade: Any | None, raw: Any | None) -> dict[str, SymbolProbe]:
    matrix: dict[str, SymbolProbe] = {}
    for symbol in ENUM_AND_STYLE_SYMBOLS:
        facade_available = _has_symbol(facade, symbol)
        raw_available = _has_symbol(raw, symbol)
        source = "facade" if facade_available else "raw"
        matrix[symbol] = SymbolProbe(
            symbol=symbol, available=facade_available or raw_available, source=source
        )
    return dict(sorted(matrix.items()))


def _text_symbol_matrix(facade: Any | None, raw: Any | None) -> dict[str, SymbolProbe]:
    matrix: dict[str, SymbolProbe] = {}
    for symbol in TEXT_SYMBOLS:
        facade_available = _has_symbol(facade, symbol)
        raw_available = _has_symbol(raw, symbol)
        source = "facade" if facade_available else "raw"
        matrix[symbol] = SymbolProbe(
            symbol=symbol, available=facade_available or raw_available, source=source
        )
    return dict(sorted(matrix.items()))


def _text_capability_matrix(
    text_symbols: Mapping[str, SymbolProbe],
) -> dict[str, CapabilityProbe]:
    matrix: dict[str, CapabilityProbe] = {}
    for capability, symbols in TEXT_RENDERER_CAPABILITIES.items():
        missing = tuple(
            symbol
            for symbol in symbols
            if not text_symbols.get(
                symbol, SymbolProbe(symbol=symbol, available=False, source="facade")
            ).available
        )
        matrix[capability] = CapabilityProbe(
            capability=capability,
            source="facade_or_raw",
            symbol=",".join(symbols),
            supported=not missing,
            reason=None if not missing else f"missing symbols: {missing}",
        )
    return dict(sorted(matrix.items()))


def _mesh_symbol_matrix(facade: Any | None, raw: Any | None) -> dict[str, SymbolProbe]:
    matrix: dict[str, SymbolProbe] = {}
    for symbol in MESH_SYMBOLS:
        facade_available = _has_symbol(facade, symbol)
        raw_available = _has_symbol(raw, symbol)
        source = "facade" if facade_available else "raw"
        matrix[symbol] = SymbolProbe(
            symbol=symbol, available=facade_available or raw_available, source=source
        )
    return dict(sorted(matrix.items()))


def _mesh_capability_matrix(
    mesh_symbols: Mapping[str, SymbolProbe],
) -> dict[str, CapabilityProbe]:
    matrix: dict[str, CapabilityProbe] = {}
    for capability, symbols in MESH_RENDERER_CAPABILITIES.items():
        missing = tuple(
            symbol
            for symbol in symbols
            if not mesh_symbols.get(
                symbol, SymbolProbe(symbol=symbol, available=False, source="facade")
            ).available
        )
        matrix[capability] = CapabilityProbe(
            capability=capability,
            source="facade_or_raw",
            symbol=",".join(symbols),
            supported=not missing,
            reason=None if not missing else f"missing symbols: {missing}",
        )
    return dict(sorted(matrix.items()))


def _color_mapping_symbol_matrix(
    facade: Any | None, raw: Any | None
) -> dict[str, SymbolProbe]:
    matrix: dict[str, SymbolProbe] = {}
    for symbol in COLOR_MAPPING_SYMBOLS:
        facade_available = _has_symbol(facade, symbol)
        raw_available = _has_symbol(raw, symbol)
        source = "facade" if facade_available else "raw"
        matrix[symbol] = SymbolProbe(
            symbol=symbol, available=facade_available or raw_available, source=source
        )
    return dict(sorted(matrix.items()))


def _color_mapping_capability_matrix(
    color_symbols: Mapping[str, SymbolProbe],
    facade_symbols: Mapping[str, SymbolProbe],
    raw_symbols: Mapping[str, SymbolProbe],
) -> dict[str, CapabilityProbe]:
    matrix: dict[str, CapabilityProbe] = {}
    all_symbols: dict[str, SymbolProbe] = {
        **dict(raw_symbols),
        **dict(facade_symbols),
        **dict(color_symbols),
    }
    for capability, symbols in COLOR_MAPPING_CAPABILITIES.items():
        missing = tuple(
            symbol
            for symbol in symbols
            if not all_symbols.get(
                symbol, SymbolProbe(symbol=symbol, available=False, source="facade")
            ).available
        )
        matrix[capability] = CapabilityProbe(
            capability=capability,
            source="facade_or_raw",
            symbol=",".join(symbols),
            supported=not missing,
            reason=None if not missing else f"missing symbols: {missing}",
        )
    for capability, reason in COLOR_MAPPING_UNVERIFIED_CAPABILITY_REASONS.items():
        matrix[capability] = CapabilityProbe(
            capability=capability,
            source="semantic_probe",
            symbol="",
            supported=False,
            reason=reason,
        )
    return dict(sorted(matrix.items()))


def _source_symbol_matrix(
    source: Path, symbols: Sequence[str]
) -> dict[str, list[SourceSymbolHit]]:
    matrix: dict[str, list[SourceSymbolHit]] = {symbol: [] for symbol in symbols}
    if not source.exists():
        return matrix
    source_files = _datoviz_source_files(source)
    for file_path in source_files:
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = str(file_path.relative_to(source))
        for line_number, line in enumerate(text.splitlines(), start=1):
            for symbol in symbols:
                if symbol in line:
                    matrix[symbol].append(
                        SourceSymbolHit(path=relative, line=line_number)
                    )
    return matrix


def _datoviz_source_files(source: Path) -> tuple[Path, ...]:
    candidates: list[Path] = []
    for relative in ("README.md", "datoviz/__init__.py", "datoviz/raw.py"):
        path = source / relative
        if path.exists():
            candidates.append(path)
    for examples in (
        source / "examples" / "c" / "visuals",
        source / "examples" / "c" / "features",
    ):
        if examples.exists():
            candidates.extend(sorted(examples.glob("*.c")))
    include_dir = source / "include" / "datoviz"
    if include_dir.exists():
        candidates.extend(sorted(include_dir.rglob("*.h")))
    return tuple(dict.fromkeys(candidates))


def _probe_minimal_point_scene(
    facade: Any | None, matrix: Mapping[str, CapabilityProbe]
) -> MinimalPointProbe:
    required = (
        "scene.create.dvz_scene",
        "scene.figure.dvz_figure",
        "scene.panel.dvz_panel_full",
        "visual.point.constructor.dvz_point",
        "visual.data.dvz_visual_set_data",
        "panel.add_visual.dvz_panel_add_visual",
    )
    missing = tuple(name for name in required if not matrix[name].supported)
    if facade is None or missing:
        return MinimalPointProbe(
            attempted=False,
            supported=False,
            reason=f"missing capabilities: {missing}",
            calls_completed=(),
        )

    calls: list[str] = []
    try:
        scene = facade.dvz_scene()
        calls.append("dvz_scene")
        figure = facade.dvz_figure(scene, 64, 64, 0)
        calls.append("dvz_figure")
        panel = facade.dvz_panel_full(figure)
        calls.append("dvz_panel_full")
        visual = facade.dvz_point(scene, 0)
        calls.append("dvz_point")
        facade.dvz_visual_set_data(
            visual, "position", np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        )
        calls.append("dvz_visual_set_data.position")
        facade.dvz_visual_set_data(
            visual, "color", np.array([[255, 255, 255, 255]], dtype=np.uint8)
        )
        calls.append("dvz_visual_set_data.color")
        facade.dvz_visual_set_data(
            visual, "diameter_px", np.array([4.0], dtype=np.float32)
        )
        calls.append("dvz_visual_set_data.diameter_px")
        facade.dvz_panel_add_visual(panel, visual, None)
        calls.append("dvz_panel_add_visual")
    except Exception as exc:  # noqa: BLE001 - construction failures are probe data.
        return MinimalPointProbe(
            attempted=True,
            supported=False,
            reason=f"{type(exc).__name__}: {exc}",
            calls_completed=tuple(calls),
        )
    return MinimalPointProbe(
        attempted=True, supported=True, reason=None, calls_completed=tuple(calls)
    )


def _git_revision(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def _string_attr(module: Any | None, name: str) -> str | None:
    if module is None:
        return None
    value = getattr(module, name, None)
    return value if isinstance(value, str) else None


def _default_banned_scan_paths() -> tuple[Path, ...]:
    return (
        Path("src/gsp/qa/visual"),
        Path("src/gsp_datoviz/protocol_renderer.py"),
        Path("src/gsp_datoviz/capabilities.py"),
        Path(".agent/missions"),
        Path(".agent/tasks"),
        Path("spec"),
    )


def _iter_scan_files(path: Path) -> tuple[Path, ...]:
    if not path.exists():
        return ()
    if path.is_file():
        return (path,)
    suffixes = {".md", ".py", ".rst", ".txt"}
    return tuple(
        sorted(
            file_path
            for file_path in path.rglob("*")
            if file_path.is_file() and file_path.suffix in suffixes
        )
    )


def _is_allowed_banned_context(path: Path) -> bool:
    normalized = path.as_posix()
    if normalized.endswith("src/gsp/qa/visual/datoviz_probe.py") or normalized.endswith(
        "gsp/qa/visual/datoviz_probe.py"
    ):
        return True
    if normalized.startswith("tests/"):
        return True
    if normalized.startswith(".agent/consultations/"):
        return True
    if normalized.startswith(".agent/missions/") or normalized.startswith(
        ".agent/tasks/"
    ):
        return True
    return False
