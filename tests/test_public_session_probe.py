"""Tests for bounded public-session evidence orchestration."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from gsp.qa.public_session_probe import (
    PUBLIC_SESSION_EVIDENCE_SCHEMA,
    _last_json_object,
    run_public_session_probe,
)


def test_last_json_object_ignores_non_json_backend_output() -> None:
    assert _last_json_object("backend log\n{\"status\": \"complete\"}\n") == {
        "status": "complete"
    }


def test_probe_validates_bounds(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="iterations"):
        run_public_session_probe(tmp_path / "result.json", iterations=0)
    with pytest.raises(ValueError, match="timeout"):
        run_public_session_probe(tmp_path / "result.json", timeout_seconds=0.0)


def test_probe_records_clean_repeated_modes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        command = args[0]
        assert isinstance(command, list)
        mode = command[-1]
        phases = ["session_opened", f"{mode}_complete", "session_closed"]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({"status": "complete", "phases": phases}) + "\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    path = tmp_path / "public_session.json"
    payload = run_public_session_probe(path, iterations=2)
    assert payload["schema_kind"] == PUBLIC_SESSION_EVIDENCE_SCHEMA
    assert payload["clean_count"] == 4
    assert payload["total_count"] == 4
    assert payload["passed"] is True
    assert json.loads(path.read_text(encoding="utf-8"))["timeout_count"] == 0


def test_probe_preserves_timeout_as_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def timeout(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd="probe", timeout=1.0)

    monkeypatch.setattr(subprocess, "run", timeout)
    payload = run_public_session_probe(tmp_path / "result.json", iterations=1)
    assert payload["passed"] is False
    assert payload["timeout_count"] == 2
    results = payload["results"]
    assert isinstance(results, list)
    assert all(
        row["diagnostic_codes"] == ("session.backend.timeout",) for row in results
    )
