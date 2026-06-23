from __future__ import annotations

import importlib
import importlib.abc
import json
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from importlib import resources

import pytest


def test_core_import_surface() -> None:
    gsp = importlib.import_module("gsp")
    vispy2 = importlib.import_module("vispy2")
    matplotlib_backend = importlib.import_module("gsp_matplotlib")
    network_backend = importlib.import_module("gsp_network")

    assert gsp.__doc__ is not None
    assert hasattr(vispy2, "Figure")
    assert hasattr(matplotlib_backend, "register_renderer_matplotlib")
    assert hasattr(network_backend, "register_renderer_network")


def test_datoviz_protocol_modules_import_without_datoviz() -> None:
    with _blocked_datoviz_modules():
        datoviz_backend = importlib.import_module("gsp_datoviz")
        protocol_renderer = importlib.import_module("gsp_datoviz.protocol_renderer")
        capabilities = importlib.import_module("gsp_datoviz.capabilities")
        query = importlib.import_module("gsp_datoviz.query")

        assert hasattr(protocol_renderer, "DatovizV04ProtocolRenderer")
        assert hasattr(capabilities, "datoviz_v04_capability_snapshot")
        assert hasattr(query, "datoviz_v04_query_binding_ready")
        with pytest.raises(ModuleNotFoundError):
            datoviz_backend.register_renderer_datoviz()
        with pytest.raises(ModuleNotFoundError):
            datoviz_backend.register_renderer_datoviz_v03()


def test_legacy_datoviz_registers_as_v03_when_available() -> None:
    try:
        datoviz_backend = importlib.import_module("gsp_datoviz")
        importlib.import_module("gsp_datoviz.renderer_registration")
    except ModuleNotFoundError as exc:
        if exc.name == "datoviz" or (exc.name is not None and exc.name.startswith("datoviz.")):
            pytest.skip("legacy Datoviz wrapper is unavailable")
        raise

    from gsp.utils.renderer_registery import RendererRegistry

    datoviz_backend.register_renderer_datoviz_v03()

    assert RendererRegistry._get_item_by_name("datoviz-v03").renderer_name == "datoviz-v03"
    with pytest.raises(ValueError, match="Renderer 'datoviz' not found"):
        RendererRegistry._get_item_by_name("datoviz")


def test_minimal_json_fixture_is_package_resource() -> None:
    fixture_path = resources.files("fixtures.conformance").joinpath("minimal_v0_1.json")
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    assert fixture["schema_kind"] == "gsp.conformance.fixture"
    assert fixture["schema_version"] == "0.1.0"


def test_gsp_extra_import_surface() -> None:
    object3d = importlib.import_module("gsp_extra.object3d")
    awsd_controls = importlib.import_module("gsp_extra.camera_controls.object_controls_awsd")
    trackball_controls = importlib.import_module("gsp_extra.camera_controls.object_controls_trackball")
    glm = importlib.import_module("gsp_extra.mpl3d.glm")

    assert hasattr(object3d, "Object3D")
    assert hasattr(awsd_controls, "ObjectControlAwsd")
    assert hasattr(trackball_controls, "ObjectControlsTrackball")
    assert hasattr(glm, "translate")


class _BlockDatovizFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path: object | None, target: object | None = None) -> None:
        if fullname == "datoviz" or fullname.startswith("datoviz."):
            raise ModuleNotFoundError(f"No module named {fullname!r}", name=fullname)
        return None


@contextmanager
def _blocked_datoviz_modules() -> Iterator[None]:
    saved_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "datoviz" or name.startswith("datoviz.") or name == "gsp_datoviz" or name.startswith("gsp_datoviz.")
    }
    for name in list(saved_modules):
        sys.modules.pop(name, None)

    finder = _BlockDatovizFinder()
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        sys.meta_path.remove(finder)
        for name in list(sys.modules):
            if name == "datoviz" or name.startswith("datoviz.") or name == "gsp_datoviz" or name.startswith("gsp_datoviz."):
                sys.modules.pop(name, None)
        sys.modules.update(saved_modules)
