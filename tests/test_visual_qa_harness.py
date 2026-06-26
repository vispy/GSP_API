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
from gsp.qa.visual.capability_matrix import build_capability_matrix
from gsp.qa.visual.review_pack import run_visual_review_pack
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
    assert payload["datoviz_color_pipeline"] == "legacy_srgb_blend"
    assert isinstance(payload["datoviz_probe_summary"]["facade_imported"], bool)
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["datoviz_color_pipeline"] == "legacy_srgb_blend"


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
    assert backend["datoviz_color_pipeline"] == "legacy_srgb_blend"
    if backend["status"] == "rendered":
        assert Path(str(backend["artifact_path"])).stat().st_size > 0
        assert "backends/datoviz/" in str(backend["artifact_path"])
    else:
        unsupported_path = Path(str(backend["unsupported_path"]))
        payload = json.loads(unsupported_path.read_text(encoding="utf-8"))
        assert payload["schema_kind"] == "gsp.visual_qa.unsupported"
        assert payload["backend_id"] == "datoviz"
        assert payload["case_id"] == "point/basic_ndc"
        assert payload["datoviz_color_pipeline"] == "legacy_srgb_blend"


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


def test_visual_qa_datoviz_linear_color_pipeline_override_is_recorded(
    tmp_path: Path,
) -> None:
    """S023 can still opt into the Datoviz-correct color pipeline."""
    report = run_visual_qa_suite(
        out_dir=tmp_path,
        backends=("datoviz",),
        case_ids=("point/basic_ndc",),
        run_id="test-datoviz-linear",
        resolution=(96, 96),
        datoviz_color_pipeline="linear_srgb",
    )

    assert report["datoviz_color_pipeline"] == "linear_srgb"
    backend = report["cases"][0]["backends"]["datoviz"]
    assert backend["datoviz_color_pipeline"] == "linear_srgb"
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["datoviz_color_pipeline"] == "linear_srgb"


def test_capability_matrix_marks_matplotlib_strict_and_unselected_datoviz_not_run(
    tmp_path: Path,
) -> None:
    """The S029 matrix distinguishes reference success from unselected backends."""
    report = run_visual_qa_suite(
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=("point/basic_ndc",),
        run_id="test-matrix",
        resolution=(96, 96),
    )

    matrix = build_capability_matrix(report)
    rows = matrix["rows"]
    assert isinstance(rows, list)
    by_backend = {row["backend"]: row for row in rows}

    assert by_backend["matplotlib"]["status"] == "strict"
    assert by_backend["matplotlib"]["reason_code"] == "matplotlib_reference_rendered"
    assert by_backend["datoviz"]["status"] == "not_run"
    assert by_backend["datoviz"]["reason_code"] == "backend_not_run"


def test_capability_matrix_classifies_datoviz_offscreen_disabled() -> None:
    """Datoviz disabled and unsupported states are separate review-pack outcomes."""
    report = {
        "suite": "s028",
        "stage": "S028",
        "run_id": "disabled",
        "cases": [
            {
                "case_id": "point/basic_ndc",
                "family": "point",
                "required_features": ["point", "ndc"],
                "backends": {
                    "datoviz": {
                        "status": "unsupported",
                        "reason": (
                            "Datoviz in-process offscreen QA is disabled by default "
                            "because native offscreen view creation can abort the Python process"
                        ),
                    }
                },
            }
        ],
    }

    matrix = build_capability_matrix(report)
    datoviz_row = [
        row
        for row in matrix["rows"]
        if isinstance(row, dict) and row["backend"] == "datoviz"
    ][0]

    assert datoviz_row["status"] == "disabled"
    assert datoviz_row["reason_code"] == "datoviz_offscreen_disabled"


def test_visual_review_pack_writes_matrix_and_index(tmp_path: Path) -> None:
    """The S029 review-pack command writes the policy layer over visual QA artifacts."""
    result = run_visual_review_pack(
        out_dir=tmp_path,
        mode="matplotlib-only",
        case_ids=("point/basic_ndc",),
        run_id="test-review-pack",
        resolution=(96, 96),
    )

    assert Path(str(result["index_path"])).exists()
    assert Path(str(result["capability_matrix_path"])).exists()
    assert (tmp_path / "summary.json").exists()
    matrix = json.loads((tmp_path / "capability_matrix.json").read_text())
    assert matrix["schema_kind"] == "gsp.visual_qa.capability_matrix"
    assert matrix["summary"]["strict"] == 1
    assert matrix["summary"]["not_run"] == 1


def test_s029_datoviz_rendered_family_audit_promotes_only_exact_scopes() -> None:
    report = {
        "suite": "s028",
        "stage": "S029",
        "run_id": "unit",
        "cases": [
            {
                "case_id": "point/basic_ndc",
                "family": "point",
                "required_features": ["point", "ndc", "rgba8", "pixel-size"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "image/scalar_gray_clim_ndc",
                "family": "image",
                "required_features": ["image", "ndc", "scalar", "gray", "clim"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "color/scalar_image_viridis_colorbar",
                "family": "color",
                "required_features": ["image", "scalar", "colormap", "colorbar"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "color/point_scalar_gray_range",
                "family": "color",
                "required_features": ["point", "scalar", "colormap"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "color/marker_scalar_fill_alpha",
                "family": "color",
                "required_features": ["marker", "scalar", "fill", "alpha"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "text/basic_ndc",
                "family": "text",
                "required_features": ["text", "ndc", "rgba8"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "text/anchor_grid_ndc",
                "family": "text",
                "required_features": ["text", "ndc", "anchor"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "text/rotation_alpha_ndc",
                "family": "text",
                "required_features": ["text", "ndc", "rotation", "alpha"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "text/data_vs_ndc",
                "family": "text",
                "required_features": ["text", "data", "ndc"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "text/multiline_unicode_smoke",
                "family": "text",
                "required_features": ["text", "multiline", "unicode"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "mesh/single_triangle_uniform_ndc_2d",
                "family": "mesh",
                "required_features": ["mesh", "ndc", "uniform-rgba"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "mesh/indexed_square_uniform_ndc_2d",
                "family": "mesh",
                "required_features": ["mesh", "ndc", "indexed", "uniform-rgba"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "mesh/indexed_square_per_face_ndc_2d",
                "family": "mesh",
                "required_features": ["mesh", "ndc", "indexed", "face-rgba"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
        ],
    }

    matrix = build_capability_matrix(report)
    rows = {
        (row["backend"], row["case_id"]): row
        for row in matrix["rows"]
        if row["backend"] == "datoviz"
    }

    assert rows[("datoviz", "point/basic_ndc")]["status"] == "strict"
    assert rows[("datoviz", "point/basic_ndc")]["promotion_blockers"] == []
    assert rows[("datoviz", "image/scalar_gray_clim_ndc")]["status"] == "strict"
    assert "CPU maps scalar gray" in rows[
        ("datoviz", "image/scalar_gray_clim_ndc")
    ]["known_adaptations"][0]
    assert rows[("datoviz", "color/scalar_image_viridis_colorbar")]["status"] == "strict"
    assert "explicit GSP tick values" in rows[
        ("datoviz", "color/scalar_image_viridis_colorbar")
    ]["known_adaptations"][1]
    assert rows[("datoviz", "color/point_scalar_gray_range")]["status"] == "strict"
    assert "endpoint clipping" in rows[
        ("datoviz", "color/point_scalar_gray_range")
    ]["known_adaptations"][1]
    assert rows[("datoviz", "color/marker_scalar_fill_alpha")]["status"] == "strict"
    assert "scalar fill alpha" in rows[
        ("datoviz", "color/marker_scalar_fill_alpha")
    ]["known_adaptations"][1]
    assert rows[("datoviz", "text/basic_ndc")]["status"] == "adapted"
    assert rows[("datoviz", "text/basic_ndc")]["promotion_blockers"] == [
        "default BASELINE text-anchor semantics are not strictly verified by the Datoviz adapter"
    ]
    assert rows[("datoviz", "text/anchor_grid_ndc")]["status"] == "adapted"
    assert "text-box anchors" in rows[
        ("datoviz", "text/anchor_grid_ndc")
    ]["promotion_blockers"][0]
    assert rows[("datoviz", "text/rotation_alpha_ndc")]["status"] == "strict"
    assert rows[("datoviz", "text/rotation_alpha_ndc")]["query_supported"] is False
    assert rows[("datoviz", "text/rotation_alpha_ndc")]["promotion_blockers"] == []
    assert "center-anchored rotation" in rows[
        ("datoviz", "text/rotation_alpha_ndc")
    ]["known_adaptations"][1]
    assert rows[("datoviz", "text/data_vs_ndc")]["status"] == "adapted"
    assert "identity [-1,+1]" in rows[
        ("datoviz", "text/data_vs_ndc")
    ]["promotion_blockers"][0]
    assert rows[("datoviz", "text/multiline_unicode_smoke")]["status"] == "adapted"
    assert "Unicode fallback" in rows[
        ("datoviz", "text/multiline_unicode_smoke")
    ]["promotion_blockers"][0]
    assert rows[("datoviz", "mesh/single_triangle_uniform_ndc_2d")]["status"] == "strict"
    assert rows[("datoviz", "mesh/single_triangle_uniform_ndc_2d")][
        "query_supported"
    ] is False
    assert "z=0 adaptation" in rows[
        ("datoviz", "mesh/single_triangle_uniform_ndc_2d")
    ]["known_adaptations"][0]
    assert rows[("datoviz", "mesh/indexed_square_uniform_ndc_2d")]["status"] == "strict"
    assert "shared-vertex" in rows[
        ("datoviz", "mesh/indexed_square_uniform_ndc_2d")
    ]["known_adaptations"][1]
    assert rows[("datoviz", "mesh/indexed_square_per_face_ndc_2d")]["status"] == "strict"
    assert rows[("datoviz", "mesh/indexed_square_per_face_ndc_2d")][
        "query_supported"
    ] is False
    assert "duplicating triangle vertices" in rows[
        ("datoviz", "mesh/indexed_square_per_face_ndc_2d")
    ]["known_adaptations"][0]


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
        dvz_visual_set_depth_test=lambda *args: None,
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
