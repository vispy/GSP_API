"""Datoviz v0.4-dev protocol capability declarations."""

from __future__ import annotations

from types import ModuleType
from typing import Any

from gsp.protocol import AxisProviderCapability


DATOVIZ_V04_AXIS_PROVIDER = "datoviz.v04.panel_axis.wip"

_REQUIRED_DVZ_AXIS_FUNCTIONS = (
    "dvz_panel_set_domain",
    "dvz_panel_view2d",
    "dvz_panel_set_view2d",
    "dvz_panel_axis",
    "dvz_axis_set_label",
    "dvz_axis_set_tick_policy",
)

_OPTIONAL_DVZ_AXIS_FUNCTIONS = (
    "dvz_axis_set_visible",
    "dvz_axis_set_grid",
    "dvz_axis_set_style",
    "dvz_axis_set_plot_margins",
    "dvz_panel_visible_domain",
    "dvz_panel_data_to_visual_positions",
)


def datoviz_v04_axis_provider_capability(dvz: ModuleType | Any | None = None) -> AxisProviderCapability:
    """Return the Datoviz v0.4-dev native axis provider capability.

    The local v0.4-dev headers contain the native axis API. Runtime support is
    advertised only when the Python facade/raw binding exposes the verified symbols.
    """
    if dvz is None:
        try:
            import datoviz as dvz
        except ModuleNotFoundError:
            return _unsupported("Datoviz is not importable")

    missing = tuple(name for name in _REQUIRED_DVZ_AXIS_FUNCTIONS if not hasattr(dvz, name))
    if missing:
        return _unsupported(f"Datoviz Python binding is missing v0.4-dev axis symbols: {missing}")

    return AxisProviderCapability(
        provider_id=DATOVIZ_V04_AXIS_PROVIDER,
        backend_id="datoviz",
        provider_status="adapted",
        supports_explicit_ticks=False,
        supports_auto_ticks_gsp_policy=False,
        supports_backend_auto_ticks=True,
        supports_tick_labels=True,
        supports_axis_labels=True,
        supports_title=False,
        supports_grid=hasattr(dvz, "dvz_axis_set_grid"),
        supports_style_basic=hasattr(dvz, "dvz_axis_set_style"),
        supports_visible_domain_readback=hasattr(dvz, "dvz_panel_visible_domain"),
        supports_guide_query=False,
        supports_text_query=False,
        diagnostics=(
            "axis-provider-selected: datoviz.v04.panel_axis.wip",
            "axis-provider-adapted: backend-native ticks used; explicit GSP ticks unsupported by verified binding",
            "axis-guide-query-unsupported: provider renders guides but cannot query tick labels",
        ),
    )


def datoviz_v04_axis_symbols(dvz: ModuleType | Any) -> dict[str, bool]:
    """Return required/optional Datoviz axis symbol availability for diagnostics/tests."""
    names = _REQUIRED_DVZ_AXIS_FUNCTIONS + _OPTIONAL_DVZ_AXIS_FUNCTIONS
    return {name: hasattr(dvz, name) for name in names}


def _unsupported(diagnostic: str) -> AxisProviderCapability:
    return AxisProviderCapability(
        provider_id=DATOVIZ_V04_AXIS_PROVIDER,
        backend_id="datoviz",
        provider_status="unsupported",
        diagnostics=(diagnostic,),
    )
