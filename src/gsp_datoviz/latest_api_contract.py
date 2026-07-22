"""Datoviz v0.4-dev generated binding contract for the GSP adapter."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Any


EXPECTED_DATOVIZ_PACKAGE_ROOT = Path("/Users/cyrille/GIT/Viz/datoviz/datoviz")

REQUIRED_DATOVIZ_V04_DEV_SYMBOLS: tuple[str, ...] = (
    "DvzVisualCoordSpace",
    "DVZ_VISUAL_COORD_VIEW",
    "DVZ_VISUAL_COORD_DATA",
    "DVZ_VISUAL_COORD_PANEL",
    "dvz_scene",
    "dvz_figure",
    "dvz_panel_full",
    "dvz_panel_add_visual",
    "dvz_panel_set_domain",
    "dvz_point",
    "dvz_image",
    "dvz_visual_set_data",
    "dvz_sampled_field_desc",
    "dvz_field_data_view",
    "dvz_sampled_field",
    "dvz_sampled_field_set_data",
    "dvz_visual_set_field",
    "dvz_field_sampling_desc",
    "dvz_visual_set_field_sampling",
    "dvz_sampled_field_destroy",
    "DvzCameraDesc",
    "DvzCameraView",
    "DvzCameraProjection",
    "DvzPanelView3DDesc",
    "DvzPanelView3DState",
    "DvzPanelFrameInfo",
    "dvz_panel_view3d_desc",
    "dvz_panel_set_view3d_desc",
    "dvz_panel_view3d_state",
    "dvz_panel_camera",
    "dvz_camera_desc",
    "dvz_camera_set_orthographic_bounds",
    "dvz_camera_set_view",
    "dvz_camera_get_view",
    "dvz_camera_get_projection",
    "dvz_camera_get_orthographic_bounds",
)

def datoviz_current_api_missing_symbols(module: ModuleType | Any) -> tuple[str, ...]:
    """Return required current generated-binding symbols absent from *module*."""
    return tuple(
        name for name in REQUIRED_DATOVIZ_V04_DEV_SYMBOLS if not hasattr(module, name)
    )


def datoviz_current_api_contract_diagnostics(
    module: ModuleType | Any,
    *,
    expected_package_root: Path | None = None,
) -> tuple[str, ...]:
    """Return latest-only contract diagnostics for a Datoviz module-like object."""
    diagnostics: list[str] = [
        "Datoviz v0.4-dev generated Python binding is missing required current API symbol: "
        f"{name}"
        for name in datoviz_current_api_missing_symbols(module)
    ]
    if expected_package_root is not None:
        module_file = getattr(module, "__file__", None)
        if module_file is None:
            diagnostics.append("Datoviz v0.4-dev generated Python binding has no __file__")
        else:
            package_root = expected_package_root.resolve()
            imported_file = Path(module_file).resolve()
            if package_root not in (imported_file, *imported_file.parents):
                diagnostics.append(
                    "Datoviz v0.4-dev generated Python binding was imported from "
                    f"{imported_file}, expected under {package_root}"
                )
    return tuple(diagnostics)
