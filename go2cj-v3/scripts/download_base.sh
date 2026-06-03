#!/usr/bin/env bash
# Download the codet5p-220m pretrained base model (220M params, T5+ enc-dec,
# pretrained on a large multi-language code corpus including Go) into
# go2cj-v3/base_model/.
#
# Source: https://github.com/SunriseSummer/CangjieSDK/releases/tag/1.0.5
# (mirror of https://huggingface.co/Salesforce/codet5p-220m — needed because
#  huggingface.co is not reachable from the sandbox).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
DEST="${HERE}/base_model"
URL="https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/codet5p-220m.zip"

if [[ -f "${DEST}/config.json" ]] && \
   { [[ -f "${DEST}/pytorch_model.bin" ]] || [[ -f "${DEST}/model.safetensors" ]]; }; then
  echo "[download_base] base model already present at ${DEST}"
  exit 0
fi

mkdir -p "${DEST}"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

echo "[download_base] fetching ${URL}"
curl -fsSL "${URL}" -o "${TMP}/codet5p-220m.zip"

echo "[download_base] extracting"
unzip -q "${TMP}/codet5p-220m.zip" -d "${TMP}/extract"
# The archive contains the files at top level.
src_root="${TMP}/extract"
if [[ ! -f "${src_root}/config.json" ]]; then
  # Some archives wrap into a sub-directory; pick the first one that has config.json.
  src_root="$(find "${TMP}/extract" -maxdepth 3 -name config.json -printf '%h\n' | head -1)"
fi
cp -r "${src_root}/." "${DEST}/"

echo "[download_base] OK; base model installed at ${DEST}"
ls "${DEST}"
