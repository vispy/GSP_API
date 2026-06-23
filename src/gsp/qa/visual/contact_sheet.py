"""Contact sheet generation for visual QA."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import matplotlib

matplotlib.use("Agg")
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import matplotlib.pyplot as plt


def write_contact_sheets(out_dir: Path, case_reports: list[dict[str, object]], backends: tuple[str, ...]) -> tuple[Path, ...]:
    """Write per-case and all-case contact sheets."""
    paths: list[Path] = []
    for case_report in case_reports:
        paths.append(_write_case_sheet(out_dir, case_report, backends))
    paths.append(_write_all_cases_sheet(out_dir, case_reports, backends))
    return tuple(paths)


def _write_case_sheet(out_dir: Path, case_report: Mapping[str, object], backends: tuple[str, ...]) -> Path:
    case_id = str(case_report["case_id"])
    slug = case_id.replace("/", "_")
    path = out_dir / "contact_sheets" / f"{slug}.png"
    fig, axes = plt.subplots(1, len(backends), figsize=(4 * len(backends), 4), squeeze=False)
    try:
        for index, backend in enumerate(backends):
            _draw_tile(axes[0][index], case_report, backend)
        fig.tight_layout()
        fig.savefig(path, dpi=120)
    finally:
        plt.close(fig)
    return path


def _write_all_cases_sheet(out_dir: Path, case_reports: list[dict[str, object]], backends: tuple[str, ...]) -> Path:
    path = out_dir / "contact_sheets" / "s023_all_cases.png"
    fig, axes = plt.subplots(len(case_reports), len(backends), figsize=(4 * len(backends), 3.2 * len(case_reports)), squeeze=False)
    try:
        for row, case_report in enumerate(case_reports):
            for column, backend in enumerate(backends):
                _draw_tile(axes[row][column], case_report, backend)
        fig.tight_layout()
        fig.savefig(path, dpi=120)
    finally:
        plt.close(fig)
    return path


def _draw_tile(axis: Axes, case_report: Mapping[str, object], backend: str) -> None:
    backends = case_report["backends"]
    assert isinstance(backends, dict)
    entry = backends.get(backend)
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_title(f"{case_report['case_id']}\n{backend}", fontsize=9)
    if isinstance(entry, dict) and entry.get("status") == "rendered" and isinstance(entry.get("artifact_path"), str):
        image = mpimg.imread(entry["artifact_path"])
        axis.imshow(image)
        return
    status = entry.get("status") if isinstance(entry, dict) else "not-run"
    detail = entry.get("unsupported_path") if isinstance(entry, dict) else None
    axis.text(
        0.5,
        0.55,
        str(status).upper(),
        ha="center",
        va="center",
        fontsize=14,
        transform=axis.transAxes,
    )
    if detail is not None:
        axis.text(0.5, 0.42, Path(str(detail)).name, ha="center", va="center", fontsize=8, transform=axis.transAxes)
