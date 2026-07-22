#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "${script_dir}/.." && pwd -P)"

DATOVIZ_REPO="${DATOVIZ_REPO:-${repo_root}/../datoviz}"
RESOLUTION="${RESOLUTION:-801x601}"

resolution_width="${RESOLUTION%x*}"
resolution_height="${RESOLUTION#*x}"
if (( resolution_width % 2 == 0 || resolution_height % 2 == 0 )); then
  echo "Texture-filter checkpoint resolution must have odd dimensions: ${RESOLUTION}" >&2
  exit 2
fi

if [[ ! -d "${DATOVIZ_REPO}/.git" ]]; then
  echo "Datoviz checkout not found: ${DATOVIZ_REPO}" >&2
  exit 2
fi

datoviz_revision="$(git -C "${DATOVIZ_REPO}" rev-parse HEAD)"
datoviz_short_revision="$(git -C "${DATOVIZ_REPO}" rev-parse --short=9 HEAD)"
datoviz_describe="$(git -C "${DATOVIZ_REPO}" describe --tags --always --dirty)"
run_id="${RUN_ID:-datoviz-texture2d-${datoviz_short_revision}}"
out_root="${OUT_ROOT:-${repo_root}/artifacts/visual_qa/s059/checkpoints/${datoviz_short_revision}}"

mkdir -p "${out_root}"
cd "${repo_root}"
export PYTHONPATH="${DATOVIZ_REPO}:${repo_root}/src${PYTHONPATH:+:${PYTHONPATH}}"

DATOVIZ_REPO="${DATOVIZ_REPO}" DATOVIZ_REVISION="${datoviz_revision}" \
  DATOVIZ_DESCRIBE="${datoviz_describe}" OUT_ROOT="${out_root}" uv run python - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

import datoviz

from gsp_datoviz.latest_api_contract import datoviz_current_api_missing_symbols


repo = Path(os.environ["DATOVIZ_REPO"]).resolve()
module = Path(datoviz.__file__).resolve()
if not module.is_relative_to(repo):
    raise SystemExit(f"Datoviz provenance mismatch: imported {module}, expected under {repo}")
missing = datoviz_current_api_missing_symbols(datoviz)
if missing:
    raise SystemExit(f"Datoviz current API is missing required symbols: {missing}")

payload = {
    "schema_kind": "gsp.s059.datoviz_texture2d_checkpoint_provenance",
    "schema_version": 1,
    "datoviz_repo": str(repo),
    "datoviz_revision": os.environ["DATOVIZ_REVISION"],
    "datoviz_describe": os.environ["DATOVIZ_DESCRIBE"],
    "datoviz_module": str(module),
    "field_slot_sampling_symbols": [
        "dvz_field_sampling_desc",
        "dvz_visual_set_field_sampling",
    ],
}
path = Path(os.environ["OUT_ROOT"]) / "provenance.json"
path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(path)
PY

tools/run_datoviz_visual_review_pack.sh \
  --suite s059 \
  --out "${out_root}/review" \
  --resolution "${RESOLUTION}" \
  --run-id "${run_id}" \
  --case mesh_texture2d/uv_orientation_triangle_ndc \
  --case mesh_texture2d/checker_quad_clamp_ndc \
  --case mesh_texture2d/color_multiply_seam_ndc \
  --case mesh_texture2d/opaque_view3d_quad \
  --case mesh_texture2d/alpha_diagnostic_ndc \
  --case mesh_texture2d/shared_nearest_linear_ndc \
  --case mesh_texture2d/linear_centers_clamp_ndc \
  --case mesh_texture2d/linear_minification_ndc \
  --case mesh_texture2d/linear_alpha_multiply_ndc

uv run python tools/verify_datoviz_texture_filter_artifacts.py "${out_root}/review"

OUT_ROOT="${out_root}" DATOVIZ_REVISION="${datoviz_revision}" uv run python - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path


out_root = Path(os.environ["OUT_ROOT"])
report_path = out_root / "review" / "report.json"
report = json.loads(report_path.read_text(encoding="utf-8"))
texture_cases = [
    case for case in report["cases"] if case["case_id"].startswith("mesh_texture2d/")
]
if len(texture_cases) != 9:
    raise SystemExit(f"expected nine Texture2D cases, found {len(texture_cases)}")

failures: list[str] = []
artifacts: list[str] = []
for case in texture_cases:
    backend = case["backends"].get("datoviz", {})
    if backend.get("status") != "rendered":
        failures.append(f"{case['case_id']}: {backend.get('status', 'missing')}")
        continue
    artifact = Path(backend["artifact_path"])
    if not artifact.is_file():
        failures.append(f"{case['case_id']}: missing artifact {artifact}")
        continue
    artifacts.append(str(artifact.relative_to(out_root)))
if failures:
    raise SystemExit("Datoviz Texture2D checkpoint failed: " + "; ".join(failures))

summary = {
    "schema_kind": "gsp.s059.datoviz_texture2d_checkpoint",
    "schema_version": 1,
    "datoviz_revision": os.environ["DATOVIZ_REVISION"],
    "case_count": len(texture_cases),
    "nearest_regression_case_count": 5,
    "linear_filter_case_count": 4,
    "rendered_count": len(artifacts),
    "artifacts": artifacts,
    "status": "passed",
}
path = out_root / "texture2d_checkpoint.json"
path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(path)
PY

uv run python examples/vispy2_datoviz_texture2d.py
uv run python -m pytest \
  tests/test_datoviz_v04_protocol_renderer.py \
  tests/test_datoviz_v04_probe.py \
  tests/test_visual_qa_harness.py \
  tests/test_vispy2_protocol_mvp.py \
  -q

echo "Datoviz revision: ${datoviz_revision} (${datoviz_describe})"
echo "Texture2D checkpoint: ${out_root}/texture2d_checkpoint.json"
echo "Review pack: ${out_root}/review/index.md"
