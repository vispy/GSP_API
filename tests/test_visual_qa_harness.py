"""Tests for the S023 visual QA harness."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.image as mpimg

from gsp.qa.visual.cases import list_cases
from gsp.qa.visual.runner import run_visual_qa_suite


def test_s023_case_registry_lists_initial_cases() -> None:
    """The harness starts with the approved Point/Image smoke cases."""
    case_ids = [case.case_id for case in list_cases()]

    assert case_ids == [
        "point/basic_ndc",
        "point/diameter_ramp_ndc",
        "point/alpha_overlap_ndc",
        "marker/shapes_ndc",
        "marker/angle_size_stroke_ndc",
        "image/checker_nearest_ndc",
        "overlay/point_over_image_ndc",
    ]


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
    assert payload["datoviz_probe_summary"]["facade_imported"] is True


def test_visual_qa_datoviz_backend_reports_rendered_or_unsupported(tmp_path: Path) -> None:
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
    if backend["status"] == "rendered":
        assert Path(str(backend["artifact_path"])).stat().st_size > 0
        assert "backends/datoviz/" in str(backend["artifact_path"])
    else:
        unsupported_path = Path(str(backend["unsupported_path"]))
        payload = json.loads(unsupported_path.read_text(encoding="utf-8"))
        assert payload["schema_kind"] == "gsp.visual_qa.unsupported"
        assert payload["backend_id"] == "datoviz"
        assert payload["case_id"] == "point/basic_ndc"


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


def test_visual_qa_harness_does_not_import_legacy_datoviz_renderer() -> None:
    """The S023 harness uses the v0.4 protocol renderer, not the legacy renderer package."""
    source_root = Path("src/gsp/qa/visual")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in source_root.glob("*.py"))

    assert "gsp_datoviz.renderer" not in combined
