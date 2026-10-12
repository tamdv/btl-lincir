#!/usr/bin/env bash
# [NHOM8] Zip the code needed on Kaggle -> dist/btl-lincir-code.zip
# Upload it once as a private Kaggle Dataset named "btl-lincir-code" (New Dataset -> drop the zip).
# After code changes: rerun this script and upload a "New Version" of that dataset.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
rm -f dist/btl-lincir-code.zip
zip -qr dist/btl-lincir-code.zip code scripts configs requirements.txt experiments/registry.csv \
  $(ls experiments/gap_delta_large.pt experiments/gap_clip_large.json 2>/dev/null) \
  -x "code/hf_models/*" "code/datasets/*" "*/__pycache__/*" "code/*.pt" "code/submission/*" "experiments/runs/*"
ls -lh dist/btl-lincir-code.zip
