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
from typing import Any, Literal, Sequence

import numpy as np

from gsp.protocol import CanvasSize, CoordinateSpace, PointVisual, View2D
from gsp.qa.visual.artifacts import write_json
from gsp.qa.visual.datoviz_probe import probe_datoviz_v04
from gsp_datoviz.protocol_renderer import DatovizV04ProtocolRenderer


ProbeMode = Literal[
    "bounded_run",
    "blocking_auto_stop",
    "polled_run",
    "retained_view2d",
    "retained_point",
]
PROBE_MODES: tuple[ProbeMode, ...] = (
    "bounded_run",
    "blocking_auto_stop",
    "polled_run",
    "retained_view2d",
    "retained_point",
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
    report_path.parent.mkdir(parents=True, exist_ok=True)
    phases: list[str] = ["create_requested"]
    before_hash: str | None = None
    after_hash: str | None = None
    frame_count = 0
    callback: Any | None = None
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
        elif mode == "blocking_auto_stop":
            live_view = renderer._ensure_live_view()
            callback_type = renderer.dvz.DvzViewFrameCallback

            def on_frame(_view: object, _user_data: object) -> None:
                nonlocal frame_count
                frame_count += 1
                if frame_count == 1:
                    phases.append("first_frame")
                if frame_count >= 3:
                    renderer.dvz.dvz_app_stop(renderer.app)
                    phases.append("stop_requested")

            callback = callback_type(on_frame)
            renderer.dvz.dvz_view_set_frame_callback(live_view, callback, None)
            renderer.show(frame_count=0)
            phases.append("blocking_run_complete")
        elif mode == "polled_run":
            for _ in range(3):
                renderer.show(frame_count=1)
            phases.extend(("first_frame", "poll_complete"))
        elif mode == "retained_view2d":
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
        else:
            live_view = renderer._ensure_live_view()
            renderer.dvz.dvz_app_render_once(renderer.app)
            phases.append("first_frame")
            before_path = report_path.with_name("before.png")
            after_path = report_path.with_name("after.png")
            before_hash = _capture_live_hash(renderer, live_view, before_path)
            renderer.update_point_visual(_point_visual(shift=0.45))
            phases.append("retained_point_update")
            renderer.dvz.dvz_view_request_frame(live_view)
            renderer.dvz.dvz_app_render_once(renderer.app)
            after_hash = _capture_live_hash(renderer, live_view, after_path)
            if before_hash == after_hash:
                raise RuntimeError("retained point update did not change live capture")
            phases.append("updated_frame_verified")
    finally:
        phases.append("close_requested")
        renderer.close()
        renderer.close()
        phases.extend(("owner_closed", "double_close_idempotent"))
    write_json(
        report_path,
        {
            "schema_kind": "gsp.s053.datoviz_live_session_child",
            "schema_version": 1,
            "mode": mode,
            "phases": phases,
            "before_sha256": before_hash,
            "after_sha256": after_hash,
            "frame_callback_count": frame_count,
            "semantic_visual_id": "visual:s053:point",
        },
    )


def _point_visual(*, shift: float = 0.0) -> PointVisual:
    return PointVisual(
        id="visual:s053:point",
        positions=np.array(
            [[-0.6 + shift, -0.2], [0.4 + shift, 0.3]], dtype=np.float32
        ),
        colors=np.array([[230, 60, 70, 255], [40, 150, 210, 255]], dtype=np.uint8),
        sizes=np.array([24.0, 36.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
    )


def _capture_live_hash(
    renderer: DatovizV04ProtocolRenderer, live_view: object, path: Path
) -> str:
    result = renderer.dvz.dvz_view_capture_png(live_view, str(path).encode())
    if result not in (0, None):
        raise RuntimeError(f"live capture failed with result {result!r}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child-mode", choices=PROBE_MODES, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    run_child(args.child_mode, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
