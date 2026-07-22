#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "${script_dir}/.." && pwd -P)"

DATOVIZ_REPO="${DATOVIZ_REPO:-${repo_root}/../datoviz}"
BASELINE="${BASELINE:-${repo_root}/artifacts/visual_qa/s050/latest_pre_rc_compat_s028}"
RESOLUTION="${RESOLUTION:-800x600}"
LIFECYCLE_ITERATIONS="${LIFECYCLE_ITERATIONS:-5}"
LIFECYCLE_TIMEOUT_SECONDS="${LIFECYCLE_TIMEOUT_SECONDS:-20}"
GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS="${GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS:-45}"

if [[ ! -d "${DATOVIZ_REPO}/.git" ]]; then
  echo "Datoviz checkout not found: ${DATOVIZ_REPO}" >&2
  exit 2
fi
if [[ ! -f "${BASELINE}/capability_matrix.json" && ! -f "${BASELINE}" ]]; then
  echo "Baseline capability matrix not found: ${BASELINE}" >&2
  exit 2
fi
if ! [[ "${LIFECYCLE_ITERATIONS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "LIFECYCLE_ITERATIONS must be a positive integer." >&2
  exit 2
fi

datoviz_revision="$(git -C "${DATOVIZ_REPO}" rev-parse HEAD)"
datoviz_short_revision="$(git -C "${DATOVIZ_REPO}" rev-parse --short=9 HEAD)"
datoviz_describe="$(git -C "${DATOVIZ_REPO}" describe --tags --always --dirty)"
run_id="${RUN_ID:-datoviz-v04dev-${datoviz_short_revision}}"
out_root="${OUT_ROOT:-${repo_root}/artifacts/visual_qa/s058/checkpoints/${datoviz_short_revision}}"
review_out="${out_root}/s028-review"
guide_out="${out_root}/guide-axis"
comparison_out="${review_out}/comparison"

mkdir -p "${out_root}"
cd "${repo_root}"
export PYTHONPATH="${DATOVIZ_REPO}:${repo_root}/src${PYTHONPATH:+:${PYTHONPATH}}"
export GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1
export GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS

DATOVIZ_REPO="${DATOVIZ_REPO}" DATOVIZ_REVISION="${datoviz_revision}" \
  DATOVIZ_DESCRIBE="${datoviz_describe}" OUT_ROOT="${out_root}" uv run python - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

import datoviz

repo = Path(os.environ["DATOVIZ_REPO"]).resolve()
module = Path(datoviz.__file__).resolve()
if not module.is_relative_to(repo):
    raise SystemExit(f"Datoviz provenance mismatch: imported {module}, expected a path under {repo}")
payload = {
    "schema_kind": "gsp.s058.datoviz_v04dev_checkpoint_provenance",
    "schema_version": 1,
    "datoviz_repo": str(repo),
    "datoviz_revision": os.environ["DATOVIZ_REVISION"],
    "datoviz_describe": os.environ["DATOVIZ_DESCRIBE"],
    "datoviz_module": str(module),
}
path = Path(os.environ["OUT_ROOT"]) / "provenance.json"
path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(path)
PY

uv run python tools/datoviz_v04_smoke.py \
  --require-query-ready \
  --require-live-query-hit > "${out_root}/datoviz_v04_smoke.json"

uv run python tools/probe_datoviz_guide_axis.py --out "${guide_out}"

uv run python -m gsp.qa.visual review-pack \
  --suite s028 \
  --mode datoviz-offscreen-opt-in \
  --out "${review_out}" \
  --resolution "${RESOLUTION}" \
  --run-id "${run_id}"

uv run python -m gsp.qa.visual compare-matrix \
  --baseline "${BASELINE}" \
  --candidate "${review_out}" \
  --out "${comparison_out}"

uv run python -m gsp.qa.public_session_probe \
  --out "${out_root}/public-session/public_session_probe.json" \
  --iterations "${LIFECYCLE_ITERATIONS}" \
  --timeout "${LIFECYCLE_TIMEOUT_SECONDS}"

OUT_ROOT="${out_root}" LIFECYCLE_ITERATIONS="${LIFECYCLE_ITERATIONS}" \
  LIFECYCLE_TIMEOUT_SECONDS="${LIFECYCLE_TIMEOUT_SECONDS}" uv run python - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

from gsp.qa.live_session_probe import run_live_session_probe

path = run_live_session_probe(
    Path(os.environ["OUT_ROOT"]) / "live-session",
    iterations=int(os.environ["LIFECYCLE_ITERATIONS"]),
    timeout_seconds=float(os.environ["LIFECYCLE_TIMEOUT_SECONDS"]),
)
print(path)
PY

uv run python -m pytest \
  tests/test_datoviz_v04_probe.py \
  tests/test_datoviz_v04_protocol_renderer.py \
  tests/test_vispy2_session.py \
  tests/test_public_session_probe.py \
  tests/test_live_session_probe.py \
  -q

echo "Datoviz revision: ${datoviz_revision} (${datoviz_describe})"
echo "Checkpoint: ${out_root}"
echo "Review pack: ${review_out}/index.md"
echo "Comparison: ${comparison_out}/comparison.md"
