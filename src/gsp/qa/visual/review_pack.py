"""Review-pack generation for post-S028 visual QA."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Literal

from gsp.qa.visual.artifacts import write_json, write_summary
from gsp.qa.visual.capability_matrix import (
    write_capability_matrix,
    write_review_pack_index,
)
from gsp.qa.visual.cases import S028_SUITE, case_slug
from gsp.qa.visual.contact_sheet import write_contact_sheets
from gsp.qa.visual.backend_ids import DATOVIZ_BACKEND_ID, MATPLOTLIB_BACKEND_ID
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
        return _run_isolated_datoviz_offscreen_review_pack(
            suite=suite,
            out_dir=out_dir,
            case_ids=case_ids,
            resolution=resolution,
            run_id=run_id,
            datoviz_color_pipeline=datoviz_color_pipeline,
        )
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


def _run_isolated_datoviz_offscreen_review_pack(
    *,
    suite: str,
    out_dir: Path,
    case_ids: tuple[str, ...],
    resolution: tuple[int, int],
    run_id: str | None,
    datoviz_color_pipeline: DatovizColorPipeline,
) -> dict[str, object]:
    """Run Datoviz offscreen QA in a child process so native crashes are reportable."""
    report = run_visual_qa_suite(
        suite=suite,
        out_dir=out_dir,
        backends=(MATPLOTLIB_BACKEND_ID,),
        case_ids=case_ids,
        contact_sheet=False,
        run_id=run_id,
        resolution=resolution,
        datoviz_color_pipeline=datoviz_color_pipeline,
    )
    child_out_dir = out_dir / "_datoviz_offscreen_child"
    if child_out_dir.exists():
        shutil.rmtree(child_out_dir)
    completed = _run_datoviz_child(
        suite=suite,
        out_dir=child_out_dir,
        case_ids=case_ids,
        resolution=resolution,
        run_id=run_id,
        datoviz_color_pipeline=datoviz_color_pipeline,
    )
    if completed.returncode == 0 and (child_out_dir / "report.json").exists():
        _merge_successful_datoviz_child_report(report, out_dir, child_out_dir)
        shutil.rmtree(child_out_dir, ignore_errors=True)
    else:
        _merge_crashed_datoviz_child_report(
            report,
            out_dir,
            child_out_dir=child_out_dir,
            completed=completed,
        )
        shutil.rmtree(child_out_dir, ignore_errors=True)

    contact_paths = write_contact_sheets(
        out_dir,
        report["cases"],  # type: ignore[arg-type]
        (MATPLOTLIB_BACKEND_ID, DATOVIZ_BACKEND_ID),
        suite=suite,
    )
    report["contact_sheets"] = [str(path) for path in contact_paths]
    report["datoviz_offscreen_isolated"] = True
    write_json(out_dir / "report.json", report)
    write_summary(out_dir, report)
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


def _run_datoviz_child(
    *,
    suite: str,
    out_dir: Path,
    case_ids: tuple[str, ...],
    resolution: tuple[int, int],
    run_id: str | None,
    datoviz_color_pipeline: DatovizColorPipeline,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-m",
        "gsp.qa.visual",
        "run",
        "--suite",
        suite,
        "--backends",
        DATOVIZ_BACKEND_ID,
        "--out",
        str(out_dir),
        "--no-contact-sheet",
        "--resolution",
        f"{resolution[0]}x{resolution[1]}",
        "--datoviz-color-pipeline",
        datoviz_color_pipeline,
    ]
    for case_id in case_ids:
        command.extend(["--case", case_id])
    if run_id is not None:
        command.extend(["--run-id", run_id])
    env = os.environ.copy()
    env[DATOVIZ_QA_OFFSCREEN_ENV] = "1"
    return subprocess.run(
        command,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _merge_successful_datoviz_child_report(
    report: dict[str, object], out_dir: Path, child_out_dir: Path
) -> None:
    child_report = json.loads((child_out_dir / "report.json").read_text(encoding="utf-8"))
    child_cases = {
        str(case["case_id"]): case
        for case in child_report.get("cases", [])
        if isinstance(case, dict)
    }
    cases = report.get("cases", [])
    if not isinstance(cases, list):
        raise TypeError("visual QA report cases must be a list")
    for case in cases:
        if not isinstance(case, dict):
            continue
        case_id = str(case["case_id"])
        child_case = child_cases.get(case_id)
        backends = case.get("backends")
        if not isinstance(backends, dict):
            continue
        if child_case is None:
            backends[DATOVIZ_BACKEND_ID] = _write_datoviz_child_missing_entry(
                out_dir, case_id
            )
            continue
        child_backends = child_case.get("backends")
        if not isinstance(child_backends, dict):
            backends[DATOVIZ_BACKEND_ID] = _write_datoviz_child_missing_entry(
                out_dir, case_id
            )
            continue
        child_entry = child_backends.get(DATOVIZ_BACKEND_ID)
        if not isinstance(child_entry, dict):
            backends[DATOVIZ_BACKEND_ID] = _write_datoviz_child_missing_entry(
                out_dir, case_id
            )
            continue
        backends[DATOVIZ_BACKEND_ID] = _copy_datoviz_backend_entry(
            child_entry, out_dir=out_dir, child_out_dir=child_out_dir
        )


def _copy_datoviz_backend_entry(
    child_entry: dict[str, object], *, out_dir: Path, child_out_dir: Path
) -> dict[str, object]:
    copied = dict(child_entry)
    for key in ("artifact_path", "unsupported_path", "log_path"):
        value = copied.get(key)
        if not isinstance(value, str):
            continue
        source = Path(value)
        if not source.exists():
            continue
        try:
            relative = source.relative_to(child_out_dir)
        except ValueError:
            relative = Path("backends") / DATOVIZ_BACKEND_ID / source.name
        destination = out_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied[key] = str(destination)
    return copied


def _merge_crashed_datoviz_child_report(
    report: dict[str, object],
    out_dir: Path,
    *,
    child_out_dir: Path,
    completed: subprocess.CompletedProcess[str],
) -> None:
    cases = report.get("cases", [])
    if not isinstance(cases, list):
        raise TypeError("visual QA report cases must be a list")
    for case in cases:
        if not isinstance(case, dict):
            continue
        backends = case.get("backends")
        if not isinstance(backends, dict):
            continue
        case_id = str(case["case_id"])
        backends[DATOVIZ_BACKEND_ID] = _write_datoviz_child_crash_entry(
            out_dir,
            case_id,
            child_out_dir=child_out_dir,
            completed=completed,
        )


def _write_datoviz_child_missing_entry(out_dir: Path, case_id: str) -> dict[str, object]:
    slug = case_slug(case_id)
    backend_dir = out_dir / "backends" / DATOVIZ_BACKEND_ID
    backend_dir.mkdir(parents=True, exist_ok=True)
    crash_path = backend_dir / f"{slug}.child_missing.json"
    log_path = backend_dir / f"{slug}.child_missing.log.txt"
    reason = "Datoviz child process completed but did not report this case"
    payload = {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.datoviz_child_missing",
        "backend_id": DATOVIZ_BACKEND_ID,
        "case_id": case_id,
        "status": "error",
        "reason": reason,
    }
    write_json(crash_path, payload)
    log_path.write_text(reason + "\n", encoding="utf-8")
    return {
        "backend_id": DATOVIZ_BACKEND_ID,
        "status": "error",
        "reason": reason,
        "unsupported_path": str(crash_path),
        "log_path": str(log_path),
    }


def _write_datoviz_child_crash_entry(
    out_dir: Path,
    case_id: str,
    *,
    child_out_dir: Path,
    completed: subprocess.CompletedProcess[str],
) -> dict[str, object]:
    slug = case_slug(case_id)
    backend_dir = out_dir / "backends" / DATOVIZ_BACKEND_ID
    backend_dir.mkdir(parents=True, exist_ok=True)
    crash_path = backend_dir / f"{slug}.native_crash.json"
    log_path = backend_dir / f"{slug}.native_crash.log.txt"
    reason = _datoviz_child_failure_reason(completed.returncode)
    command = completed.args if isinstance(completed.args, list) else [completed.args]
    payload = {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.datoviz_native_crash",
        "backend_id": DATOVIZ_BACKEND_ID,
        "case_id": case_id,
        "status": "error",
        "reason": reason,
        "returncode": completed.returncode,
        "command": [str(part) for part in command],
        "child_out_dir": str(child_out_dir),
        "partial_artifacts_discarded": True,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    write_json(crash_path, payload)
    log_path.write_text(
        "\n".join(
            [
                reason,
                "",
                "Command:",
                " ".join(str(part) for part in command),
                "",
                "stdout:",
                completed.stdout or "",
                "",
                "stderr:",
                completed.stderr or "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "backend_id": DATOVIZ_BACKEND_ID,
        "status": "error",
        "reason": reason,
        "unsupported_path": str(crash_path),
        "log_path": str(log_path),
    }


def _datoviz_child_failure_reason(returncode: int) -> str:
    if returncode < 0:
        return f"Datoviz offscreen child process terminated by signal {-returncode}"
    return f"Datoviz offscreen child process exited with code {returncode}"
