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
The center certificate uses

- the exact second-moment row;
- 80 ordinary cosine rows;
- one fixed weighted Parseval row
  `-sum_{n=1}^{400} w_n C_{n*pi} <= 1/2`, with `0 <= w_n <= 1`;
- 216 exact harmonic rows `C_{n*pi} <= 0`.

The weighted row is a direct consequence of the existing Parseval energy bound
`sum |H(n*pi)|^2 <= 1/2`; the novelty is the optimized non-rectangular spectral
window inside Price's mean-conditioned certificate framework.

## Two interval verification paths

Both implementations verify the same frozen proof object. They were developed
within this project and therefore do **not** constitute an external third-party
audit.

### Direct MPFR/C

`code/verify_weighted_center_mpfr.c` uses MPFR directed rounding, sixth-order
Taylor sign enclosures with a seventh-derivative remainder, and an explicit
antiderivative on cells proved positive. It uses no `mpmath`, NumPy, SciPy,
Arb, root finder, or LP solver.

A full 32-piece reproduction gives

```text
D_upper: 2.627701565496540078311925225882431013359788494257...
target:  0.38056070
margin_D: 1.38857062382478166867179201467e-7
CERTIFIED True
```

The C verifier reads `certificate/weighted_center_coefficients_038056070.txt`, a
compact terminating-decimal transcription of the frozen JSON proof object;
`code/check_weighted_mpfr_certificate_match.py` checks that transcription
against the JSON before the C verifier is accepted.

### Independent `mpmath.iv`

`code/verify_weighted_center_mpmath.py` reconstructs the certificate separately
using `mpmath.iv`. It uses third-order Taylor enclosures on the main mass and
sixth-order enclosures in the high-frequency tail. Floating root searches, when
used to propose subdivisions, are outside the trusted path: every cell is still
validated by interval arithmetic.

The archived verification gives

```text
D_upper: 2.62770156515276293334556455703
target_D: 2.62770170435360246079009209306...
margin_D: 1.39200839527444527536031632481e-7
CERTIFIED True
```

The implied reciprocal of that certified upper bound is approximately
`0.380560720159964`, so the theorem target deliberately keeps margin.

## Noncentral bins

The other 170 bins reuse Price's published Arb-certified balls. The largest
noncentral `D` upper bound is approximately

```text
2.6275385308733757900902721758784
```

corresponding to a reciprocal about `0.3805843333`, so the new global bottleneck
remains the two center bins. `code/check_noncentral_target.py` checks all 170
vendored Arb balls against `0.38056070`.

## Frozen proof object

- `certificate/weighted_center_certificate_038056070.json` - exact decimal
  multipliers and the 400 fixed spectral weights.
- `verification/weighted_038056070_mpmath_manifest.csv` - exact 32-piece
  coverage used by the independent Python verifier.
- `verification/weighted_038056070_mpmath_result.txt` - archived Python interval
  transcript summary.
- `verification/weighted_038056070_mpfr_result.txt` - archived direct-MPFR
  reproduction summary.

The LP/search code under `experiments/` is exploratory and is not part of the
trusted proof path.

## Reproduce the center certificate

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt

python code/run_weighted_mpmath_verification.py --jobs 8
```

For the direct MPFR path, install a C compiler plus MPFR/GMP development
headers (`libmpfr-dev libgmp-dev` on Debian/Ubuntu, `brew install mpfr` on
macOS), then run

```bash
python code/check_weighted_mpfr_certificate_match.py
python code/run_weighted_mpfr_verification.py --jobs 8
```

The supported release/CI path compiles against the real `<mpfr.h>`. A guarded
`MPFR_SELFDECL` fallback exists only for LP64 Linux development environments
that have the runtime library but not the header; CI rejects that fallback as
an authoritative release check.

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

## Paper and reproducible release

- `paper.tex` - proof note source. CI builds `paper.pdf` reproducibly; the PDF is
  attached to releases rather than kept as a tracked source artifact.
- `code/build_paper.sh` - reproducible pdfTeX build with a pinned
  `SOURCE_DATE_EPOCH`.
- `arxiv-source.zip` - generated by CI/release from the final `paper.tex` and
  attached as an artifact; the ZIP is not tracked in git.
- `SHA256SUMS.txt` - generated by clean-checkout CI after verification and
  attached to the release artifact bundle; it is intentionally not tracked in
  git, so it cannot go stale relative to the commit it describes.
- `vendor/price/` - pinned upstream Price package with its own provenance and
  manifests.

The repository's MIT license does not relicense `vendor/price/`; see `LICENSE`
and `vendor/price/README.md`.

## Trust model

The trusted path consists of the frozen certificate, rigorous interval
arithmetic in either verifier, exact aggregation of chunk bounds, and the
vendored noncentral Arb reports. The LP optimizer, exploratory frequency search,
and ordinary floating-point continuous integration are not needed to verify the
theorem.

The two verifier implementations are separate code paths but were produced
within the same project. External reproduction by another researcher is still
welcome and should be described separately from this internal dual verification.

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

Zenodo concept DOI (always resolves to the latest archived version):

```text
10.5281/zenodo.22279894
```

A version-specific DOI for this `0.38056070` release should be inserted only
after Zenodo creates the new release record; it is intentionally not prefilled
here.
