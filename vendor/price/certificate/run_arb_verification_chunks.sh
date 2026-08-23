#!/usr/bin/env bash
set -euo pipefail

# Reproduce the theorem-target verification for c > 0.38055470.
# Usage: ./run_arb_verification_chunks.sh [certificate.json]

CERT=${1:-erdos_aug_central_gridF400.json}
PYTHON=${PYTHON:-python3}
VERIFIER=${VERIFIER:-prove_erdos_0380554275_arb.py}
TARGET=0.38055470

$PYTHON "$VERIFIER" "$CERT" --target "$TARGET" --only-bins 0-84 \
  --csv arb_0_84_0380554700.csv \
  --json-report arb_0_84_0380554700.json \
  > arb_0_84_0380554700.out

$PYTHON "$VERIFIER" "$CERT" --target "$TARGET" --only-bins 85-88 \
  --csv arb_85_88_0380554700.csv \
  --json-report arb_85_88_0380554700.json \
  > arb_85_88_0380554700.out

$PYTHON "$VERIFIER" "$CERT" --target "$TARGET" --only-bins 89-171 \
  --csv arb_89_171_0380554700.csv \
  --json-report arb_89_171_0380554700.json \
  > arb_89_171_0380554700.out

$PYTHON combine_theorem_target_reports.py
