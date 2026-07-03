"""Tests for the Datoviz v0.4 API probe."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from gsp.qa.visual.datoviz_probe import probe_datoviz_v04, scan_banned_symbols


class FakeDatovizFacade:
    """Small retained-scene facade used by probe tests."""

    __file__ = "/fake/datoviz/__init__.py"
    __version__ = "0.4.test"

    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def dvz_scene(self) -> str:
        self.calls.append(("dvz_scene",))
        return "scene"

    def dvz_figure(self, scene: object, width: int, height: int, flags: int) -> str:
        self.calls.append(("dvz_figure", scene, width, height, flags))
        return "figure"

    def dvz_panel_full(self, figure: object) -> str:
        self.calls.append(("dvz_panel_full", figure))
        return "panel"

    def dvz_panel_add_visual(
        self, panel: object, visual: object, attach_desc: object | None
    ) -> int:
        self.calls.append(("dvz_panel_add_visual", panel, visual, attach_desc))
        return 0

    def dvz_visual_set_data(self, visual: object, name: str, data: object) -> int:
        self.calls.append(("dvz_visual_set_data", visual, name, data))
        return 0

    def dvz_visual_set_data_many(
        self, visual: object, updates: object, count: int
    ) -> int:
        self.calls.append(("dvz_visual_set_data_many", visual, updates, count))
        return 0

    def dvz_visual_set_data_range(
        self, visual: object, name: str, offset: int, data: object
    ) -> int:
        self.calls.append(("dvz_visual_set_data_range", visual, name, offset, data))
        return 0

    def dvz_point(self, scene: object, flags: int) -> str:
        self.calls.append(("dvz_point", scene, flags))
        return "point"

    def dvz_marker(self, scene: object, flags: int) -> str:
        self.calls.append(("dvz_marker", scene, flags))
        return "marker"

    def dvz_segment(self, scene: object, flags: int) -> str:
        self.calls.append(("dvz_segment", scene, flags))
        return "segment"

    def dvz_path(self, scene: object, flags: int) -> str:
        self.calls.append(("dvz_path", scene, flags))
        return "path"

    def dvz_image(self, scene: object, flags: int) -> str:
        self.calls.append(("dvz_image", scene, flags))
        return "image"

    def dvz_path_set_subpaths(self, path: object, count: int, subpaths: object) -> int:
        self.calls.append(("dvz_path_set_subpaths", path, count, subpaths))
        return 0

    def dvz_path_set_caps(self, path: object, start: int, end: int) -> int:
        self.calls.append(("dvz_path_set_caps", path, start, end))
        return 0

    def dvz_path_set_join(self, path: object, join: int, miter_limit: float) -> int:
        self.calls.append(("dvz_path_set_join", path, join, miter_limit))
        return 0

    def dvz_sampled_field(self, scene: object, desc: object) -> str:
        self.calls.append(("dvz_sampled_field", scene, desc))
        return "field"

    def dvz_sampled_field_set_data(self, field: object, view: object) -> bool:
        self.calls.append(("dvz_sampled_field_set_data", field, view))
        return True

    def dvz_visual_set_field(self, visual: object, name: str, field: object) -> bool:
        self.calls.append(("dvz_visual_set_field", visual, name, field))
        return True

    def capture(
        self,
        scene: object,
        figure: object,
        path: str = "output.png",
        width: int = 800,
        height: int = 600,
    ) -> None:
        self.calls.append(("capture", scene, figure, path, width, height))

    class DvzVisualAttachDesc:
        """Fake attach descriptor."""


class FakeRaw:
    """Small raw binding surface used by probe tests."""

    __file__ = "/fake/datoviz/raw.py"
    DvzVisualAttachDesc = object
    DvzText = object
    DvzTextStyle = object
    DvzTextAtlas = object
    DvzTextAtlasSpec = object
    DvzTextRenderer = object
    DvzVisualCoordSpace = object
    DVZ_VISUAL_COORD_VIEW = 1
    DVZ_VISUAL_COORD_DATA = 2
    DVZ_VISUAL_COORD_PANEL = 3
    DVZ_PATH_JOIN_ROUND = 10
    DVZ_SEGMENT_CAP_ROUND = 11
    DVZ_BLEND_ALPHA = 12
    DVZ_SCENE_VISUAL_FAMILY_TEXT = 13

    def dvz_text(self, panel: object, flags: int) -> str:
        return "text"

    def dvz_text_set_string(self, text: object, string: bytes) -> None:
        return None

    def dvz_text_style(self) -> object:
        return object()

    def dvz_text_set_style(self, text: object, style: object) -> int:
        return 0

    def dvz_text_placement(self) -> object:
        return object()

    def dvz_text_set_placement(self, text: object, placement: object) -> None:
        return None

    def dvz_font(self, scene: object, desc: object) -> str:
        return "font"

    def dvz_font_desc(self) -> object:
        return object()

    def dvz_text_atlas_spec(self, renderer: object, size_px: float) -> object:
        return object()

    def dvz_font_atlas_ensure_strings(
        self, font: object, spec: object, strings: object, count: int
    ) -> bool:
        return True

    def dvz_font_atlas(self, font: object, spec: object) -> str:
        return "atlas"

    def dvz_text_atlas_field(self, atlas: object) -> str:
        return "field"

    def dvz_glyph(self, scene: object, flags: int) -> str:
        return "glyph"

    def dvz_glyph_set_atlas(self, visual: object, atlas: object) -> int:
        return 0


def test_probe_successful_fake_facade_is_json_safe(tmp_path: Path) -> None:
    source = tmp_path / "datoviz"
    source.mkdir()
    (source / "README.md").write_text(
        "dvz_scene\nDvzVisualAttachDesc\nDVZ_VISUAL_COORD_DATA\ndvz_text\ndvz_text_set_placement\n",
        encoding="utf-8",
    )
    facade = FakeDatovizFacade()

    report = probe_datoviz_v04(
        source_path=source,
        banned_scan_paths=(),
        facade_module=facade,
        raw_module=FakeRaw(),
    )
    payload = report.to_json()

    assert payload["installed_package"]["imported"] is True
    assert payload["sibling_source"]["exists"] is True
    assert payload["capability_matrix"]["scene.create.dvz_scene"]["supported"] is True
    assert (
        payload["capability_matrix"]["attach.coord_space.DVZ_VISUAL_COORD_DATA"]["supported"]
        is True
    )
    assert payload["minimal_point_scene"]["supported"] is True
    assert payload["minimal_point_scene"]["attempted"] is True
    assert (
        "dvz_visual_set_data.diameter_px"
        in payload["minimal_point_scene"]["calls_completed"]
    )
    assert payload["source_symbol_matrix"]["dvz_scene"] == [
        {"path": "README.md", "line": 1}
    ]
    assert payload["text_symbols"]["dvz_text"]["available"] is True
    assert payload["text_symbols"]["dvz_text_placement"]["available"] is True
    assert (
        payload["text_capability_matrix"]["text.visual.constructor"]["supported"]
        is True
    )
    assert payload["text_capability_matrix"]["text.placement"]["supported"] is True
    assert payload["source_symbol_matrix"]["dvz_text_set_placement"] == [
        {"path": "README.md", "line": 5}
    ]
    assert "color_mapping_capability_matrix" in payload
    json.dumps(payload)
    assert ("dvz_panel_add_visual", "panel", "point", None) in facade.calls


def test_probe_reports_missing_symbols_without_constructing_point(
    tmp_path: Path,
) -> None:
    class MinimalFacade:
        __file__ = "/fake/datoviz/__init__.py"

        def dvz_scene(self) -> str:
            return "scene"

    report = probe_datoviz_v04(
        source_path=tmp_path / "missing",
        banned_scan_paths=(),
        facade_module=MinimalFacade(),
        raw_module=None,
    )
    payload = report.to_json()

    assert payload["capability_matrix"]["scene.create.dvz_scene"]["supported"] is True
    assert (
        payload["capability_matrix"]["visual.point.constructor.dvz_point"]["supported"]
        is False
    )
    assert payload["minimal_point_scene"]["attempted"] is False
    assert "missing capabilities" in str(payload["minimal_point_scene"]["reason"])


def test_probe_imports_datoviz_from_source_path_when_not_installed(
    tmp_path: Path, monkeypatch
) -> None:
    """The probe can use a sibling Datoviz checkout without manual PYTHONPATH."""
    source = tmp_path / "datoviz"
    package = source / "datoviz"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(
        "def dvz_scene(): return 'scene-from-source'\n",
        encoding="utf-8",
    )
    (package / "raw.py").write_text(
        "class DvzBuiltinColormap:\n"
        "    DVZ_BUILTIN_COLORMAP_GRAY = 7\n"
        "class DvzScaleKind:\n"
        "    DVZ_SCALE_CONTINUOUS = 0\n",
        encoding="utf-8",
    )
    monkeypatch.delitem(sys.modules, "datoviz", raising=False)
    monkeypatch.delitem(sys.modules, "datoviz.raw", raising=False)

    report = probe_datoviz_v04(source_path=source, banned_scan_paths=())
    payload = report.to_json()

    assert payload["installed_package"]["imported"] is True
    assert payload["installed_package"]["path"].endswith("datoviz/__init__.py")
    assert (
        payload["color_mapping_symbols"]["DVZ_BUILTIN_COLORMAP_GRAY"]["available"]
        is True
    )
    assert payload["color_mapping_symbols"]["DVZ_SCALE_CONTINUOUS"]["available"] is True


def test_banned_symbol_detection_marks_source_hits_unexpected(tmp_path: Path) -> None:
    adapter = tmp_path / "adapter.py"
    adapter.write_text("def bad():\n    return 'dvz_point_alloc'\n", encoding="utf-8")

    hits = scan_banned_symbols((adapter,))

    assert len(hits) == 1
    assert hits[0].symbol == "dvz_point_alloc"
    assert hits[0].allowed_context is False


def test_probe_reports_color_mapping_capabilities(tmp_path: Path) -> None:
    """The v0.4 probe records S026 color mapping evidence separately."""
    from types import SimpleNamespace

    source = tmp_path / "datoviz"
    include = source / "include" / "datoviz"
    include.mkdir(parents=True)
    (include / "scene.h").write_text(
        "DVZ_EXPORT DvzScale* dvz_scale(DvzScene* scene, const DvzScaleDesc* desc);\n"
        "DVZ_EXPORT void dvz_scale_set_domain(DvzScale* scale, double min, double max);\n"
        "DVZ_EXPORT DvzColorbar* dvz_colorbar(DvzPanel* panel, DvzScale* scale, const DvzColorbarDesc* desc);\n",
        encoding="utf-8",
    )
    fake = SimpleNamespace(
        __version__="0.4-test",
        DvzColorbarDesc=object,
        DvzScaleDesc=object,
        DVZ_BUILTIN_COLORMAP_CIVIDIS=1,
        DVZ_BUILTIN_COLORMAP_GRAY=2,
        DVZ_BUILTIN_COLORMAP_INFERNO=3,
        DVZ_BUILTIN_COLORMAP_MAGMA=4,
        DVZ_BUILTIN_COLORMAP_PLASMA=5,
        DVZ_BUILTIN_COLORMAP_VIRIDIS=6,
        DVZ_COLORBAR_ORIENTATION_HORIZONTAL=7,
        DVZ_COLORBAR_ORIENTATION_VERTICAL=8,
        DVZ_FIELD_DIM_2D=9,
        DVZ_FIELD_FORMAT_R32_FLOAT=10,
        DVZ_FIELD_SEMANTIC_SCALAR=11,
        DVZ_SCALE_CONTINUOUS=12,
        dvz_colorbar=lambda *args: None,
        dvz_colormap_builtin=lambda *args: None,
        dvz_colormap_custom=lambda *args: None,
        dvz_colormap_set_stops=lambda *args: None,
        dvz_panel_query=lambda *args: None,
        dvz_panel_query_now=lambda *args: None,
        dvz_point=lambda *args: None,
        dvz_sampled_field=lambda *args: None,
        dvz_sampled_field_set_data=lambda *args: None,
        dvz_scene_poll_query=lambda *args: None,
        dvz_scale=lambda *args: None,
        dvz_scale_set_colormap=lambda *args: None,
        dvz_scale_set_domain=lambda *args: None,
        dvz_visual_set_data=lambda *args: None,
        dvz_visual_set_field=lambda *args: None,
        dvz_visual_set_scale=lambda *args: None,
    )

    report = probe_datoviz_v04(source_path=source, facade_module=fake, raw_module=fake)
    payload = report.to_json()

    assert payload["color_mapping_symbols"]["dvz_scale"]["available"] is True
    assert (
        payload["color_mapping_capability_matrix"]["color.scale.continuous"][
            "supported"
        ]
        is True
    )
    assert (
        payload["color_mapping_capability_matrix"]["color.image.scalar_field"][
            "supported"
        ]
        is True
    )
    assert (
        payload["color_mapping_capability_matrix"]["color.colorbar.semantic"][
            "supported"
        ]
        is True
    )
    assert (
        payload["color_mapping_capability_matrix"]["color.marker.scalar_fill"][
            "supported"
        ]
        is False
    )
    assert (
        "MarkerVisual scalar fill"
        in payload["color_mapping_capability_matrix"]["color.marker.scalar_fill"][
            "reason"
        ]
    )
    assert payload["source_symbol_matrix"]["dvz_colorbar"] == [
        {"path": "include/datoviz/scene.h", "line": 3}
    ]
