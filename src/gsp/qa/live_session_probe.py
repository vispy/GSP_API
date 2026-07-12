"""Bounded Datoviz live-window lifecycle evidence for S053."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from time import monotonic
from typing import Literal, Sequence

import numpy as np

from gsp.protocol import CanvasSize, CoordinateSpace, PointVisual, View2D
from gsp.qa.visual.artifacts import write_json
from gsp.qa.visual.datoviz_probe import probe_datoviz_v04
from gsp_datoviz.protocol_renderer import DatovizV04ProtocolRenderer


ProbeMode = Literal["bounded_run", "polled_run", "retained_view2d"]
PROBE_MODES: tuple[ProbeMode, ...] = (
    "bounded_run",
    "polled_run",
    "retained_view2d",
)


def run_live_session_probe(
    out_dir: Path, *, iterations: int = 5, timeout_seconds: float = 20.0
) -> Path:
    """Run every live lifecycle mode in isolated bounded subprocesses."""
    if iterations < 1:
        raise ValueError("iterations must be positive")
    results: list[dict[str, object]] = []
    clean_exit_count = 0
    complete_report_count = 0
    timeout_count = 0
    env = os.environ.copy()
    env.pop("GSP_TEST", None)
    env.setdefault("PYTHONPATH", "src")
    for mode in PROBE_MODES:
        for iteration in range(1, iterations + 1):
            child_dir = out_dir / "iterations" / mode / f"{iteration:02d}"
            child_report = child_dir / "child_report.json"
            command = [
                sys.executable,
                "-m",
                "gsp.qa.live_session_probe",
                "--child-mode",
                mode,
                "--out",
                str(child_report),
            ]
            started = monotonic()
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
                timed_out = False
                stdout = completed.stdout
                stderr = completed.stderr
            except subprocess.TimeoutExpired as exc:
                returncode = 124
                timed_out = True
                stdout = str(exc.stdout or "")
                stderr = str(exc.stderr or "")
            report_complete = child_report.is_file()
            clean_exit_count += int(returncode == 0)
            complete_report_count += int(report_complete)
            timeout_count += int(timed_out)
            results.append(
                {
                    "mode": mode,
                    "iteration": iteration,
                    "returncode": returncode,
                    "timed_out": timed_out,
                    "elapsed_seconds": monotonic() - started,
                    "report_complete": report_complete,
                    "stdout": stdout,
                    "stderr": stderr,
                }
            )
    probe = probe_datoviz_v04()
    payload = {
        "schema_kind": "gsp.s053.datoviz_live_session_probe",
        "schema_version": 1,
        "iterations_per_mode": iterations,
        "modes": list(PROBE_MODES),
        "datoviz": {
            "installed_package": dict(probe.installed_package),
            "sibling_source": dict(probe.sibling_source),
        },
        "results": results,
        "summary": {
            "attempted": len(results),
            "clean_exit": clean_exit_count,
            "complete_report": complete_report_count,
            "timeouts": timeout_count,
        },
        "future_wrapper_misuse_policy": {
            "double_close": "idempotent",
            "show_after_close": "must_raise_lifecycle_error",
            "update_after_close": "must_raise_lifecycle_error",
            "poll_after_owner_close": "must_raise_lifecycle_error",
            "hidden_nonblocking_owner": "forbidden",
        },
    }
    path = out_dir / "live_session_probe.json"
    write_json(path, payload)
    return path


def run_child(mode: ProbeMode, report_path: Path) -> None:
    """Execute one bounded live lifecycle inside a crash-isolated process."""
    phases: list[str] = ["create_requested"]
    before_hash: str | None = None
    after_hash: str | None = None
    view = View2D(id="view:s053", panel_id="panel:s053")
    renderer = DatovizV04ProtocolRenderer(
        canvas_size=CanvasSize.pixel_exact(320, 240), view=view
    )
    phases.append("owner_created")
    try:
        renderer.add_point_visual(_point_visual())
        phases.append("visual_attached")
        if mode == "bounded_run":
            renderer.show(frame_count=2)
            phases.extend(("first_frame", "bounded_run_complete"))
        elif mode == "polled_run":
            for _ in range(3):
                renderer.show(frame_count=1)
            phases.extend(("first_frame", "poll_complete"))
        else:
            before = renderer.capture_png_bytes()
            before_hash = hashlib.sha256(before).hexdigest()
            phases.append("first_frame")
            updated_view = View2D(
                id=view.id,
                panel_id=view.panel_id,
                x_range=(-0.5, 0.5),
                y_range=(-0.5, 0.5),
            )
            renderer.apply_retained_view2d_navigation(updated_view)
            phases.append("retained_view2d_update")
            after = renderer.capture_png_bytes()
            after_hash = hashlib.sha256(after).hexdigest()
            if before_hash == after_hash:
                raise RuntimeError("retained View2D update did not change captured output")
            phases.append("updated_frame_verified")
    finally:
        phases.append("close_requested")
        renderer.close()
        renderer.close()
        phases.extend(("owner_closed", "double_close_idempotent"))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        report_path,
        {
            "schema_kind": "gsp.s053.datoviz_live_session_child",
            "schema_version": 1,
            "mode": mode,
            "phases": phases,
            "before_sha256": before_hash,
            "after_sha256": after_hash,
            "semantic_visual_id": "visual:s053:point",
        },
    )


def _point_visual() -> PointVisual:
    return PointVisual(
        id="visual:s053:point",
        positions=np.array([[-0.6, -0.2], [0.4, 0.3]], dtype=np.float32),
        colors=np.array([[230, 60, 70, 255], [40, 150, 210, 255]], dtype=np.uint8),
        sizes=np.array([24.0, 36.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child-mode", choices=PROBE_MODES, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    run_child(args.child_mode, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
