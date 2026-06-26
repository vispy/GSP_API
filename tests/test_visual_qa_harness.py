"""Tests for the S023 visual QA harness."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.image as mpimg
import pytest

from gsp.protocol import (
    TRANSFORM_QUERY_PAYLOAD_KIND,
    QueryRequest,
    QueryStatus,
    TransformQueryPayload,
)
from gsp.qa.visual.cases import (
    S024_SUITE,
    S026_SUITE,
    S027_SUITE,
    S028_SUITE,
    get_case,
    list_cases,
)
from gsp.qa.visual.runner import run_visual_qa_suite
from gsp_matplotlib.protocol_query import QueryVisualEntry, query_visuals


def test_s023_case_registry_lists_initial_cases() -> None:
    """The harness starts with the approved Point/Image smoke cases."""
    case_ids = [case.case_id for case in list_cases()]

    assert case_ids == [
        "point/basic_ndc",
        "point/diameter_ramp_ndc",
        "point/alpha_overlap_ndc",
        "marker/shapes_ndc",
        "marker/angle_size_stroke_ndc",
        "segment/width_cap_ndc",
        "segment/alpha_order_ndc",
        "path/subpaths_width_join_ndc",
        "image/checker_nearest_ndc",
        "image/origin_lower_ndc",
        "image/scalar_gray_clim_ndc",
        "image/rgba_alpha_ndc",
        "overlay/point_over_image_ndc",
    ]


def test_s024_case_registry_extends_s023_with_text_cases() -> None:
    """S024 adds deterministic TextVisual QA cases without changing S023."""
    case_ids = [case.case_id for case in list_cases(suite=S024_SUITE)]

    assert case_ids[-5:] == [
        "text/basic_ndc",
        "text/anchor_grid_ndc",
        "text/rotation_alpha_ndc",
        "text/data_vs_ndc",
        "text/multiline_unicode_smoke",
    ]


def test_s024_text_visual_qa_run_writes_matplotlib_artifacts(tmp_path: Path) -> None:
    """S024 text cases render through the Matplotlib reference backend."""
    report = run_visual_qa_suite(
        suite=S024_SUITE,
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=("text/basic_ndc", "text/rotation_alpha_ndc"),
        run_id="test-s024-text",
        resolution=(320, 240),
    )

    assert report["stage"] == "S024"
    assert (tmp_path / "contact_sheets" / "s024_all_cases.png").stat().st_size > 0
    scene = json.loads(
        (tmp_path / "scenes" / "text_basic_ndc.scene.json").read_text(encoding="utf-8")
    )
    assert scene["visuals"][0]["family"] == "text"
    assert scene["visuals"][0]["texts"] == ["Alpha", "Beta", "Gamma", "Delta"]
    for case in report["cases"]:
        assert case["backends"]["matplotlib"]["status"] == "rendered"


def test_s024_text_visual_datoviz_reports_structured_unsupported(
    tmp_path: Path,
) -> None:
    """Datoviz text QA remains capability-gated until M078/M079."""
    report = run_visual_qa_suite(
        suite=S024_SUITE,
        out_dir=tmp_path,
        backends=("datoviz",),
        case_ids=("text/basic_ndc",),
        run_id="test-s024-text-dvz",
        resolution=(96, 96),
    )

    backend = report["cases"][0]["backends"]["datoviz"]
    assert backend["status"] == "unsupported"
    payload = json.loads(Path(str(backend["unsupported_path"])).read_text())
    assert payload["schema_kind"] == "gsp.visual_qa.unsupported"
    assert payload["case_id"] == "text/basic_ndc"


def test_visual_qa_run_writes_matplotlib_artifacts_and_report(tmp_path: Path) -> None:
    """A Matplotlib-only run writes the stable artifact layout."""
    report = run_visual_qa_suite(
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=("point/basic_ndc", "image/checker_nearest_ndc"),
        run_id="test-run",
        resolution=(320, 240),
    )

    assert report["schema_kind"] == "gsp.visual_qa.report"
    assert (tmp_path / "run_manifest.json").exists()
    assert (tmp_path / "environment.json").exists()
    assert (tmp_path / "manual_notes.yaml").exists()
    assert (tmp_path / "summary.md").exists()
    assert (tmp_path / "report.json").exists()
    assert (tmp_path / "contact_sheets" / "s023_all_cases.png").stat().st_size > 0

    for case in report["cases"]:
        assert isinstance(case, dict)
        scene_path = Path(str(case["scene_path"]))
        arrays_path = Path(str(case["arrays_path"]))
        assert scene_path.exists()
        assert arrays_path.exists()
        backend = case["backends"]["matplotlib"]
        assert backend["status"] == "rendered"
        artifact_path = Path(str(backend["artifact_path"]))
        assert artifact_path.stat().st_size > 0
        image = mpimg.imread(artifact_path)
        assert image.shape[:2] == (240, 320)

    payload = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert payload["run_id"] == "test-run"
    assert payload["datoviz_color_pipeline"] == "linear_srgb"
    assert isinstance(payload["datoviz_probe_summary"]["facade_imported"], bool)
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["datoviz_color_pipeline"] == "linear_srgb"


def test_visual_qa_datoviz_backend_reports_rendered_or_unsupported(
    tmp_path: Path,
) -> None:
    """The Datoviz path renders or writes explicit unsupported diagnostics."""
    report = run_visual_qa_suite(
        out_dir=tmp_path,
        backends=("datoviz",),
        case_ids=("point/basic_ndc",),
        run_id="test-datoviz",
        resolution=(96, 96),
    )

    case = report["cases"][0]
    assert isinstance(case, dict)
    backend = case["backends"]["datoviz"]
    assert backend["status"] in {"rendered", "unsupported"}
    assert backend["datoviz_color_pipeline"] == "linear_srgb"
    if backend["status"] == "rendered":
        assert Path(str(backend["artifact_path"])).stat().st_size > 0
        assert "backends/datoviz/" in str(backend["artifact_path"])
    else:
        unsupported_path = Path(str(backend["unsupported_path"]))
        payload = json.loads(unsupported_path.read_text(encoding="utf-8"))
        assert payload["schema_kind"] == "gsp.visual_qa.unsupported"
        assert payload["backend_id"] == "datoviz"
        assert payload["case_id"] == "point/basic_ndc"
        assert payload["datoviz_color_pipeline"] == "linear_srgb"


def test_visual_qa_datoviz_v04_alias_normalizes_to_datoviz(tmp_path: Path) -> None:
    """The former datoviz-v04 QA backend id remains a compatibility alias."""
    report = run_visual_qa_suite(
        out_dir=tmp_path,
        backends=("datoviz-v04",),
        case_ids=("point/basic_ndc",),
        run_id="test-datoviz-alias",
        resolution=(96, 96),
    )

    assert report["cases"][0]["backends"].keys() == {"datoviz"}
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["backends"] == ["datoviz"]


def test_visual_qa_datoviz_legacy_color_pipeline_override_is_recorded(
    tmp_path: Path,
) -> None:
    """S023 can still opt into the Matplotlib-compatibility color pipeline."""
    report = run_visual_qa_suite(
        out_dir=tmp_path,
        backends=("datoviz",),
        case_ids=("point/basic_ndc",),
        run_id="test-datoviz-legacy",
        resolution=(96, 96),
        datoviz_color_pipeline="legacy_srgb_blend",
    )

    assert report["datoviz_color_pipeline"] == "legacy_srgb_blend"
    backend = report["cases"][0]["backends"]["datoviz"]
    assert backend["datoviz_color_pipeline"] == "legacy_srgb_blend"
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["datoviz_color_pipeline"] == "legacy_srgb_blend"


def test_visual_qa_harness_does_not_import_legacy_datoviz_renderer() -> None:
    """The S023 harness uses the v0.4 protocol renderer, not the legacy renderer package."""
    source_root = Path("src/gsp/qa/visual")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in source_root.glob("*.py")
    )

    assert "gsp_datoviz.renderer" not in combined


def test_s025_case_registry_extends_s024_with_mesh_cases() -> None:
    """S025 adds strict MeshVisual QA cases after the S024 text cases."""
    from gsp.qa.visual.cases import S025_SUITE

    case_ids = [case.case_id for case in list_cases(suite=S025_SUITE)]

    assert case_ids[-3:] == [
        "mesh/single_triangle_uniform_ndc_2d",
        "mesh/indexed_square_uniform_ndc_2d",
        "mesh/indexed_square_per_face_ndc_2d",
    ]


def test_s025_mesh_visual_qa_run_writes_matplotlib_artifacts(tmp_path: Path) -> None:
    """S025 strict mesh cases render through the Matplotlib reference backend."""
    from gsp.qa.visual.cases import S025_SUITE

    report = run_visual_qa_suite(
        suite=S025_SUITE,
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=(
            "mesh/single_triangle_uniform_ndc_2d",
            "mesh/indexed_square_per_face_ndc_2d",
        ),
        run_id="test-s025-mesh",
        resolution=(320, 240),
    )

    assert report["stage"] == "S025"
    assert (tmp_path / "contact_sheets" / "s025_all_cases.png").stat().st_size > 0
    scene = json.loads(
        (
            tmp_path / "scenes" / "mesh_single_triangle_uniform_ndc_2d.scene.json"
        ).read_text(encoding="utf-8")
    )
    assert scene["visuals"][0]["family"] == "mesh"
    assert scene["visuals"][0]["color_mode"] == "uniform"
    for case in report["cases"]:
        assert case["backends"]["matplotlib"]["status"] == "rendered"


def test_s026_case_registry_extends_s025_with_color_cases() -> None:
    """S026 adds deterministic color mapping cases after the mesh suite."""
    case_ids = [case.case_id for case in list_cases(suite=S026_SUITE)]

    assert case_ids[-3:] == [
        "color/scalar_image_viridis_colorbar",
        "color/point_scalar_gray_range",
        "color/marker_scalar_fill_alpha",
    ]


def test_s026_color_visual_qa_run_writes_matplotlib_artifacts(tmp_path: Path) -> None:
    """S026 color cases render and serialize color scale resources."""
    report = run_visual_qa_suite(
        suite=S026_SUITE,
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=(
            "color/scalar_image_viridis_colorbar",
            "color/point_scalar_gray_range",
        ),
        run_id="test-s026-color",
        resolution=(360, 240),
    )

    assert report["stage"] == "S026"
    assert (tmp_path / "contact_sheets" / "s026_all_cases.png").stat().st_size > 0
    scene = json.loads(
        (
            tmp_path / "scenes" / "color_scalar_image_viridis_colorbar.scene.json"
        ).read_text(encoding="utf-8")
    )
    assert scene["color_scales"][0]["colormap"]["id"] == "viridis"
    assert scene["colorbar_guides"][0]["color_scale_id"] == "scale:viridis"
    assert scene["visuals"][0]["color_scale_id"] == "scale:viridis"
    for case in report["cases"]:
        assert case["backends"]["matplotlib"]["status"] == "rendered"


def test_s027_case_registry_extends_s026_with_transform_cases() -> None:
    """S027 adds deterministic transform and View2D QA cases after S026."""
    case_ids = [case.case_id for case in list_cases(suite=S027_SUITE)]

    assert case_ids[-3:] == [
        "transform/inline_named_equivalence",
        "transform/view2d_data_ndc_overlay",
        "transform/family_affine_view2d",
    ]


def test_s027_transform_visual_qa_run_writes_matplotlib_artifacts(
    tmp_path: Path,
) -> None:
    """S027 transform cases render and serialize transform/view fixture state."""
    report = run_visual_qa_suite(
        suite=S027_SUITE,
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=(
            "transform/inline_named_equivalence",
            "transform/family_affine_view2d",
        ),
        run_id="test-s027-transform",
        resolution=(360, 240),
    )

    assert report["stage"] == "S027"
    assert (tmp_path / "contact_sheets" / "s027_all_cases.png").stat().st_size > 0
    scene = json.loads(
        (
            tmp_path / "scenes" / "transform_family_affine_view2d.scene.json"
        ).read_text(encoding="utf-8")
    )
    assert scene["transform_resources"][0]["id"] == "transform:s027-family-shear"
    assert scene["views"][0]["id"] == "view:s027-family"
    assert scene["visuals"][0]["transform"]["ref"]["id"] == "transform:s027-family-shear"
    for case in report["cases"]:
        assert case["backends"]["matplotlib"]["status"] == "rendered"


def test_s027_transform_query_fixture_reports_inverse_payload() -> None:
    """The S027 QA fixture supports strict transformed query inverse payloads."""
    scene = get_case(
        "transform/inline_named_equivalence", suite=S027_SUITE
    ).build()
    resources = {resource.id: resource for resource in scene.transform_resources}
    result = query_visuals(
        QueryRequest(
            id="query:s027-transform",
            panel_id="panel:main",
            coordinate=(-0.0528, 0.0204),
        ),
        [QueryVisualEntry(scene.visuals[0])],
        transform_resources=resources,
    )

    assert result.status == QueryStatus.HIT
    assert result.extension_payload_kind == TRANSFORM_QUERY_PAYLOAD_KIND
    assert isinstance(result.extension_payload, TransformQueryPayload)
    assert result.extension_payload.panel_ndc == pytest.approx((-0.0528, 0.0204))
    assert result.extension_payload.declared_space_coord == pytest.approx(
        (-0.0528, 0.0204)
    )
    assert result.extension_payload.source_coord == pytest.approx((-0.28, 0.18))
    assert result.extension_payload.inline_transform_digest is not None


def test_s028_case_registry_extends_s027_with_guide_view2d_cases() -> None:
    """S028 adds deterministic guide/View2D QA cases after S027."""
    case_ids = [case.case_id for case in list_cases(suite=S028_SUITE)]

    assert case_ids[-2:] == [
        "guide/view2d_auto_grid",
        "guide/view2d_reversed_explicit",
    ]


def test_s028_guide_view2d_visual_qa_run_writes_matplotlib_artifacts(
    tmp_path: Path,
) -> None:
    """S028 guide cases render and serialize semantic guide state."""
    report = run_visual_qa_suite(
        suite=S028_SUITE,
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=(
            "guide/view2d_auto_grid",
            "guide/view2d_reversed_explicit",
        ),
        run_id="test-s028-guides",
        resolution=(360, 240),
    )

    assert report["stage"] == "S028"
    assert (tmp_path / "contact_sheets" / "s028_all_cases.png").stat().st_size > 0
    scene = json.loads(
        (
            tmp_path / "scenes" / "guide_view2d_reversed_explicit.scene.json"
        ).read_text(encoding="utf-8")
    )
    assert scene["views"][0]["x_range"] == [1.0, -1.0]
    assert scene["axis_guides"][0]["tick_spec"]["explicit_labels"] == [
        "right",
        "center",
        "left",
    ]
    assert scene["panel_text_guides"][0]["text"] == "S028 reversed guide View2D"
    assert scene["visuals"][0]["family"] == "point"
    for case in report["cases"]:
        assert case["backends"]["matplotlib"]["status"] == "rendered"


def test_datoviz_probe_reports_mesh_capabilities(tmp_path: Path) -> None:
    """The v0.4 probe records retained mesh evidence separately from text evidence."""
    from types import SimpleNamespace

    from gsp.qa.visual.datoviz_probe import probe_datoviz_v04

    source = tmp_path / "datoviz"
    include = source / "include" / "datoviz"
    include.mkdir(parents=True)
    (include / "scene.h").write_text(
        "DVZ_EXPORT DvzVisual* dvz_mesh(DvzScene* scene, uint32_t flags);\n"
        "DVZ_EXPORT int dvz_mesh_set_geometry(DvzVisual* visual, const DvzGeometry* geometry);\n"
        "DVZ_EXPORT int dvz_visual_set_index_data(DvzVisual* visual, const DvzIndex* indices, uint32_t index_count);\n",
        encoding="utf-8",
    )
    fake = SimpleNamespace(
        __version__="0.4-test",
        dvz_mesh=lambda *args: None,
        dvz_mesh_set_geometry=lambda *args: None,
        dvz_visual_set_data=lambda *args: None,
        dvz_visual_set_index_data=lambda *args: None,
        dvz_visual_set_material=lambda *args: None,
        dvz_visual_set_depth=lambda *args: None,
        dvz_visual_set_texture=lambda *args: None,
    )

    report = probe_datoviz_v04(source_path=source, facade_module=fake, raw_module=fake)
    payload = report.to_json()

    assert payload["mesh_symbols"]["dvz_mesh"]["available"] is True
    assert payload["mesh_symbols"]["dvz_mesh_set_geometry"]["available"] is True
    assert (
        payload["mesh_capability_matrix"]["mesh.visual.constructor"]["supported"]
        is True
    )
    assert payload["mesh_capability_matrix"]["mesh.index.upload"]["supported"] is True
    assert payload["source_symbol_matrix"]["dvz_mesh"]
