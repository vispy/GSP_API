"""Review-pack generation for post-S028 visual QA."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from gsp.qa.visual.capability_matrix import (
    write_capability_matrix,
    write_review_pack_index,
)
from gsp.qa.visual.cases import S028_SUITE
from gsp.qa.visual.runner import DATOVIZ_QA_OFFSCREEN_ENV, run_visual_qa_suite
from gsp_datoviz.protocol_renderer import DatovizColorPipeline


ReviewPackMode = Literal[
    "side-by-side",
    "matplotlib-only",
    "datoviz-diagnostic",
    "datoviz-offscreen-opt-in",
]


def run_visual_review_pack(
    *,
    out_dir: Path,
    suite: str = S028_SUITE,
    mode: ReviewPackMode = "side-by-side",
    case_ids: tuple[str, ...] = (),
    resolution: tuple[int, int] = (800, 600),
    run_id: str | None = None,
    datoviz_color_pipeline: DatovizColorPipeline = "legacy_srgb_blend",
) -> dict[str, object]:
    """Run visual QA and write review-pack matrix artifacts."""
    backends: tuple[str, ...]
    if mode == "matplotlib-only":
        backends = ("matplotlib",)
    elif mode == "datoviz-diagnostic":
        backends = ("matplotlib", "datoviz")
        os.environ.pop(DATOVIZ_QA_OFFSCREEN_ENV, None)
    elif mode == "datoviz-offscreen-opt-in":
        backends = ("matplotlib", "datoviz")
        os.environ[DATOVIZ_QA_OFFSCREEN_ENV] = "1"
    elif mode == "side-by-side":
        backends = ("matplotlib", "datoviz")
    else:
        raise ValueError(f"unknown visual review-pack mode: {mode}")

    report = run_visual_qa_suite(
        suite=suite,
        out_dir=out_dir,
        backends=backends,
        case_ids=case_ids,
        contact_sheet=True,
        run_id=run_id,
        resolution=resolution,
        datoviz_color_pipeline=datoviz_color_pipeline,
    )
    matrix = write_capability_matrix(out_dir, report)
    write_review_pack_index(out_dir, report, matrix)
    return {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.review_pack",
        "out_dir": str(out_dir),
        "report_path": str(out_dir / "report.json"),
        "capability_matrix_path": str(out_dir / "capability_matrix.json"),
        "index_path": str(out_dir / "index.md"),
        "summary_path": str(out_dir / "summary.json"),
        "report": report,
        "capability_matrix": matrix,
    }
