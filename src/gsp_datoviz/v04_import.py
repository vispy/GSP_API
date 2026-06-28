"""Import bootstrap helpers for local Datoviz v0.4-dev checkouts."""

from __future__ import annotations

import os
from pathlib import Path
import sys


_ENV_SOURCE = "GSP_DATOVIZ_SOURCE"


def bootstrap_datoviz_v04_source() -> Path | None:
    """Prefer a source checkout for the Datoviz v0.4 adapter when available.

    By default this discovers the sibling `../datoviz` checkout used by local GSP
    development. Set `GSP_DATOVIZ_SOURCE=/path/to/datoviz` to override it, or set
    `GSP_DATOVIZ_SOURCE=none` to disable source-checkout bootstrapping.
    """
    source = _datoviz_source_path()
    if source is None:
        return None
    source_str = str(source)
    if sys.path[:1] != [source_str]:
        sys.path[:] = [path for path in sys.path if path != source_str]
        sys.path.insert(0, source_str)
    _configure_runtime_env(source)
    return source


def _datoviz_source_path() -> Path | None:
    configured = os.environ.get(_ENV_SOURCE)
    if configured is not None:
        if configured.lower() in {"", "0", "false", "none", "off"}:
            return None
        return _valid_source_path(Path(configured).expanduser())

    repo_root = Path(__file__).resolve().parents[2]
    candidates = (
        repo_root.parent / "datoviz",
        Path.cwd().resolve().parent / "datoviz",
    )
    for candidate in candidates:
        source = _valid_source_path(candidate)
        if source is not None:
            return source
    return None


def _valid_source_path(path: Path) -> Path | None:
    resolved = path.resolve()
    if (resolved / "datoviz" / "__init__.py").is_file():
        return resolved
    return None


def _configure_runtime_env(source: Path) -> None:
    build_src = source / "build" / "src"
    libdatoviz = build_src / _native_library_name()
    if libdatoviz.is_file():
        os.environ.setdefault("DATOVIZ_LIBRARY", str(libdatoviz))

    shaderc = build_src / "libshaderc_shared.dylib"
    if shaderc.is_file():
        os.environ.setdefault("DVZ_SHADERC_RUNTIME_LIBRARY", str(shaderc))

    if build_src.is_dir():
        existing = [path for path in os.environ.get("DVZ_WHEEL_RUNTIME_DIRS", "").split(os.pathsep) if path]
        build_src_str = str(build_src)
        os.environ["DVZ_WHEEL_RUNTIME_DIRS"] = os.pathsep.join([build_src_str, *[path for path in existing if path != build_src_str]])


def _native_library_name() -> str:
    if sys.platform == "darwin":
        return "libdatoviz.dylib"
    if sys.platform.startswith("linux"):
        return "libdatoviz.so"
    if sys.platform.startswith("win"):
        return "datoviz.dll"
    return "libdatoviz.dylib"
