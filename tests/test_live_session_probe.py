from __future__ import annotations

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from gsp.qa import live_session_probe


def test_live_session_probe_counts_clean_isolated_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        report_path = Path(command[command.index("--out") + 1])
        report_path.parent.mkdir(parents=True)
        report_path.write_text("{}\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(live_session_probe.subprocess, "run", fake_run)
    monkeypatch.setattr(
        live_session_probe,
        "probe_datoviz_v04",
        lambda: SimpleNamespace(installed_package={}, sibling_source={}),
    )

    path = live_session_probe.run_live_session_probe(tmp_path, iterations=2)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["summary"] == {
        "attempted": 6,
        "clean_exit": 6,
        "complete_report": 6,
        "timeouts": 0,
    }


def test_live_session_probe_rejects_unbounded_iteration_count(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="iterations must be positive"):
        live_session_probe.run_live_session_probe(tmp_path, iterations=0)
