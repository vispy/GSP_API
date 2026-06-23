"""GSP Datoviz integration package.

The legacy renderer subpackages target the older Datoviz Python wrapper surface
and register under the ``datoviz-v03`` renderer id. Datoviz v0.4 protocol work
lives in :mod:`gsp_datoviz.protocol_renderer` and is the canonical ``datoviz``
backend for protocol-facing code.
"""

from __future__ import annotations

from typing import Callable


_LEGACY_IMPORT_ERROR: ModuleNotFoundError | None = None
register_renderer_datoviz: Callable[[], None]
register_renderer_datoviz_v03: Callable[[], None]

try:
    from .renderer_registration import register_renderer_datoviz, register_renderer_datoviz_v03
except ModuleNotFoundError as exc:
    if exc.name == "datoviz" or (exc.name is not None and exc.name.startswith("datoviz.")):
        _LEGACY_IMPORT_ERROR = exc

        def register_renderer_datoviz() -> None:
            """Report why the legacy Datoviz renderer cannot be registered."""
            assert _LEGACY_IMPORT_ERROR is not None
            raise _LEGACY_IMPORT_ERROR

        def register_renderer_datoviz_v03() -> None:
            """Report why the legacy Datoviz renderer cannot be registered."""
            register_renderer_datoviz()

    else:
        raise
else:
    register_renderer_datoviz()


__all__ = ["register_renderer_datoviz", "register_renderer_datoviz_v03"]
