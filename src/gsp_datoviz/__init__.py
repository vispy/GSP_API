"""GSP Datoviz integration package.

The legacy renderer subpackages target the older Datoviz Python wrapper surface.
Datoviz v0.4 protocol work lives in :mod:`gsp_datoviz.protocol_renderer` and must
remain importable even when those legacy wrapper modules are absent.
"""

from __future__ import annotations

from typing import Callable


_LEGACY_IMPORT_ERROR: ModuleNotFoundError | None = None
register_renderer_datoviz: Callable[[], None]

try:
    from .renderer_registration import register_renderer_datoviz
except ModuleNotFoundError as exc:
    if exc.name == "datoviz" or (exc.name is not None and exc.name.startswith("datoviz.")):
        _LEGACY_IMPORT_ERROR = exc

        def register_renderer_datoviz() -> None:
            """Report why the legacy Datoviz renderer cannot be registered."""
            assert _LEGACY_IMPORT_ERROR is not None
            raise _LEGACY_IMPORT_ERROR

    else:
        raise
else:
    register_renderer_datoviz()


__all__ = ["register_renderer_datoviz"]
