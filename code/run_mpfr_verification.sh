#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CC="${CC:-gcc}"
SRC="$HERE/verify_center_mpfr.c"
python "$HERE/check_mpfr_certificate_match.py"
TMP="${TMPDIR:-/tmp}/erdos36_verify_center_mpfr"

# Decide the build mode ONCE, by probing for a usable <mpfr.h>, rather than by
# retrying after a failed compile.  Retrying would let a genuine error in
# verify_center_mpfr.c silently demote the build to the fallback ABI instead of
# reporting it, which is exactly the failure this verifier must not hide.
LINK_LIBS=""
if printf '#include <mpfr.h>\nint main(void){mpfr_t x;mpfr_init2(x,64);mpfr_clear(x);return 0;}\n' \
     | "$CC" -x c - -o /dev/null -lmpfr -lgmp -lm 2>/dev/null; then
  LINK_LIBS="-lmpfr -lgmp -lm"
elif printf '#include <mpfr.h>\nint main(void){mpfr_t x;mpfr_init2(x,64);mpfr_clear(x);return 0;}\n' \
       | "$CC" -x c - -o /dev/null -lmpfr -lm 2>/dev/null; then
  LINK_LIBS="-lmpfr -lm"
fi

if [ -n "$LINK_LIBS" ]; then
  # Supported path: the compiler type-checks every call against the installed
  # MPFR.  Works on Linux and macOS alike.
  MODE_FLAGS=""
  echo "Using <mpfr.h> with: $LINK_LIBS"
else
  # Convenience path for header-less machines.  It hard-codes the mpfr_t layout
  # for the LP64 Linux ABI, where a mismatch is silent memory corruption rather
  # than a compile error, so it is announced loudly and rejected by CI.
  MODE_FLAGS="-DMPFR_SELFDECL"
  LINK_LIBS="-Wl,-l:libmpfr.so.6 -lm"
  echo "WARNING: <mpfr.h> not usable; falling back to self-declared MPFR ABI." >&2
  echo "WARNING: this assumes MPFR 4.x on the LP64 Linux ABI, and is not a" >&2
  echo "WARNING: supported verification path.  Install libmpfr-dev." >&2
fi

build_run () {
  local prec="$1"
  local exe="${TMP}_${prec}"
  echo "== MPFR ${prec}-bit run =="
  # Compiler diagnostics are deliberately NOT suppressed here.
  "$CC" -O3 -DPREC="$prec" $MODE_FLAGS "$SRC" -o "$exe" $LINK_LIBS
  output="$($exe --base-depth 7 --terminal-depth 14 --max-nodes 500000 2>&1)"
  printf '%s\n' "$output"
  printf '%s\n' "$output" | grep -q 'CERTIFIED True'
  rm -f "$exe"
}

build_run 256
build_run 384

echo "Both MPFR runs certified the target."
