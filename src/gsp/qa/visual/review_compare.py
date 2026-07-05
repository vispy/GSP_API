"""Comparison helpers for visual QA review-pack capability matrices."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Mapping

from gsp.qa.visual.artifacts import write_json


_STATUS_RANK = {
    "not_run": 0,
    "crashed": 1,
    "disabled": 2,
    "unsupported": 2,
    "experimental": 3,
    "adapted": 4,
    "strict": 5,
}


def compare_capability_matrices(
    *,
    baseline_path: Path,
    candidate_path: Path,
    out_dir: Path | None = None,
) -> dict[str, object]:
    """Compare two review-pack capability matrices by backend and case."""
    baseline = _load_matrix(_resolve_matrix_path(baseline_path))
    candidate = _load_matrix(_resolve_matrix_path(candidate_path))
    baseline_rows = _rows_by_key(baseline)
    candidate_rows = _rows_by_key(candidate)
    row_changes: list[dict[str, object]] = []

    for key in sorted(baseline_rows.keys() | candidate_rows.keys()):
        baseline_row = baseline_rows.get(key)
        candidate_row = candidate_rows.get(key)
        row_changes.append(_compare_row(key, baseline_row, candidate_row))

    summary = _comparison_summary(row_changes)
    result: dict[str, object] = {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.capability_matrix_comparison",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline_path": str(_resolve_matrix_path(baseline_path)),
        "candidate_path": str(_resolve_matrix_path(candidate_path)),
        "baseline_run_id": baseline.get("run_id"),
        "candidate_run_id": candidate.get("run_id"),
        "suite": candidate.get("suite") or baseline.get("suite"),
        "summary": summary,
        "baseline_summary": baseline.get("summary", {}),
        "candidate_summary": candidate.get("summary", {}),
        "rows": row_changes,
    }
    if out_dir is not None:
        _write_comparison(out_dir, result)
    return result


def _resolve_matrix_path(path: Path) -> Path:
    if path.is_dir():
        return path / "capability_matrix.json"
    return path


def _load_matrix(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise TypeError(f"capability matrix must be a JSON object: {path}")
    if payload.get("schema_kind") != "gsp.visual_qa.capability_matrix":
        raise ValueError(f"not a visual QA capability matrix: {path}")
    return payload


def _rows_by_key(matrix: Mapping[str, object]) -> dict[tuple[str, str], Mapping[str, object]]:
    rows = matrix.get("rows")
    if not isinstance(rows, list):
        raise TypeError("capability matrix rows must be a list")
    by_key: dict[tuple[str, str], Mapping[str, object]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise TypeError("capability matrix row entries must be objects")
        backend = row.get("backend")
        case_id = row.get("case_id")
        if not isinstance(backend, str) or not isinstance(case_id, str):
            raise TypeError("capability matrix rows require string backend and case_id")
        by_key[(backend, case_id)] = row
    return by_key


def _compare_row(
    key: tuple[str, str],
    baseline_row: Mapping[str, object] | None,
    candidate_row: Mapping[str, object] | None,
) -> dict[str, object]:
    backend, case_id = key
    if baseline_row is None:
        candidate_status = _row_text(candidate_row, "status")
        return {
            "backend": backend,
            "case_id": case_id,
            "outcome": "added",
            "baseline_status": None,
            "candidate_status": candidate_status,
            "baseline_reason_code": None,
            "candidate_reason_code": _row_text(candidate_row, "reason_code"),
            "status_delta": _status_rank(candidate_status),
        }
    if candidate_row is None:
        baseline_status = _row_text(baseline_row, "status")
        return {
            "backend": backend,
            "case_id": case_id,
            "outcome": "removed",
            "baseline_status": baseline_status,
            "candidate_status": None,
            "baseline_reason_code": _row_text(baseline_row, "reason_code"),
            "candidate_reason_code": None,
            "status_delta": -_status_rank(baseline_status),
        }

    baseline_status = _row_text(baseline_row, "status")
    candidate_status = _row_text(candidate_row, "status")
    baseline_reason = _row_text(baseline_row, "reason_code")
    candidate_reason = _row_text(candidate_row, "reason_code")
    status_delta = _status_rank(candidate_status) - _status_rank(baseline_status)
    if status_delta > 0:
        outcome = "improved"
    elif status_delta < 0:
        outcome = "regressed"
    elif baseline_status != candidate_status or baseline_reason != candidate_reason:
        outcome = "changed"
    else:
        outcome = "unchanged"
    return {
        "backend": backend,
        "case_id": case_id,
        "outcome": outcome,
        "baseline_status": baseline_status,
        "candidate_status": candidate_status,
        "baseline_reason_code": baseline_reason,
        "candidate_reason_code": candidate_reason,
        "status_delta": status_delta,
    }


def _row_text(row: Mapping[str, object] | None, key: str) -> str:
    if row is None:
        return ""
    value = row.get(key)
    return value if isinstance(value, str) else ""


def _status_rank(status: str) -> int:
    return _STATUS_RANK.get(status, 0)


def _comparison_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    outcomes = Counter(str(row["outcome"]) for row in rows)
    backend_outcomes: dict[str, dict[str, int]] = {}
    for row in rows:
        backend = str(row["backend"])
        backend_counter = backend_outcomes.setdefault(backend, {})
        outcome = str(row["outcome"])
        backend_counter[outcome] = backend_counter.get(outcome, 0) + 1
    return {
        "total_rows": len(rows),
        "outcomes": {
            outcome: outcomes.get(outcome, 0)
            for outcome in ("improved", "regressed", "changed", "added", "removed", "unchanged")
        },
        "backend_outcomes": backend_outcomes,
    }


def _write_comparison(out_dir: Path, comparison: Mapping[str, object]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "comparison.json", comparison)
    (out_dir / "comparison.md").write_text(
        _comparison_markdown(comparison), encoding="utf-8"
    )


def _comparison_markdown(comparison: Mapping[str, object]) -> str:
    summary = comparison.get("summary", {})
    outcomes = summary.get("outcomes", {}) if isinstance(summary, Mapping) else {}
    lines = [
        "# Visual QA capability matrix comparison",
        "",
        f"- Baseline: `{comparison.get('baseline_path', '')}`",
        f"- Candidate: `{comparison.get('candidate_path', '')}`",
        f"- Baseline run: `{comparison.get('baseline_run_id', '')}`",
        f"- Candidate run: `{comparison.get('candidate_run_id', '')}`",
        "",
        "## Summary",
        "",
        "| Outcome | Count |",
        "|---|---:|",
    ]
    for outcome in ("improved", "regressed", "changed", "added", "removed", "unchanged"):
        count = outcomes.get(outcome, 0) if isinstance(outcomes, Mapping) else 0
        lines.append(f"| {outcome} | {count} |")

    rows = comparison.get("rows", [])
    if isinstance(rows, list):
        for title, outcome in (("Regressions", "regressed"), ("Improvements", "improved"), ("Changes", "changed")):
            selected = [
                row
                for row in rows
                if isinstance(row, Mapping) and row.get("outcome") == outcome
            ]
            if not selected:
                continue
            lines.extend(["", f"## {title}", "", "| Backend | Case | Baseline | Candidate |", "|---|---|---|---|"])
            for row in selected:
                lines.append(
                    "| {backend} | `{case}` | {baseline} | {candidate} |".format(
                        backend=row.get("backend", ""),
                        case=row.get("case_id", ""),
                        baseline=row.get("baseline_status", ""),
                        candidate=row.get("candidate_status", ""),
                    )
                )
    lines.append("")
    return "\n".join(lines)
