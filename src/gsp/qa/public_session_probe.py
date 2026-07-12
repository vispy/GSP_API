"""Bounded subprocess evidence for the public VisPy2 Datoviz session preview."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Literal

import gsp_vispy2 as vp


PUBLIC_SESSION_EVIDENCE_SCHEMA = "gsp.s056.public_session_lifecycle"
PublicSessionMode = Literal["blocking", "polling"]


@dataclass(frozen=True, slots=True)
class PublicSessionIteration:
    """Outcome of one isolated public-session lifecycle."""

    mode: PublicSessionMode
    iteration: int
    returncode: int | None
    timed_out: bool
    report_complete: bool
    phases: tuple[str, ...]
    diagnostic_codes: tuple[str, ...]
    stderr: str

    @property
    def clean(self) -> bool:
        return (
            not self.timed_out
            and self.returncode == 0
            and self.report_complete
            and "session_closed" in self.phases
        )


def run_public_session_probe(
    output_path: Path,
    *,
    iterations: int = 5,
    timeout_seconds: float = 20.0,
) -> dict[str, object]:
    """Run repeated blocking and polling lifecycles in bounded subprocesses."""
    if iterations < 1:
        raise ValueError("iterations must be positive")
    if timeout_seconds <= 0.0:
        raise ValueError("timeout_seconds must be positive")
    results: list[PublicSessionIteration] = []
    env = os.environ.copy()
    env.pop("GSP_TEST", None)
    env.setdefault("PYTHONPATH", "src")
    for mode in ("blocking", "polling"):
        for iteration in range(1, iterations + 1):
            command = [
                sys.executable,
                "-m",
                "gsp.qa.public_session_probe",
                "--child-mode",
                mode,
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
                child = _last_json_object(completed.stdout)
                results.append(PublicSessionIteration(
                    mode=mode,
                    iteration=iteration,
                    returncode=completed.returncode,
                    timed_out=False,
                    report_complete=child.get("status") == "complete",
                    phases=_string_tuple(child.get("phases")),
                    diagnostic_codes=_string_tuple(child.get("diagnostic_codes")),
                    stderr=completed.stderr[-2000:],
                ))
            except subprocess.TimeoutExpired as exc:
                results.append(PublicSessionIteration(
                    mode=mode,
                    iteration=iteration,
                    returncode=None,
                    timed_out=True,
                    report_complete=False,
                    phases=(),
                    diagnostic_codes=("session.backend.timeout",),
                    stderr=str(exc),
                ))
    rows = [asdict(result) | {"clean": result.clean} for result in results]
    clean_count = sum(result.clean for result in results)
    payload: dict[str, object] = {
        "schema_kind": PUBLIC_SESSION_EVIDENCE_SCHEMA,
        "schema_version": 1,
        "iterations_per_mode": iterations,
        "timeout_seconds": timeout_seconds,
        "modes": ["blocking", "polling"],
        "clean_count": clean_count,
        "total_count": len(results),
        "timeout_count": sum(result.timed_out for result in results),
        "passed": clean_count == len(results),
        "results": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def _run_child(mode: PublicSessionMode) -> int:
    phases = ["figure_created"]
    figure, axes = vp.subplots()
    axes.scatter([-0.6, 0.0, 0.55], [-0.3, 0.45, -0.1], size=[20, 36, 52])
    axes.set_xlim(-1.0, 1.0)
    axes.set_ylim(-1.0, 1.0)
    phases.append("scene_ready")
    diagnostic_codes: list[str] = []
    try:
        with vp.open_session("datoviz") as session:
            phases.append("session_opened")
            plan = session.inspect(figure)
            phases.append("inspection_complete")
            plan.require_executable()
            if mode == "blocking":
                session.show(figure, block=True, frame_count=2)
                phases.append("blocking_complete")
            else:
                display = session.show(figure, block=False)
                phases.append("display_created")
                session.poll(display)
                phases.append("poll_1_complete")
                session.poll(display)
                phases.append("poll_2_complete")
            diagnostic_codes.extend(item.code for item in session.diagnostics)
        phases.append("session_closed")
    except Exception as exc:
        print(json.dumps({
            "status": "failed",
            "mode": mode,
            "phases": phases,
            "diagnostic_codes": diagnostic_codes,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }))
        return 1
    print(json.dumps({
        "status": "complete",
        "mode": mode,
        "phases": phases,
        "diagnostic_codes": diagnostic_codes,
    }))
    return 0


def _last_json_object(stdout: str) -> dict[str, object]:
    for line in reversed(stdout.splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return {str(key): item for key, item in value.items()}
    return {}


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child-mode", choices=("blocking", "polling"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    if args.child_mode is not None:
        return _run_child(args.child_mode)
    if args.out is None:
        parser.error("--out is required for the parent probe")
    payload = run_public_session_probe(
        args.out,
        iterations=args.iterations,
        timeout_seconds=args.timeout,
    )
    print(json.dumps({
        "passed": payload["passed"],
        "clean_count": payload["clean_count"],
        "total_count": payload["total_count"],
        "output": str(args.out),
    }))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
