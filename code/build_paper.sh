#!/usr/bin/env bash
# Build paper.pdf reproducibly.
#
# pdfTeX stamps a creation time and a trailer ID into the PDF, so an ordinary
# build produces a different file every time and its SHA-256 in the root
# manifest could never be checked. Pinning SOURCE_DATE_EPOCH (with
# FORCE_SOURCE_DATE=1, which also overrides \pdfcreationdate) makes the output
# byte-identical across builds and machines.
#
# The epoch below is fixed to the paper's date, 7 September 2026 00:00:00 UTC.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export SOURCE_DATE_EPOCH=1788739200
export FORCE_SOURCE_DATE=1
pdflatex -interaction=nonstopmode -halt-on-error paper.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error paper.tex >/dev/null
if grep -qE 'Rerun to get|undefined (references|citations)' paper.log; then
  pdflatex -interaction=nonstopmode -halt-on-error paper.tex >/dev/null
fi
rm -f paper.aux paper.log paper.out paper.synctex.gz
echo "Built paper.pdf: $(sha256sum -b paper.pdf)"
