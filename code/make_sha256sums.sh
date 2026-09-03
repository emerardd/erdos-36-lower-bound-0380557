#!/usr/bin/env bash
# Regenerate the root SHA256SUMS.txt.
#
# Covers the git-tracked files authored for this repository.  Excluded:
#   - SHA256SUMS.txt itself (a manifest cannot contain its own hash);
#   - vendor/, which carries its own manifests and is third-party material;
#   - verification/ci_*, verification/GLOBAL_CERTIFICATION_*, and
#     verification/VENDORED_PRICE_REPORT_CHECK_*, which are rewritten by CI on
#     every run and would make the manifest stale by construction.  The frozen
#     transcripts (center_result.txt, center_mpfr_*.txt) are covered.
#
# Hashes are taken in binary mode so the manifest is identical whether it is
# generated on Linux, macOS or Windows.  The repository sets `* -text` in
# .gitattributes, so a clone reproduces the hashed bytes on every platform.
#
# Run this after any content change and before tagging a release.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

git ls-files -z \
  | grep -zv '^vendor/' \
  | grep -zv '^SHA256SUMS\.txt$' \
  | grep -zv '^verification/ci_' \
  | grep -zv '^verification/GLOBAL_CERTIFICATION_' \
  | grep -zv '^verification/VENDORED_PRICE_REPORT_CHECK_' \
  | sort -z \
  | xargs -0 sha256sum -b > SHA256SUMS.txt

echo "Wrote SHA256SUMS.txt covering $(wc -l < SHA256SUMS.txt) files."
