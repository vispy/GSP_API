"""Internal S051 acceptance bridge from public VisPy2 producers to visual QA."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
import hashlib
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import numpy.typing as npt

from gsp.qa.visual.case_spec import VisualQACase, VisualQAScene
from gsp.qa.visual.artifacts import write_json
from gsp.qa.visual.datoviz_probe import probe_datoviz_v04
from gsp_vispy2 import Figure, subplots


S051_SUITE = "s051"
S051_PRODUCER_API_VERSION = "experimental-rc1"
GSP_SCENE_SCHEMA_VERSION = 1
S052_LIFECYCLE_CASE_IDS = (
    "vispy2/primitives",
    "vispy2/text",
    "vispy2/mesh",
)


def figure_to_visual_qa_scene(
    figure: Figure, *, case_id: str, notes: tuple[str, ...] = ()
) -> VisualQAScene:
    """Lower producer state to the accepted in-memory QA scene model.

    This private bridge deliberately performs no JSON/base64 conversion.  The returned
    scene retains the exact protocol records and ndarray objects emitted by VisPy2.
    """
    visuals = figure.visuals()
    arrays: dict[str, npt.NDArray[Any]] = {}
    for record in (
        *visuals,
        *figure.color_scales(),
        *figure.texture_resources(),
    ):
        _collect_arrays(record, prefix=str(getattr(record, "id", "record")), out=arrays)
    return VisualQAScene(
        case_id=case_id,
        visuals=visuals,
        arrays=arrays,
        axis_guides=figure.axis_guides(),
        panel_text_guides=figure.panel_text_guides(),
        color_scales=figure.color_scales(),
        colorbar_guides=figure.colorbar_guides(),
        texture_resources=figure.texture_resources(),
        views=figure.views(),
        notes=notes,
    )


def s051_cases() -> tuple[VisualQACase, ...]:
    """Return the bounded public-producer acceptance matrix."""
    return (
        VisualQACase("vispy2/primitives", "VisPy2 primitive families", "producer", (
            "point", "marker", "segment", "path", "view2d", "guides"), _primitives),
        VisualQACase("vispy2/scalar_image_colorbar", "VisPy2 scalar image and colorbar", "producer", (
            "image", "scalar-color", "colorbar", "guides"), _scalar_image_colorbar),
        VisualQACase("vispy2/text", "VisPy2 text", "producer", ("text", "guides"), _text),
        VisualQACase("vispy2/mesh", "VisPy2 untextured mesh", "producer", ("mesh", "view2d"), _mesh),
        VisualQACase("vispy2/texture2d_boundary", "VisPy2 Texture2D boundary", "producer", (
            "mesh", "texture2d-unlit", "unsupported-boundary"), _texture2d),
    )


def write_s051_acceptance_manifest(out_dir: Path) -> Path:
    """Write the version/evidence manifest for a completed isolated S051 pack."""
    report = _read_json(out_dir / "report.json")
    matrix = _read_json(out_dir / "capability_matrix.json")
    rows = matrix.get("rows", [])
    outcomes: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        raw = str(row.get("status"))
        outcome = {
            "strict": "strict", "adapted": "adapted", "disabled": "deactivated",
            "unsupported": "unsupported", "crashed": "backend_failure",
            "error": "backend_failure", "not_run": "backend_failure",
        }.get(raw, "backend_failure")
        case_id = str(row.get("case_id"))
        if case_id == "vispy2/texture2d_boundary" and raw == "not_run":
            outcome = "unsupported"
        outcomes.append({
            "case_id": case_id, "backend": row.get("backend"), "outcome": outcome,
            "raw_status": raw, "diagnostic_code": row.get("reason_code"),
            "semantic_record_ids": _scene_record_ids(out_dir, case_id),
        })
    artifacts = {
        str(path.relative_to(out_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(out_dir.rglob("*"))
        if path.is_file() and path.name != "acceptance_manifest.json"
    }
    probe = report.get("datoviz_probe_summary", {})
    datoviz_evidence = dict(probe) if isinstance(probe, dict) else {}
    installed = datoviz_evidence.get("installed_package")
    if isinstance(installed, dict) and isinstance(installed.get("path"), str):
        datoviz_evidence.update(_git_evidence(Path(str(installed["path"]))))
    payload: dict[str, object] = {
        "schema_kind": "gsp.s051.vispy2_rc1_acceptance_manifest",
        "schema_version": 1,
        "producer": {"import": "gsp_vispy2", "api_version": S051_PRODUCER_API_VERSION},
        "gsp_scene_schema_version": GSP_SCENE_SCHEMA_VERSION,
        "backends": ["matplotlib", "datoviz"],
        "datoviz_evidence": datoviz_evidence,
        "capability_snapshot": probe,
        "platform": platform.platform(),
        "local_execution_encoding": "inproc-python-records-and-ndarray",
        "replay_encoding": "debug-json-plus-npz-sidecars",
        "outcomes": outcomes,
        "artifact_sha256": artifacts,
    }
    path = out_dir / "acceptance_manifest.json"
    write_json(path, payload)
    return path


def run_s052_lifecycle_probe(
    out_dir: Path,
    *,
    iterations: int = 5,
    timeout_seconds: float = 45.0,
) -> Path:
    """Repeat isolated Datoviz create/capture/report/close cycles for S051 scenes."""
    if iterations < 1:
        raise ValueError("iterations must be positive")
    results: list[dict[str, object]] = []
    clean_exit_count = 0
    complete_report_count = 0
    complete_artifact_count = 0
    env = os.environ.copy()
    env["GSP_DATOVIZ_QA_ENABLE_OFFSCREEN"] = "1"
    env.setdefault("PYTHONPATH", "src")
    for case_id in S052_LIFECYCLE_CASE_IDS:
        slug = case_id.replace("/", "_")
        for iteration in range(1, iterations + 1):
            iteration_dir = out_dir / "iterations" / slug / f"{iteration:02d}"
            command = [
                sys.executable,
                "-m",
                "gsp.qa.visual",
                "run",
                "--suite",
                S051_SUITE,
                "--backends",
                "datoviz",
                "--out",
                str(iteration_dir),
                "--no-contact-sheet",
                "--case",
                case_id,
                "--run-id",
                f"s052-lifecycle-{slug}-{iteration:02d}",
            ]
            try:
                completed = subprocess.run(
                    command,
                    env=env,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=timeout_seconds,
                )
                returncode = completed.returncode
                stdout = completed.stdout
                stderr = completed.stderr
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                returncode = 124
                stdout = str(exc.stdout or "")
                stderr = str(exc.stderr or "")
                timed_out = True
            report_path = iteration_dir / "report.json"
            artifact_path = (
                iteration_dir / "backends" / "datoviz" / f"{slug}.png"
            )
            report_complete = report_path.is_file()
            artifact_complete = artifact_path.is_file()
            clean_exit_count += int(returncode == 0)
            complete_report_count += int(report_complete)
            complete_artifact_count += int(artifact_complete)
            results.append(
                {
                    "case_id": case_id,
                    "iteration": iteration,
                    "returncode": returncode,
                    "timed_out": timed_out,
                    "report_complete": report_complete,
                    "artifact_complete": artifact_complete,
                    "phase": "closed" if returncode == 0 else "native_or_teardown_failure",
                    "stdout": stdout,
                    "stderr": stderr,
                }
            )
    probe = probe_datoviz_v04()
    installed = probe.installed_package
    datoviz_evidence: dict[str, object] = dict(installed)
    installed_path = installed.get("path")
    if isinstance(installed_path, str):
        datoviz_evidence.update(_git_evidence(Path(installed_path)))
    payload = {
        "schema_kind": "gsp.s052.datoviz_lifecycle_probe",
        "schema_version": 1,
        "iterations_per_case": iterations,
        "cases": list(S052_LIFECYCLE_CASE_IDS),
        "datoviz_evidence": datoviz_evidence,
        "results": results,
        "summary": {
            "attempted": len(results),
            "clean_exit": clean_exit_count,
            "complete_report": complete_report_count,
            "complete_artifact": complete_artifact_count,
        },
    }
    path = out_dir / "lifecycle_probe.json"
    write_json(path, payload)
    return path


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _scene_record_ids(out_dir: Path, case_id: str) -> list[str]:
    slug = case_id.replace("/", "_")
    scene = _read_json(out_dir / "scenes" / f"{slug}.scene.json")
    visuals = scene.get("visuals", [])
    if not isinstance(visuals, list):
        raise TypeError("scene visuals must be a list")
    return [str(value["id"]) for value in visuals if isinstance(value, dict) and "id" in value]


def _git_evidence(installed_file: Path) -> dict[str, object]:
    repo = installed_file.parent.parent
    try:
        revision = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "-C", str(repo), "branch", "--show-current"], check=True,
            capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return {"git_path": str(repo), "git_revision": None, "git_branch": None}
    return {"git_path": str(repo), "git_revision": revision, "git_branch": branch}


def _collect_arrays(
    value: object, *, prefix: str, out: dict[str, npt.NDArray[Any]]
) -> None:
    if isinstance(value, np.ndarray):
        out[prefix.replace(":", "_").replace(".", "_")] = value
        return
    if not is_dataclass(value):
        return
    for item in fields(value):
        child: Any = getattr(value, item.name)
        if isinstance(child, np.ndarray):
            _collect_arrays(child, prefix=f"{prefix}_{item.name}", out=out)


def _primitives() -> VisualQAScene:
    fig, ax = subplots()
    ax.set_view2d(xlim=(-1.0, 1.0), ylim=(-1.0, 1.0))
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_title("public primitives")
    ax.scatter([-0.75, -0.5], [0.6, 0.3], color=(40, 100, 220, 255), size=10, id="s051:point")
    ax.markers([-0.2, 0.1], [0.5, 0.2], shape="triangle", fill_color=(220, 80, 80, 255), size=14, id="s051:marker")
    ax.segments([[-0.8, -0.2]], [[-0.2, -0.5]], color=(40, 160, 80, 255), width=4, id="s051:segment")
    ax.plot([0.2, 0.5, 0.8], [-0.5, -0.1, -0.4], color=(120, 60, 180, 255), width=3, id="s051:path")
    return figure_to_visual_qa_scene(fig, case_id="vispy2/primitives")


def _scalar_image_colorbar() -> VisualQAScene:
    fig, ax = subplots()
    image = np.arange(16, dtype=np.float32).reshape(4, 4)
    visual = ax.imshow(image, cmap="viridis", clim=(0.0, 15.0), id="s051:image")
    ax.colorbar(fig.color_scales()[0], label="value", linked_visual_ids=(visual.id,))
    return figure_to_visual_qa_scene(fig, case_id="vispy2/scalar_image_colorbar",
        notes=("Known pre-RC Datoviz colorbar/guide crash boundary must remain isolated.",))


def _text() -> VisualQAScene:
    fig, ax = subplots()
    ax.text([0.0], [0.0], ["VisPy2 α"], color=(20, 20, 20, 255),
            anchor_x="center", rotation_rad=0.2, id="s051:text")
    return figure_to_visual_qa_scene(fig, case_id="vispy2/text",
        notes=("Text adaptations must carry diagnostics and may not be silent.",))


def _mesh() -> VisualQAScene:
    fig, ax = subplots()
    ax.mesh([[-0.7, -0.6], [0.7, -0.6], [0.0, 0.7]], [[0, 1, 2]],
            color=(60, 140, 220, 255), id="s051:mesh")
    return figure_to_visual_qa_scene(fig, case_id="vispy2/mesh")


def _texture2d() -> VisualQAScene:
    fig, ax = subplots()
    texture = np.array([[[255, 0, 0, 255], [0, 255, 0, 255]],
                        [[0, 0, 255, 255], [255, 255, 255, 255]]], dtype=np.uint8)
    ax.mesh([[-0.7, -0.7], [0.7, -0.7], [0.7, 0.7], [-0.7, 0.7]],
            [[0, 1, 2], [0, 2, 3]], color=(255, 255, 255, 255),
            texture=texture, uvs=[[0, 0], [1, 0], [1, 1], [0, 1]], id="s051:texture-mesh")
    return figure_to_visual_qa_scene(fig, case_id="vispy2/texture2d_boundary",
        notes=("Both backends must report unsupported until independent strict evidence exists.",))
