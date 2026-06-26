#!/usr/bin/env bash
set -euo pipefail

DATOVIZ_REPO="${DATOVIZ_REPO:-/Users/cyrille/GIT/Viz/datoviz}"

if [[ ! -d "${DATOVIZ_REPO}" ]]; then
  echo "Datoviz checkout not found: ${DATOVIZ_REPO}" >&2
  echo "Set DATOVIZ_REPO to the local Datoviz v0.4-dev checkout." >&2
  exit 2
fi

export PYTHONPATH="${DATOVIZ_REPO}${PYTHONPATH:+:${PYTHONPATH}}"
export GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1

if [[ "$(uname -s)" == "Darwin" ]]; then
  datoviz_vulkan_dir="${DATOVIZ_REPO}/libs/vulkan/macos_arm64"
  datoviz_icd="${datoviz_vulkan_dir}/MoltenVK_icd.json"
  if [[ ! -f "${datoviz_icd}" ]]; then
    echo "Datoviz MoltenVK ICD not found: ${datoviz_icd}" >&2
    echo "Build or fetch Datoviz runtime libraries, then retry." >&2
    exit 2
  fi
  export DYLD_LIBRARY_PATH="${datoviz_vulkan_dir}${DYLD_LIBRARY_PATH:+:${DYLD_LIBRARY_PATH}}"
  export VK_ICD_FILENAMES="${datoviz_icd}"
fi

exec uv run python -m gsp.qa.visual run --datoviz-color-pipeline legacy_srgb_blend "$@"
