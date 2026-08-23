#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CC="${CC:-gcc}"
SRC="$HERE/verify_center_mpfr.c"
python "$HERE/check_mpfr_certificate_match.py"
TMP="${TMPDIR:-/tmp}/erdos36_verify_center_mpfr"

build_run () {
  local prec="$1"
  local exe="${TMP}_${prec}"
  echo "== MPFR ${prec}-bit run =="
  "$CC" -O3 -DPREC="$prec" "$SRC" -o "$exe" -Wl,-l:libmpfr.so.6 -lm
  output="$($exe --base-depth 7 --terminal-depth 14 --max-nodes 500000 2>&1)"
  printf '%s\n' "$output"
  printf '%s\n' "$output" | grep -q 'CERTIFIED True'
  rm -f "$exe"
}

build_run 256
build_run 384

echo "Both MPFR runs certified the target."
