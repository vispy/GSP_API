"""Artifact writers for visual QA runs."""

from __future__ import annotations

import json
from pathlib import Path
import platform
import sys
from typing import Any, Mapping, cast

import numpy as np

from gsp.protocol import ImageVisual, MarkerVisual, PointVisual, SegmentVisual
from gsp.qa.visual.backend_ids import DATOVIZ_BACKEND_ID
from gsp.qa.visual.case_spec import ProtocolVisual, VisualQAScene
from gsp.qa.visual.cases import case_slug
from gsp.qa.visual.datoviz_probe import DatovizV04ProbeReport


def ensure_run_dirs(out_dir: Path) -> None:
    """Create the visual QA artifact directory layout."""
    for relative in (
        "scenes",
        "backends/matplotlib",
        f"backends/{DATOVIZ_BACKEND_ID}",
        "contact_sheets",
        "notes",
    ):
        (out_dir / relative).mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Mapping[str, object]) -> None:
    """Write deterministic JSON."""
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_scene_artifacts(out_dir: Path, scene: VisualQAScene) -> tuple[Path, Path]:
    """Write a scene JSON file and NumPy sidecar arrays."""
    slug = case_slug(scene.case_id)
    scene_path = out_dir / "scenes" / f"{slug}.scene.json"
    arrays_path = out_dir / "scenes" / f"{slug}.arrays.npz"
    write_json(scene_path, _scene_json(scene))
    np.savez(arrays_path, **cast(Any, scene.arrays))
    return scene_path, arrays_path


def write_environment(out_dir: Path, probe_report: DatovizV04ProbeReport) -> Path:
    """Write the environment summary for a run."""
    path = out_dir / "environment.json"
    payload = {
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "datoviz": {
            "path": probe_report.installed_package.get("path"),
            "imported": probe_report.imports["datoviz"].imported,
            "raw_imported": probe_report.imports["datoviz.raw"].imported,
            "minimal_point_supported": probe_report.minimal_point_scene.supported,
        },
    }
    write_json(path, payload)
    return path


def write_run_manifest(out_dir: Path, payload: Mapping[str, object]) -> Path:
    """Write the run manifest."""
    path = out_dir / "run_manifest.json"
    write_json(path, payload)
    return path


def write_manual_notes(out_dir: Path, case_ids: tuple[str, ...]) -> Path:
    """Write the manual review notes template."""
    path = out_dir / "manual_notes.yaml"
    lines = ["schema_version: 1", "cases:"]
    for case_id in case_ids:
        lines.extend(
            [
                f"  - case_id: {case_id}",
                "    status: pending",
                "    notes: ''",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_case_note(
    out_dir: Path, case_id: str, title: str, notes: tuple[str, ...]
) -> Path:
    """Write a per-case manual review note."""
    path = out_dir / "notes" / f"{case_slug(case_id)}.md"
    body = [f"# {title}", "", f"Case: `{case_id}`", "", "## Review Notes", ""]
    body.extend(f"- {note}" for note in notes)
    body.extend(["", "## Decision", "", "- [ ] pass", "- [ ] needs follow-up", ""])
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def write_summary(out_dir: Path, report: Mapping[str, object]) -> Path:
    """Write a Markdown summary for a run."""
    path = out_dir / "summary.md"
    cases = report["cases"]
    assert isinstance(cases, list)
    lines = [
        "# S023 Visual QA Run",
        "",
        f"Run id: `{report['run_id']}`",
        "",
        "| Case | Matplotlib | Datoviz |",
        "|---|---|---|",
    ]
    for entry in cases:
        assert isinstance(entry, dict)
        backends = entry["backends"]
        assert isinstance(backends, dict)
        matplotlib_status = _backend_status(backends, "matplotlib")
        datoviz_status = _backend_status(backends, DATOVIZ_BACKEND_ID)
        lines.append(
            f"| `{entry['case_id']}` | {matplotlib_status} | {datoviz_status} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _backend_status(backends: Mapping[str, object], backend_id: str) -> str:
    entry = backends.get(backend_id)
    if not isinstance(entry, dict):
        return "not-run"
    status = entry.get("status")
    return str(status)


def _scene_json(scene: VisualQAScene) -> dict[str, object]:
    return {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.scene",
        "case_id": scene.case_id,
        "visuals": [_visual_json(visual) for visual in scene.visuals],
        "arrays": {
            name: {
                "path": f"{case_slug(scene.case_id)}.arrays.npz",
                "key": name,
                "shape": list(array.shape),
                "dtype": str(array.dtype),
            }
            for name, array in scene.arrays.items()
        },
    }


def _visual_json(visual: ProtocolVisual) -> dict[str, Any]:
    if isinstance(visual, PointVisual):
        sizes = visual.sizes
        size_shape: list[int] = (
            list(sizes.shape) if isinstance(sizes, np.ndarray) else []
        )
        return {
            "family": "point",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "positions": {
                "shape": list(visual.positions.shape),
                "dtype": str(visual.positions.dtype),
            },
            "colors": {
                "shape": list(visual.colors.shape),
                "dtype": str(visual.colors.dtype),
            },
            "sizes": {
                "shape": size_shape,
                "dtype": str(sizes.dtype) if isinstance(sizes, np.ndarray) else "float",
            },
        }
    if isinstance(visual, MarkerVisual):
        sizes = visual.sizes
        size_shape = list(sizes.shape) if isinstance(sizes, np.ndarray) else []
        angle = visual.angle
        angle_shape = list(angle.shape) if isinstance(angle, np.ndarray) else []
        shape = visual.shape
        return {
            "family": "marker",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "positions": {
                "shape": list(visual.positions.shape),
                "dtype": str(visual.positions.dtype),
            },
            "shape": [value.value for value in shape]
            if isinstance(shape, tuple)
            else shape.value,
            "fill_colors": {
                "shape": list(visual.fill_colors.shape),
                "dtype": str(visual.fill_colors.dtype),
            },
            "sizes": {
                "shape": size_shape,
                "dtype": str(sizes.dtype) if isinstance(sizes, np.ndarray) else "float",
            },
            "angle": {
                "shape": angle_shape,
                "dtype": str(angle.dtype) if isinstance(angle, np.ndarray) else "float",
            },
            "stroke_color": {
                "shape": list(visual.stroke_color.shape),
                "dtype": str(visual.stroke_color.dtype),
            },
            "stroke_width": visual.stroke_width,
        }
    if isinstance(visual, SegmentVisual):
        widths = visual.widths
        width_shape = list(widths.shape) if isinstance(widths, np.ndarray) else []
        return {
            "family": "segment",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "start_positions": {
                "shape": list(visual.start_positions.shape),
                "dtype": str(visual.start_positions.dtype),
            },
            "end_positions": {
                "shape": list(visual.end_positions.shape),
                "dtype": str(visual.end_positions.dtype),
            },
            "colors": {
                "shape": list(visual.colors.shape),
                "dtype": str(visual.colors.dtype),
            },
            "widths": {
                "shape": width_shape,
                "dtype": str(widths.dtype)
                if isinstance(widths, np.ndarray)
                else "float",
            },
            "cap": visual.cap.value,
        }
    if isinstance(visual, ImageVisual):
        return {
            "family": "image",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "image": {
                "shape": list(visual.image.shape),
                "dtype": str(visual.image.dtype),
            },
            "extent": list(visual.extent),
            "interpolation": visual.interpolation.value,
            "origin": visual.origin.value,
        }
    raise TypeError(f"unsupported visual type: {type(visual).__name__}")
