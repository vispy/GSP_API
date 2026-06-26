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
  datoviz_icd=""
  if [[ -n "${VK_ICD_FILENAMES:-}" && -f "${VK_ICD_FILENAMES%%:*}" ]]; then
    datoviz_icd="${VK_ICD_FILENAMES%%:*}"
  else
    datoviz_icd_candidates=(
      "${DATOVIZ_REPO}/libs/vulkan/macos_arm64/MoltenVK_icd.json"
      "${DATOVIZ_REPO}/libs/vulkan/macos/MoltenVK_icd.json"
    )
    if [[ -n "${VULKAN_SDK:-}" ]]; then
      datoviz_icd_candidates+=(
        "${VULKAN_SDK}/share/vulkan/icd.d/MoltenVK_icd.json"
        "${VULKAN_SDK}/etc/vulkan/icd.d/MoltenVK_icd.json"
      )
    fi
    for prefix in /opt/homebrew /usr/local; do
      datoviz_icd_candidates+=(
        "${prefix}/share/vulkan/icd.d/MoltenVK_icd.json"
        "${prefix}/etc/vulkan/icd.d/MoltenVK_icd.json"
      )
    done
    for candidate in "${datoviz_icd_candidates[@]}"; do
      if [[ -f "${candidate}" ]]; then
        datoviz_icd="${candidate}"
        break
      fi
    done
  fi

  if [[ -z "${datoviz_icd}" ]]; then
    echo "Datoviz MoltenVK ICD not found in VK_ICD_FILENAMES, Datoviz, VULKAN_SDK, or Homebrew paths." >&2
    echo "Install/configure MoltenVK, set VK_ICD_FILENAMES, or set VULKAN_SDK, then retry." >&2
    exit 2
  fi

  datoviz_vulkan_dir="$(cd "$(dirname "${datoviz_icd}")/../../.." && pwd -P)"
  datoviz_library_dirs=(
    "${datoviz_vulkan_dir}/lib"
    "${DATOVIZ_REPO}/libs/vulkan/macos_arm64"
    "${DATOVIZ_REPO}/libs/vulkan/macos"
  )
  if [[ -n "${VULKAN_SDK:-}" ]]; then
    datoviz_library_dirs+=("${VULKAN_SDK}/lib")
  fi
  datoviz_library_dirs+=(/opt/homebrew/lib /usr/local/lib)
  for lib_dir in "${datoviz_library_dirs[@]}"; do
    if [[ -d "${lib_dir}" ]]; then
      case ":${DYLD_LIBRARY_PATH:-}:" in
        *:"${lib_dir}":*) ;;
        *) export DYLD_LIBRARY_PATH="${lib_dir}${DYLD_LIBRARY_PATH:+:${DYLD_LIBRARY_PATH}}" ;;
      esac
      case ":${DYLD_FALLBACK_LIBRARY_PATH:-}:" in
        *:"${lib_dir}":*) ;;
        *) export DYLD_FALLBACK_LIBRARY_PATH="${lib_dir}${DYLD_FALLBACK_LIBRARY_PATH:+:${DYLD_FALLBACK_LIBRARY_PATH}}" ;;
      esac
    fi
  done
  export VK_ICD_FILENAMES="${datoviz_icd}"
fi

exec uv run python -m gsp.qa.visual review-pack \
  --mode datoviz-offscreen-opt-in \
  --datoviz-color-pipeline legacy_srgb_blend \
  "$@"
