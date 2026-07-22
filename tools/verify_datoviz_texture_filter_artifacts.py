"""Verify S059 Datoviz texture-filter captures against numeric fixture probes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import numpy as np
import numpy.typing as npt

LINEAR_CASE_IDS = (
    "mesh_texture2d/shared_nearest_linear_ndc",
    "mesh_texture2d/linear_centers_clamp_ndc",
    "mesh_texture2d/linear_minification_ndc",
    "mesh_texture2d/linear_alpha_multiply_ndc",
)


def verify_texture_filter_artifacts(
    root: Path, *, tolerance: int = 2
) -> dict[str, object]:
    """Return a conformance summary or raise when a probe exceeds tolerance."""
    report = json.loads((root / "report.json").read_text(encoding="utf-8"))
    report_cases = {case["case_id"]: case for case in report["cases"]}
    results: list[dict[str, object]] = []
    total_probe_count = 0

    for case_id in LINEAR_CASE_IDS:
        case = report_cases.get(case_id)
        if case is None:
            raise ValueError(f"missing S059 case in report: {case_id}")
        backend = case["backends"].get("datoviz", {})
        if backend.get("status") != "rendered":
            raise ValueError(f"Datoviz case did not render: {case_id}")
        slug = case_id.replace("/", "_")
        capture = _rgba8_image(root / "backends" / "datoviz" / f"{slug}.png")
        with np.load(root / "scenes" / f"{slug}.arrays.npz") as arrays:
            probes = np.asarray(arrays["expected_probe_ndc_xy"], dtype=np.float64)
            expected = _expected_rgba(case_id, arrays)
        actual = np.stack([_sample_ndc(capture, float(x), float(y)) for x, y in probes])
        error = np.abs(actual.astype(np.int16) - expected.astype(np.int16))
        max_error = int(error.max(initial=0))
        if max_error > tolerance:
            raise ValueError(
                f"{case_id} exceeded {tolerance}/255 tolerance: max error {max_error}/255; "
                f"actual={actual.tolist()}, expected={expected.tolist()}"
            )
        results.append(
            {
                "case_id": case_id,
                "probe_count": int(probes.shape[0]),
                "max_channel_error_255": max_error,
                "actual_rgba8": actual.tolist(),
                "expected_rgba8": expected.tolist(),
            }
        )
        total_probe_count += int(probes.shape[0])

    return {
        "schema_kind": "gsp.s059.datoviz_texture_filter_conformance",
        "schema_version": 1,
        "tolerance_255": tolerance,
        "case_count": len(results),
        "probe_count": total_probe_count,
        "status": "passed",
        "cases": results,
    }


def _expected_rgba(case_id: str, arrays: Any) -> npt.NDArray[np.uint8]:
    if case_id.endswith("shared_nearest_linear_ndc"):
        return np.stack(
            [arrays["expected_nearest_rgba"], arrays["expected_linear_rgba"]]
        ).astype(np.uint8)
    if case_id.endswith("linear_alpha_multiply_ndc"):
        return np.asarray(arrays["expected_probe_rgba_over_white"], dtype=np.uint8)
    return np.asarray(arrays["expected_probe_rgba"], dtype=np.uint8)


def _rgba8_image(path: Path) -> npt.NDArray[np.uint8]:
    image = np.asarray(mpimg.imread(path))
    if np.issubdtype(image.dtype, np.floating):
        image = np.rint(255.0 * image)
    rgba8 = np.asarray(image, dtype=np.uint8)
    if rgba8.ndim != 3 or rgba8.shape[2] != 4:
        raise ValueError(f"expected RGBA capture at {path}, got {rgba8.shape}")
    return rgba8


def _sample_ndc(
    image: npt.NDArray[np.uint8], x_ndc: float, y_ndc: float
) -> npt.NDArray[np.uint8]:
    height, width, _ = image.shape
    x = int(round((x_ndc + 1.0) * 0.5 * (width - 1)))
    y = int(round((1.0 - y_ndc) * 0.5 * (height - 1)))
    return np.asarray(image[y, x], dtype=np.uint8)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--tolerance", type=int, default=2)
    args = parser.parse_args()
    result = verify_texture_filter_artifacts(args.root, tolerance=args.tolerance)
    path = args.root / "linear_filter_conformance.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
