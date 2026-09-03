#!/usr/bin/env bash
# Build paper.pdf reproducibly.
#
# pdfTeX stamps a creation time and a trailer ID into the PDF, so an ordinary
# build produces a different file every time and its SHA-256 in the root
# manifest could never be checked.  Pinning SOURCE_DATE_EPOCH (with
# FORCE_SOURCE_DATE=1, which also overrides \pdfcreationdate) makes the output
# byte-identical across builds and machines.
#
# The epoch below is fixed to the paper's date, 23 August 2026 00:00:00 UTC.
# Do not change it casually: changing it changes paper.pdf's hash.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export SOURCE_DATE_EPOCH=1787443200
export FORCE_SOURCE_DATE=1

# Two passes so the cross-references and hyperref anchors settle.
pdflatex -interaction=nonstopmode -halt-on-error paper.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error paper.tex >/dev/null

if grep -qE 'Rerun to get|undefined (references|citations)' paper.log; then
  echo 'paper.log still asks for another pass; running a third.' >&2
  pdflatex -interaction=nonstopmode -halt-on-error paper.tex >/dev/null
fi

rm -f paper.aux paper.log paper.out paper.synctex.gz
echo "Built paper.pdf: $(sha256sum -b paper.pdf)"
