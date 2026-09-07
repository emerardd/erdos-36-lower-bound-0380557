#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
JOBS="${JOBS:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)}"
if [ "$JOBS" -gt 8 ]; then JOBS=8; fi

echo '== frozen certificate sanity =='
python code/generate_weighted_mpfr_coefficients.py >/tmp/erdos36_coefficients_preview.txt
grep -q 'GENERATED True' /tmp/erdos36_coefficients_preview.txt

echo '== 170 noncentral Arb balls =='
python code/check_noncentral_target.py \
  vendor/price/certificate/erdos_0380554700_theorem_target_per_bin.csv \
  --target 0.38056070

echo '== independent mpmath.iv center verification =='
python code/run_weighted_mpmath_verification.py --jobs "$JOBS"

echo '== direct MPFR/C center verification =='
python code/run_weighted_mpfr_verification.py --jobs "$JOBS" --prec 192 --max-depth 20

echo 'GLOBAL CERTIFIED c_E > 0.38056070'
