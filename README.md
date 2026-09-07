# Erdős #36: certified lower-bound package for `c_E > 0.38056070`

This repository contains a computer-assisted proof package for

```text
c_E > 0.38056070
```

for Erdős' minimum-overlap problem.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22279894.svg)](https://doi.org/10.5281/zenodo.22279894)

## Result

The proof keeps Liam Price's Arb-certified bounds for 170 noncentral mean bins
and replaces the two binding center bins with a stronger frozen dual certificate.
The center proof object is stored in combined spectral form. It contains

- the exact second-moment multiplier;
- 80 nonnegative ordinary cosine multipliers;
- one positive weighted-Parseval budget `lambda_W`;
- 400 exact combined harmonic coefficients `c_n`, each satisfying
  `c_n <= lambda_W`.

The last condition is enough to recover a valid weighted-Parseval/harmonic-row
decomposition. For `c_n >= 0`, take `w_n = c_n/lambda_W` and harmonic
multiplier `eta_n = 0`; for `c_n < 0`, take `w_n = 0` and
`eta_n = -c_n`. Hence `0 <= w_n <= 1`, `eta_n >= 0`, and
`c_n = lambda_W*w_n - eta_n` exactly. This is checked with exact rational
arithmetic before interval verification.

The weighted Parseval row itself is the consequence
`-sum w_n C_{n*pi} <= 1/2` of White's Parseval energy bound. The improvement
comes from using a frozen non-rectangular spectral combination inside Price's
mean-conditioned certificate framework.

## Certified center verification

`code/check_weighted_combined_certificate.py` validates the standalone
finite-decimal proof object
`certificate/weighted_center_combined_038056070.txt`, including all multiplier
sign conditions, the exact PI index set `1..400`, and `c_n <= lambda_W` for every
combined coefficient.

`code/verify_weighted_center_mpfr.c` then uses MPFR directed rounding,
sixth-order Taylor sign enclosures with a seventh-derivative remainder, and an
explicit antiderivative on cells proved positive. Archived integral values are
not trusted inputs: `code/run_weighted_mpfr_verification.py` recomputes all 32
center subintervals and aggregates the printed upward-rounded bounds as exact
rationals.

The clean-checkout release verification gives

```text
D_upper: 2.627701565496540078311925225882434229578618824422997827900570...
target_D: 2.627701704353602460790092093061632480705443310357585531033551...
margin_D: 0.000000138857062382478166867179198251126824485934587703132981...
CERTIFIED True
```

Thus the center certificate proves `c_E > 0.38056070` with a positive rigorous
margin. Earlier JSON-decomposition and `mpmath.iv` experiments were useful
during development but are not part of the release proof path.

## Noncentral bins

The other 170 bins reuse Price's published Arb-certified balls. The largest
noncentral `D` upper bound is approximately

```text
2.6275385308733757900902721758784
```

corresponding to a reciprocal about `0.3805843333`, so the new global bottleneck
remains the two center bins. `code/check_noncentral_target.py` checks all 170
vendored Arb balls against `0.38056070`.

## Current proof package

The files below are the current trusted path for `v1.1.0`:

- `paper.pdf` - the CI-built PDF corresponding to the current proof note.
- `paper.tex` - proof note source.
- `certificate/weighted_center_combined_038056070.txt` - authoritative
  finite-decimal center certificate: `T2`, `WINDOW`, 80 `COS` rows, and 400
  combined `PI` coefficients.
- `verification/weighted_038056070_center_manifest.csv` - exact 32-piece
  partition of `[0,2]` used to schedule rigorous MPFR subproblems.
- `verification/weighted_038056070_mpfr_result.txt` - archived current MPFR
  result summary.
- `verification/RELEASE_VERIFICATION_038056070.txt` - full clean-checkout CI
  transcript used for the `v1.1.0` release.
- `code/check_weighted_combined_certificate.py` - exact-rational certificate
  validity check.
- `code/verify_weighted_center_mpfr.c` and
  `code/run_weighted_mpfr_verification.py` - rigorous center verifier and exact
  aggregator.
- `code/check_noncentral_target.py` - checks the 170 retained Price/Arb bins.

The LP/search code under `experiments/` is exploratory and is not part of the
trusted proof path.

## Reproduce the current certificate

Python 3.10+ and a C compiler are required. Install MPFR/GMP development
headers (`libmpfr-dev libgmp-dev` on Debian/Ubuntu, `brew install mpfr` on
macOS), then run

```bash
python code/check_weighted_combined_certificate.py
python code/run_weighted_mpfr_verification.py --jobs 8
```

The supported release/CI path compiles against the real `<mpfr.h>`. A guarded
`MPFR_SELFDECL` fallback exists only for LP64 Linux development environments
that have the runtime library but not the header; CI rejects that fallback as an
authoritative release check.

To check the noncentral splice:

```bash
python code/check_noncentral_target.py \
  vendor/price/certificate/erdos_0380554700_theorem_target_per_bin.csv \
  --target 0.38056070
```

Or run the complete release verification after dependencies are installed:

```bash
bash code/run_release_verification.sh
```

## Paper and release artifacts

- `paper.pdf` is tracked at repository root for convenient reading. The tracked
  bytes are copied from the successful clean-checkout `v1.1.0` CI artifact.
- `code/build_paper.sh` reproducibly builds the PDF from `paper.tex` with a
  pinned `SOURCE_DATE_EPOCH`.
- `arxiv-source.zip` is generated by CI/release from the final `paper.tex` and
  remains a GitHub Release asset rather than a tracked Git file.
- `SHA256SUMS.txt` for a release is generated by clean-checkout CI after all
  proof checks pass and remains attached to that GitHub Release, avoiding a
  stale self-referential manifest in the repository root.
- `vendor/price/` is the pinned upstream Price package with its own provenance
  and manifests.

The repository's MIT license does not relicense `vendor/price/`; see `LICENSE`
and `vendor/price/README.md`.

## Historical material

The previous `v1.0.0` / `v1.0.1` proof package for

```text
c_E > 0.380557
```

is preserved under `legacy/v1.0.1/` for provenance and historical
reproducibility. It is not part of the current trusted proof path. The immutable
Git tags `v1.0.0` and `v1.0.1` remain the authoritative snapshots of those
releases.

## Trust model

The trusted path consists of the standalone combined center certificate, its
exact-rational validity checker, the direct-MPFR interval verifier with exact
chunk aggregation, and the vendored noncentral Arb reports. The LP optimizer,
exploratory frequency search, ordinary floating-point continuous integration,
and historical Python interval experiments are not needed to verify the
current theorem.

The center verifier was developed within this project; it is not a third-party
audit. External reproduction by another researcher remains desirable and
should be described separately if obtained.

## References

- Ethan P. White, *A new bound for Erdős' minimum overlap problem*, Acta Arith.
  208 (2023), 235-255, DOI 10.4064/aa220728-7-6.
- Liam Price, public Arb certificate for `c_E > 0.38055470` (2026-06-29):
  https://github.com/Leeham06972452/erdos-36-lower-bound
- Independent audit of Price's certificate:
  https://github.com/occisn/erdos-36-certified-lower-bound

## Archive

Canonical repository:
https://github.com/emerardd/erdos-36-lower-bound-0380557

GitHub release `v1.1.0` contains the arXiv source ZIP, release SHA-256 manifest,
and the same verification transcript archived here.

Zenodo concept DOI (always resolves to the latest archived version):

```text
10.5281/zenodo.22279894
```

A version-specific DOI for this `0.38056070` release should be inserted only
after Zenodo creates the new release record; it is intentionally not prefilled
here.
