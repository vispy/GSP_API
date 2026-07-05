#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "${script_dir}/.." && pwd -P)"

DATOVIZ_REPO="${DATOVIZ_REPO:-${repo_root}/../datoviz}"
BASELINE="${BASELINE:-${repo_root}/artifacts/visual_qa/s050/pre_rc_compat_s028_timeout}"
OUT_DIR="${OUT_DIR:-${repo_root}/artifacts/visual_qa/s050/post_merge_pre_rc_compat_s028}"
GUIDE_OUT="${GUIDE_OUT:-${repo_root}/artifacts/visual_qa/s050/post_merge_datoviz_guide_axis}"
COMPARE_OUT="${COMPARE_OUT:-${OUT_DIR}/comparison_to_pre_rc_baseline}"
RUN_ID="${RUN_ID:-post-merge-pre-rc-compat-s028}"
RESOLUTION="${RESOLUTION:-800x600}"
GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS="${GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS:-45}"

if [[ ! -d "${DATOVIZ_REPO}" ]]; then
  echo "Datoviz checkout not found: ${DATOVIZ_REPO}" >&2
  echo "Set DATOVIZ_REPO to the local Datoviz checkout." >&2
  exit 2
fi

if [[ ! -f "${BASELINE}/capability_matrix.json" && ! -f "${BASELINE}" ]]; then
  echo "Baseline capability matrix not found: ${BASELINE}" >&2
  echo "Set BASELINE to a review-pack directory or capability_matrix.json." >&2
  exit 2
fi

cd "${repo_root}"
export PYTHONPATH="${DATOVIZ_REPO}:${repo_root}${PYTHONPATH:+:${PYTHONPATH}}"
export GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1
export GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS

uv run python tools/datoviz_v04_smoke.py

uv run python tools/probe_datoviz_guide_axis.py \
  --out "${GUIDE_OUT}"

uv run python -m gsp.qa.visual review-pack \
  --suite s028 \
  --mode datoviz-offscreen-opt-in \
  --out "${OUT_DIR}" \
  --resolution "${RESOLUTION}" \
  --run-id "${RUN_ID}"

uv run python -m gsp.qa.visual compare-matrix \
  --baseline "${BASELINE}" \
  --candidate "${OUT_DIR}" \
  --out "${COMPARE_OUT}"

echo "Review pack: ${OUT_DIR}/index.md"
echo "Comparison: ${COMPARE_OUT}/comparison.md"
