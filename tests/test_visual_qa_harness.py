"""Tests for the S023 visual QA harness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import numpy as np
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
    S034_SUITE,
    get_case,
    list_cases,
)
from gsp.qa.visual.capability_matrix import build_capability_matrix
from gsp.qa.visual.datoviz_probe import (
    DatovizV04ProbeReport,
    ImportProbe,
    MinimalPointProbe,
)
from gsp.qa.visual.review_pack import run_visual_review_pack
import gsp.qa.visual.runner as visual_runner
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
            {
                "case_id": "transform/inline_named_equivalence",
                "family": "transform",
                "required_features": [
                    "affine2d",
                    "inline-transform",
                    "named-transform",
                ],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "transform/view2d_data_ndc_overlay",
                "family": "transform",
                "required_features": ["view2d", "data", "ndc", "reversed-limits"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "rendered"},
                },
            },
            {
                "case_id": "transform/family_affine_view2d",
                "family": "transform",
                "required_features": [
                    "point",
                    "marker",
                    "segment",
                    "path",
                    "text",
                    "mesh",
                    "affine2d",
                    "view2d",
                ],
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
    assert (
        rows[("datoviz", "point/basic_ndc")]["review_classification"]
        == "pass.semantic_strict"
    )
    assert matrix["review_classification_summary"]["pass.semantic_strict"] > 0
    assert rows[("datoviz", "point/basic_ndc")]["promotion_blockers"] == []
    assert rows[("datoviz", "image/scalar_gray_clim_ndc")]["status"] == "strict"
    assert (
        "CPU maps scalar gray"
        in rows[("datoviz", "image/scalar_gray_clim_ndc")]["known_adaptations"][0]
    )
    assert (
        rows[("datoviz", "color/scalar_image_viridis_colorbar")]["status"] == "strict"
    )
    assert (
        "explicit GSP tick values"
        in rows[("datoviz", "color/scalar_image_viridis_colorbar")][
            "known_adaptations"
        ][1]
    )
    assert rows[("datoviz", "color/point_scalar_gray_range")]["status"] == "strict"
    assert (
        "endpoint clipping"
        in rows[("datoviz", "color/point_scalar_gray_range")]["known_adaptations"][1]
    )
    assert rows[("datoviz", "color/marker_scalar_fill_alpha")]["status"] == "strict"
    assert (
        "scalar fill alpha"
        in rows[("datoviz", "color/marker_scalar_fill_alpha")]["known_adaptations"][1]
    )
    assert rows[("datoviz", "text/basic_ndc")]["status"] == "adapted"
    assert rows[("datoviz", "text/basic_ndc")]["promotion_blockers"] == [
        "default BASELINE text-anchor semantics are not strictly verified by the Datoviz adapter"
    ]
    assert rows[("datoviz", "text/anchor_grid_ndc")]["status"] == "adapted"
    assert (
        "text-box anchors"
        in rows[("datoviz", "text/anchor_grid_ndc")]["promotion_blockers"][0]
    )
    assert rows[("datoviz", "text/rotation_alpha_ndc")]["status"] == "strict"
    assert rows[("datoviz", "text/rotation_alpha_ndc")]["query_supported"] is False
    assert rows[("datoviz", "text/rotation_alpha_ndc")]["promotion_blockers"] == []
    assert (
        "center-anchored rotation"
        in rows[("datoviz", "text/rotation_alpha_ndc")]["known_adaptations"][1]
    )
    assert rows[("datoviz", "text/data_vs_ndc")]["status"] == "adapted"
    assert (
        "identity [-1,+1]"
        in rows[("datoviz", "text/data_vs_ndc")]["promotion_blockers"][0]
    )
    assert rows[("datoviz", "text/multiline_unicode_smoke")]["status"] == "adapted"
    assert (
        "Unicode fallback"
        in rows[("datoviz", "text/multiline_unicode_smoke")]["promotion_blockers"][0]
    )
    assert (
        rows[("datoviz", "mesh/single_triangle_uniform_ndc_2d")]["status"] == "strict"
    )
    assert (
        rows[("datoviz", "mesh/single_triangle_uniform_ndc_2d")]["query_supported"]
        is False
    )
    assert (
        "z=0 adaptation"
        in rows[("datoviz", "mesh/single_triangle_uniform_ndc_2d")][
            "known_adaptations"
        ][0]
    )
    assert rows[("datoviz", "mesh/indexed_square_uniform_ndc_2d")]["status"] == "strict"
    assert (
        "shared-vertex"
        in rows[("datoviz", "mesh/indexed_square_uniform_ndc_2d")]["known_adaptations"][
            1
        ]
    )
    assert (
        rows[("datoviz", "mesh/indexed_square_per_face_ndc_2d")]["status"] == "strict"
    )
    assert (
        rows[("datoviz", "mesh/indexed_square_per_face_ndc_2d")]["query_supported"]
        is False
    )
    assert (
        "duplicating triangle vertices"
        in rows[("datoviz", "mesh/indexed_square_per_face_ndc_2d")][
            "known_adaptations"
        ][0]
    )
    assert rows[("datoviz", "transform/inline_named_equivalence")]["status"] == "strict"
    assert (
        rows[("datoviz", "transform/inline_named_equivalence")]["query_supported"]
        is False
    )
    assert (
        "inline and named AFFINE_2D"
        in rows[("datoviz", "transform/inline_named_equivalence")]["known_adaptations"][
            0
        ]
    )
    assert (
        rows[("datoviz", "transform/inline_named_equivalence")]["promotion_blockers"]
        == []
    )
    assert rows[("datoviz", "transform/view2d_data_ndc_overlay")]["status"] == "strict"
    assert (
        "reversed x limits"
        in rows[("datoviz", "transform/view2d_data_ndc_overlay")]["known_adaptations"][
            0
        ]
    )
    assert (
        rows[("datoviz", "transform/view2d_data_ndc_overlay")]["query_supported"]
        is False
    )
    assert rows[("datoviz", "transform/family_affine_view2d")]["status"] == "strict"
    assert (
        "point, marker, segment, path, text-center-anchor, and 2D uniform-mesh"
        in rows[("datoviz", "transform/family_affine_view2d")]["known_adaptations"][1]
    )
    assert (
        rows[("datoviz", "transform/family_affine_view2d")]["query_supported"] is False
    )


def test_s029_datoviz_guide_view2d_rows_stay_unsupported_with_specific_blockers() -> (
    None
):
    reason = (
        "axis_guide_render_unsupported: Datoviz v0.4 axis guides and panel text "
        "guides remain capability-gated until native axes, explicit tick labels, "
        "title placement, and guide query semantics are verified together"
    )
    report = {
        "suite": "s028",
        "stage": "S029",
        "run_id": "unit",
        "cases": [
            {
                "case_id": "guide/view2d_auto_grid",
                "family": "guide",
                "required_features": [
                    "guide",
                    "view2d",
                    "auto-ticks",
                    "grid",
                    "labels",
                ],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "unsupported", "reason": reason},
                },
            },
            {
                "case_id": "guide/view2d_reversed_explicit",
                "family": "guide",
                "required_features": [
                    "guide",
                    "view2d",
                    "reversed-limits",
                    "explicit-ticks",
                    "grid",
                    "labels",
                ],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "unsupported", "reason": reason},
                },
            },
            {
                "case_id": "guide/view2d_grid_clip_title_boundary",
                "family": "guide",
                "required_features": [
                    "guide",
                    "view2d",
                    "explicit-ticks",
                    "grid",
                    "plot-clip",
                    "title",
                ],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {"status": "unsupported", "reason": reason},
                },
            },
        ],
    }

    matrix = build_capability_matrix(report)
    rows = {
        row["case_id"]: row for row in matrix["rows"] if row["backend"] == "datoviz"
    }

    auto = rows["guide/view2d_auto_grid"]
    assert auto["status"] == "unsupported"
    assert auto["rendering_supported"] is False
    assert auto["query_supported"] is False
    assert auto["reason_code"] == "datoviz_axis_guide_contract_unverified"
    assert "backend auto ticks" in auto["known_missing_semantics"][0]
    assert "guide-query support" in auto["promotion_blockers"][1]

    reversed_explicit = rows["guide/view2d_reversed_explicit"]
    assert reversed_explicit["status"] == "unsupported"
    assert reversed_explicit["rendering_supported"] is False
    assert reversed_explicit["query_supported"] is False
    assert (
        "explicit GSP tick values and labels"
        in reversed_explicit["known_missing_semantics"][0]
    )
    assert (
        "reversed View2D axis/grid placement"
        in reversed_explicit["promotion_blockers"][1]
    )
    clip_boundary = rows["guide/view2d_grid_clip_title_boundary"]
    assert clip_boundary["status"] == "unsupported"
    assert "plot-rect grid clipping" in clip_boundary["known_missing_semantics"][0]
    assert "plot viewport and plot clip rect" in clip_boundary["promotion_blockers"][0]


def test_s030_rendered_datoviz_guide_rows_are_adapted_not_promoted() -> None:
    report = {
        "suite": "s028",
        "stage": "S030",
        "run_id": "unit",
        "cases": [
            {
                "case_id": "guide/view2d_auto_grid",
                "family": "guide",
                "required_features": [
                    "guide",
                    "view2d",
                    "auto-ticks",
                    "grid",
                    "labels",
                ],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {
                        "status": "rendered",
                        "artifact_path": "backends/datoviz/guide_view2d_auto_grid.png",
                        "log_path": "backends/datoviz/guide_view2d_auto_grid.log.txt",
                        "guide_diagnostics": {
                            "axis_rendering": "adapted-review",
                            "panel_title": "unsupported",
                            "guide_query": "unsupported",
                        },
                    },
                },
            },
            {
                "case_id": "guide/view2d_reversed_explicit",
                "family": "guide",
                "required_features": [
                    "guide",
                    "view2d",
                    "reversed-limits",
                    "explicit-ticks",
                    "grid",
                    "labels",
                ],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {
                        "status": "rendered",
                        "artifact_path": (
                            "backends/datoviz/guide_view2d_reversed_explicit.png"
                        ),
                        "log_path": (
                            "backends/datoviz/guide_view2d_reversed_explicit.log.txt"
                        ),
                        "guide_diagnostics": {
                            "axis_rendering": "adapted-review",
                            "explicit_ticks": (
                                "binding-dependent; dvz_axis_set_ticks when exposed, "
                                "backend-native ticks otherwise"
                            ),
                            "panel_title": "unsupported",
                            "guide_query": "unsupported",
                        },
                    },
                },
            },
            {
                "case_id": "guide/view2d_grid_clip_title_boundary",
                "family": "guide",
                "required_features": [
                    "guide",
                    "view2d",
                    "explicit-ticks",
                    "grid",
                    "plot-clip",
                    "title",
                ],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {
                        "status": "rendered",
                        "artifact_path": (
                            "backends/datoviz/"
                            "guide_view2d_grid_clip_title_boundary.png"
                        ),
                        "log_path": (
                            "backends/datoviz/"
                            "guide_view2d_grid_clip_title_boundary.log.txt"
                        ),
                        "guide_diagnostics": {
                            "axis_rendering": "adapted-review",
                            "grid_clip_to_plot_rect": "native-verified",
                            "grid_clip_evidence": (
                                "datoviz-native-axis-grid-plot-viewport-clip"
                            ),
                            "panel_title": "unsupported",
                            "guide_query": "unsupported",
                        },
                    },
                },
            },
        ],
    }

    matrix = build_capability_matrix(report)
    assert "review.adapted" in matrix["review_classification_taxonomy"]
    assert matrix["review_classification_summary"]["review.adapted"] == 3
    rows = {
        row["case_id"]: row for row in matrix["rows"] if row["backend"] == "datoviz"
    }

    auto = rows["guide/view2d_auto_grid"]
    assert auto["status"] == "adapted"
    assert auto["review_classification"] == "review.adapted"
    assert auto["rendering_supported"] is True
    assert auto["query_supported"] is False
    assert auto["reason_code"] == "datoviz_axis_guide_adapted_review"
    assert "backend-native auto ticks" in auto["known_adaptations"][0]
    assert "guide/all-rendered query" in auto["known_missing_semantics"][1]
    assert auto["evidence_artifacts"] == [
        "backends/datoviz/guide_view2d_auto_grid.png",
        "backends/datoviz/guide_view2d_auto_grid.log.txt",
    ]

    reversed_explicit = rows["guide/view2d_reversed_explicit"]
    assert reversed_explicit["status"] == "adapted"
    assert reversed_explicit["review_classification"] == "review.adapted"
    assert "dvz_axis_set_ticks" in reversed_explicit["known_adaptations"][0]
    assert "backend-native tick policy" in reversed_explicit["known_adaptations"][0]
    assert "guide-query support" in reversed_explicit["promotion_blockers"][1]

    clip_boundary = rows["guide/view2d_grid_clip_title_boundary"]
    assert clip_boundary["status"] == "adapted"
    assert clip_boundary["reason_code"] == "datoviz_axis_guide_adapted_review"
    assert "title-boundary grid clipping" in clip_boundary["known_adaptations"][0]
    assert "guide-query support" in clip_boundary["promotion_blockers"][1]


def test_s030_rendered_datoviz_guide_row_promotes_with_strict_snapshot_evidence() -> None:
    report = {
        "suite": "s028",
        "stage": "S043",
        "run_id": "unit",
        "cases": [
            {
                "case_id": "guide/view2d_auto_grid",
                "family": "guide",
                "required_features": ["guide", "view2d", "auto-ticks", "grid", "labels"],
                "backends": {
                    "matplotlib": {"status": "rendered"},
                    "datoviz": {
                        "status": "rendered",
                        "artifact_path": "backends/datoviz/guide_view2d_auto_grid.png",
                        "log_path": "backends/datoviz/guide_view2d_auto_grid.log.txt",
                        "guide_diagnostics": {
                            "axis_rendering": "native-verified",
                            "panel_title": "native-verified",
                            "guide_identity": "native-verified",
                            "guide_box": "native-verified",
                            "guide_query": "native-verified",
                            "all_rendered_guide_query": "native-verified",
                            "layout_snapshot_id_equality": "native-verified",
                            "rendered_contribution": "native-verified",
                            "rendered_contribution_count": 1,
                        },
                    },
                },
            }
        ],
    }

    matrix = build_capability_matrix(report)
    row = next(row for row in matrix["rows"] if row["backend"] == "datoviz")

    assert row["status"] == "strict"
    assert row["review_classification"] == "pass.semantic_strict"
    assert row["rendering_supported"] is True
    assert row["query_supported"] is True
    assert row["reason_code"] == "datoviz_axis_guide_strict_snapshot_evidence"
    assert row["known_missing_semantics"] == []
    assert row["promotion_blockers"] == []


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
        (tmp_path / "scenes" / "transform_family_affine_view2d.scene.json").read_text(
            encoding="utf-8"
        )
    )
    assert scene["transform_resources"][0]["id"] == "transform:s027-family-shear"
    assert scene["views"][0]["id"] == "view:s027-family"
    assert (
        scene["visuals"][0]["transform"]["ref"]["id"] == "transform:s027-family-shear"
    )
    for case in report["cases"]:
        assert case["backends"]["matplotlib"]["status"] == "rendered"


def test_s027_transform_query_fixture_reports_inverse_payload() -> None:
    """The S027 QA fixture supports strict transformed query inverse payloads."""
    scene = get_case("transform/inline_named_equivalence", suite=S027_SUITE).build()
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

    assert case_ids[-3:] == [
        "guide/view2d_auto_grid",
        "guide/view2d_reversed_explicit",
        "guide/view2d_grid_clip_title_boundary",
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
            "guide/view2d_grid_clip_title_boundary",
        ),
        run_id="test-s028-guides",
        resolution=(360, 240),
    )

    assert report["stage"] == "S028"
    assert (tmp_path / "contact_sheets" / "s028_all_cases.png").stat().st_size > 0
    scene = json.loads(
        (tmp_path / "scenes" / "guide_view2d_reversed_explicit.scene.json").read_text(
            encoding="utf-8"
        )
    )
    assert scene["views"][0]["x_range"] == [1.0, -1.0]
    assert scene["axis_guides"][0]["tick_spec"]["explicit_labels"] == [
        "right",
        "center",
        "left",
    ]
    assert scene["panel_text_guides"][0]["text"] == "S028 reversed guide View2D"
    assert scene["visuals"][0]["family"] == "point"
    clip_scene = json.loads(
        (
            tmp_path
            / "scenes"
            / "guide_view2d_grid_clip_title_boundary.scene.json"
        ).read_text(encoding="utf-8")
    )
    assert clip_scene["panel_text_guides"][0]["text"] == "S028 grid clip boundary"
    assert clip_scene["axis_guides"][0]["tick_spec"]["explicit_values"] == [
        -2.0,
        0.0,
        2.0,
    ]
    for case in report["cases"]:
        assert case["backends"]["matplotlib"]["status"] == "rendered"


def test_s028_matplotlib_guide_artifacts_keep_layout_inside_canvas(
    tmp_path: Path,
) -> None:
    """Guide title, ticks, and labels should not be clipped at image borders."""
    report = run_visual_qa_suite(
        suite=S028_SUITE,
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=("guide/view2d_auto_grid",),
        run_id="test-s028-guide-layout",
        resolution=(360, 240),
    )

    artifact_path = Path(
        str(report["cases"][0]["backends"]["matplotlib"]["artifact_path"])
    )
    image = np.asarray(mpimg.imread(artifact_path)[..., :3], dtype=np.float64)

    assert image.shape[:2] == (240, 360)
    assert image[0, :, :].mean() > 0.98
    assert image[-1, :, :].mean() > 0.98
    assert image[:, 0, :].mean() > 0.98
    assert image[:, -1, :].mean() > 0.98


def test_s028_datoviz_guide_path_configures_view2d_before_data_visuals(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Datoviz guide review rows must attach DATA points after native View2D setup."""
    captured: dict[str, Any] = {}

    class FakeDatovizRenderer:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            captured["view"] = kwargs["view"]
            captured["events"] = []
            captured["point_positions"] = []

        def __enter__(self) -> "FakeDatovizRenderer":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def add_point_visual(self, visual: Any) -> None:
            captured["events"].append("add_point")
            positions = np.asarray(visual.positions, dtype=np.float64)
            captured["point_positions"].append(positions)

        def add_text_visual(self, visual: Any) -> None:
            captured["events"].append("add_text")
            captured["title_text"] = tuple(visual.texts)
            captured["title_positions"] = np.asarray(visual.positions, dtype=np.float64)

        def configure_view2d_axes(self, view: Any, **kwargs: Any) -> None:
            captured["events"].append("configure_axes")
            captured["axis_view"] = view

        def capture_png_bytes(self) -> bytes:
            return b"fake-png"

    monkeypatch.setattr(
        visual_runner, "probe_datoviz_v04", _supported_datoviz_probe_report
    )
    monkeypatch.setattr(
        visual_runner, "DatovizV04ProtocolRenderer", FakeDatovizRenderer
    )
    monkeypatch.setenv(visual_runner.DATOVIZ_QA_OFFSCREEN_ENV, "1")

    report = run_visual_qa_suite(
        suite=S028_SUITE,
        out_dir=tmp_path,
        backends=("datoviz",),
        case_ids=("guide/view2d_auto_grid",),
        contact_sheet=False,
        run_id="test-s028-dataviz-guide-view",
        resolution=(96, 96),
    )

    assert report["cases"][0]["backends"]["datoviz"]["status"] == "rendered"
    diagnostics = report["cases"][0]["backends"]["datoviz"]["guide_diagnostics"]
    assert diagnostics["panel_title"] == "adapted-review"
    assert diagnostics["panel_text_adapter"] == "datoviz.ndc_text_visual"
    assert (
        diagnostics["datoviz_view2d_carrier"]
        == "dvz_panel_set_domain+DvzPanelView2D policy"
    )
    assert diagnostics["ordered_ranges_preserved"] is True
    assert diagnostics["legacy_panel_domain_sync"] == "compat-before-dvz_panel_set_view2d"
    assert diagnostics["grid_clip_to_plot_rect"] == "unsupported"
    assert diagnostics["grid_clip_blockers"] == [
        "grid_clip_not_enforced",
        "grid_clip_native_api_unverified",
    ]
    assert captured["view"] is None
    assert captured["axis_view"].x_range == (-2.0, 2.0)
    assert captured["axis_view"].y_range == (-1.0, 1.0)
    assert captured["events"] == ["configure_axes", "add_point", "add_text"]
    assert captured["title_text"] == ("S028 auto guide View2D",)
    np.testing.assert_allclose(captured["title_positions"], [[0.0, 0.92]])
    np.testing.assert_allclose(
        captured["point_positions"][0],
        np.array(
            [
                [-1.5, -0.5],
                [-0.5, 0.45],
                [0.5, -0.15],
                [1.5, 0.65],
            ]
        ),
        atol=1e-6,
    )


def test_s028_datoviz_guide_diagnostics_report_native_grid_clip_when_source_is_fixed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_datoviz_grid_clip_source(tmp_path)

    class FakeDatovizRenderer:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> "FakeDatovizRenderer":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def add_point_visual(self, visual: Any) -> None:
            pass

        def add_text_visual(self, visual: Any) -> None:
            pass

        def configure_view2d_axes(self, view: Any, **kwargs: Any) -> None:
            pass

        def capture_png_bytes(self) -> bytes:
            return b"fake-png"

    monkeypatch.setattr(
        visual_runner,
        "probe_datoviz_v04",
        lambda: _supported_datoviz_probe_report(source),
    )
    monkeypatch.setattr(
        visual_runner, "DatovizV04ProtocolRenderer", FakeDatovizRenderer
    )
    monkeypatch.setenv(visual_runner.DATOVIZ_QA_OFFSCREEN_ENV, "1")

    report = run_visual_qa_suite(
        suite=S028_SUITE,
        out_dir=tmp_path,
        backends=("datoviz",),
        case_ids=("guide/view2d_auto_grid",),
        contact_sheet=False,
        run_id="test-s028-dataviz-guide-grid-clip",
        resolution=(96, 96),
    )

    diagnostics = report["cases"][0]["backends"]["datoviz"]["guide_diagnostics"]
    assert diagnostics["grid_clip_to_plot_rect"] == "native-verified"
    assert diagnostics["grid_clip_evidence"] == "datoviz-native-axis-grid-plot-viewport-clip"
    assert "grid_clip_blockers" not in diagnostics


def test_s034_case_registry_extends_s028_with_layout_cases() -> None:
    """S034 adds resolved-layout QA cases after S028 guide/View2D cases."""
    case_ids = [case.case_id for case in list_cases(suite=S034_SUITE)]

    assert case_ids[-2:] == [
        "layout/scatter_title_axes_grid",
        "layout/reversed_explicit_tick_boxes",
    ]


def test_s034_layout_visual_qa_run_reports_matplotlib_layout_snapshots(
    tmp_path: Path,
) -> None:
    """S034 Matplotlib QA rows expose the resolved layout snapshot used by rendering."""
    report = run_visual_qa_suite(
        suite=S034_SUITE,
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=(
            "layout/scatter_title_axes_grid",
            "layout/reversed_explicit_tick_boxes",
        ),
        run_id="test-s034-layout",
        resolution=(360, 240),
    )

    assert report["stage"] == "S034"
    assert (tmp_path / "contact_sheets" / "s034_all_cases.png").stat().st_size > 0
    scene = json.loads(
        (tmp_path / "scenes" / "layout_scatter_title_axes_grid.scene.json").read_text(
            encoding="utf-8"
        )
    )
    assert scene["views"][0]["x_range"] == [-2.5, 2.5]
    assert scene["axis_guides"][0]["style"]["tick_label_font_size_px"] == 12.0
    assert scene["panel_text_guides"][0]["style"]["title_font_size_px"] == 18.0

    for case in report["cases"]:
        backend = case["backends"]["matplotlib"]
        assert backend["status"] == "rendered"
        assert backend["layout_snapshot_id"].startswith("layout:")
        snapshot = backend["layout_snapshot"]
        assert snapshot["snapshot_id"] == backend["layout_snapshot_id"]
        assert snapshot["plot_rect_px"]["width"] > 0.0
        assert snapshot["grid_clip_rect_px"] == snapshot["plot_rect_px"]
        assert snapshot["title_boxes"][0]["kind"] == "title"
        assert len(snapshot["axis_label_boxes"]) == 2
        assert snapshot["tick_label_box_count"] > 0


def test_s034_layout_snapshots_track_resized_viewports(tmp_path: Path) -> None:
    """Resolved layout snapshot metadata follows the Matplotlib render target size."""
    small = run_visual_qa_suite(
        suite=S034_SUITE,
        out_dir=tmp_path / "small",
        backends=("matplotlib",),
        case_ids=("layout/scatter_title_axes_grid",),
        contact_sheet=False,
        run_id="test-s034-layout-small",
        resolution=(320, 220),
    )
    large = run_visual_qa_suite(
        suite=S034_SUITE,
        out_dir=tmp_path / "large",
        backends=("matplotlib",),
        case_ids=("layout/scatter_title_axes_grid",),
        contact_sheet=False,
        run_id="test-s034-layout-large",
        resolution=(640, 360),
    )

    small_snapshot = small["cases"][0]["backends"]["matplotlib"]["layout_snapshot"]
    large_snapshot = large["cases"][0]["backends"]["matplotlib"]["layout_snapshot"]

    assert small_snapshot["render_target"]["logical_width_px"] == pytest.approx(320.0)
    assert small_snapshot["render_target"]["logical_height_px"] == pytest.approx(220.0)
    assert large_snapshot["render_target"]["logical_width_px"] == pytest.approx(640.0)
    assert large_snapshot["render_target"]["logical_height_px"] == pytest.approx(360.0)
    assert large_snapshot["plot_rect_px"]["width"] > small_snapshot["plot_rect_px"]["width"]
    assert large_snapshot["plot_rect_px"]["height"] > small_snapshot["plot_rect_px"]["height"]
    assert small_snapshot["grid_clip_rect_px"] == small_snapshot["plot_rect_px"]
    assert large_snapshot["grid_clip_rect_px"] == large_snapshot["plot_rect_px"]


def test_s034_layout_snapshot_reports_device_scale(tmp_path: Path) -> None:
    """S034 layout QA preserves logical size while reporting physical scale metadata."""
    report = run_visual_qa_suite(
        suite=S034_SUITE,
        out_dir=tmp_path,
        backends=("matplotlib",),
        case_ids=("layout/scatter_title_axes_grid",),
        contact_sheet=False,
        run_id="test-s034-device-scale",
        resolution=(320, 220),
        device_scale=2.0,
    )

    backend = report["cases"][0]["backends"]["matplotlib"]
    snapshot = backend["layout_snapshot"]
    target = snapshot["render_target"]

    assert report["device_scale"] == 2.0
    assert target["logical_width_px"] == pytest.approx(320.0)
    assert target["logical_height_px"] == pytest.approx(220.0)
    assert target["device_scale"] == pytest.approx(2.0)
    assert target["framebuffer_width_px"] == 640
    assert target["framebuffer_height_px"] == 440
    assert snapshot["grid_clip_rect_px"] == snapshot["plot_rect_px"]


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


def _supported_datoviz_probe_report(
    source_path: Path | None = None,
) -> DatovizV04ProbeReport:
    return DatovizV04ProbeReport(
        installed_package={},
        sibling_source={} if source_path is None else {"path": str(source_path)},
        imports={
            "datoviz": ImportProbe(
                module="datoviz",
                imported=True,
                path=None,
                error_type=None,
                error_message=None,
                traceback=None,
            ),
            "datoviz.raw": ImportProbe(
                module="datoviz.raw",
                imported=True,
                path=None,
                error_type=None,
                error_message=None,
                traceback=None,
            ),
        },
        generated_files={},
        facade_symbols={},
        raw_symbols={},
        capability_matrix={},
        enum_style_symbols={},
        text_symbols={},
        text_capability_matrix={},
        mesh_symbols={},
        mesh_capability_matrix={},
        color_mapping_symbols={},
        color_mapping_capability_matrix={},
        source_symbol_matrix={},
        minimal_point_scene=MinimalPointProbe(
            attempted=True,
            supported=True,
            reason=None,
            calls_completed=("fake",),
        ),
        capture={},
        banned_symbol_check={},
    )


def _write_datoviz_grid_clip_source(root: Path) -> Path:
    source = root / "datoviz-source"
    (source / "datoviz").mkdir(parents=True)
    (source / "datoviz" / "__init__.py").write_text("", encoding="utf-8")
    axis_visual = source / "src" / "scene" / "annotation" / "axis_visual.c"
    axis_visual.parent.mkdir(parents=True)
    axis_visual.write_text(
        "\n".join(
            (
                "source_x0 = _axis_inverse_panzoom_coord(extent, 0, 1, -1.0f);",
                "source_x1 = _axis_inverse_panzoom_coord(extent, 0, 1, +1.0f);",
                "source_y0 = _axis_inverse_panzoom_coord(extent, 2, 3, -1.0f);",
                "source_y1 = _axis_inverse_panzoom_coord(extent, 2, 3, +1.0f);",
            )
        ),
        encoding="utf-8",
    )
    axis_tests = source / "src" / "scene" / "tests" / "axis.c"
    axis_tests.parent.mkdir(parents=True)
    axis_tests.write_text(
        "test_axis_grid_style_margins_do_not_double_clip", encoding="utf-8"
    )
    return source
