# Erdős #36: certified lower-bound package for `c_E > 0.380557`

This repository package contains a proof note and a machine-checkable center-bin
certificate for the lower bound

```text
c_E > 0.380557
```

for Erdős' minimum-overlap problem.

## Status

The center certificate has now been verified by **two separate interval-arithmetic implementations**.
The original 45-decimal-digit `mpmath.iv` checker returns, on the pinned
dependency versions in `requirements.txt`:

```text
FINAL Dupper 2.6277191078658615742268756
TARGET 2.6277272524221075949200776756175815975...
MARGIN 0.0000081445562460206932020756175815975...
CERTIFIED True
```

The asserted bound is `<= 2.6277192`; see "Note on digits" below before
comparing the tail against your own run.

A second checker, `code/verify_center_mpfr.c`, calls MPFR 4.x directly with
explicit downward/upward rounding.  It uses no `mpmath`, Arb, SciPy, or root
finder and returns, at both 256-bit and 384-bit precision:

```text
D_upper 2.627722684051132572474851527168563565889667723367257198
target_D_lower 2.627727252422107594920077675617581597500505837496091255
margin_lower 0.000004568370975022445226148449018031610838114128834058127384
CERTIFIED True
```

The MPFR bound is intentionally more conservative than the first verifier, but
still proves the theorem target.  The global proof reuses Liam Price's already
published Arb-certified bounds for all mean bins except the two central bins 85
and 86.  Those two bins are replaced by the certificate here.  External
third-party reproduction is still invited; the second implementation is an
independent code path written for this work, not a third-party audit.

## What is new, and what is not

The Parseval energy inequality used here is **not new**; it is already present in
White's Fourier-analytic approach.  The contribution is the hybrid certificate:
White's global Parseval energy row is inserted into Price's mean-conditioned
dual-certificate framework, allowing the two binding center bins to be improved.

## Files

- `paper.tex` / `paper.pdf` - complete proof note.  Rebuild the PDF with
  `bash code/build_paper.sh`, which pins `SOURCE_DATE_EPOCH` so the output is
  byte-identical to the hash in `SHA256SUMS.txt`.  A plain `pdflatex paper.tex`
  produces the same document but a different file, because pdfTeX stamps the
  build time into it.
- `certificate/center_certificate.json` - 69 nonzero exact-decimal dual multipliers.
- `code/verify_center_chunked.py` - interval verifier, checkpointed in short chunks.
- `code/run_center_verification.py` - one-command wrapper for the Python verifier.
- `code/verify_center_mpfr.c` - independent MPFR/C verifier.
- `code/run_mpfr_verification.sh` - compile-and-run wrapper for the MPFR verifier.
- `code/check_mpfr_certificate_match.py` - checks the constants embedded in the
  C verifier against the JSON certificate, string for string.
- `code/check_vendored_price_reports.py` - checks the archived upstream Arb
  balls against the stronger target.
- `code/make_sha256sums.sh` - regenerates the root `SHA256SUMS.txt`.
- `code/build_paper.sh` - reproducible build of `paper.pdf`.
- `verification/center_result.txt` - fresh 45-digit verification transcript.
- `verification/REPRODUCIBILITY_NOTES.md` - **what is reproducible and to how
  many digits.  Read this before reporting a mismatch.**
- `verification/PRICE_DEPENDENCY.md` - exact statement of what is reused from Price.
- `verification/MPFR_INDEPENDENT_VERIFICATION.md` - the second implementation.
- `PUBLICATION_CHECKLIST.md` - staged release instructions.
- `CITATION.cff` - citation metadata for this repository.
- `LICENSE` - MIT license for this repository's own code; see the scope note in
  that file, which excludes `vendor/`.
- `SHA256SUMS.txt` - hashes for this repository's own files.
- `vendor/price/` - redistributed upstream package; see below.

## Licensing and attribution

The MIT license covers only material authored for this repository: `paper.tex`,
`certificate/`, `code/`, `templates/`, and this repository's own verification
transcripts.

`vendor/price/` is a byte-for-byte redistribution of the `certificate/`
directory of Liam Price's public repository
`Leeham06972452/erdos-36-lower-bound`, pinned at the commit in
`vendor/price/UPSTREAM_COMMIT.txt`.  It is included so that the noncentral bins
of the theorem can be re-verified against exactly the bytes that were used.
That material is the work of its original author and is **not** covered by the
MIT license here; at the time of vendoring the upstream repository carried no
explicit license file, and no rights over it are claimed or granted by this
repository.  See `vendor/price/README.md` and the scope note in `LICENSE`.

## Note on digits

Only the inequalities are claimed, not the trailing digits of the Python
checker's printed bound.  The initial subdivision is proposed by a
floating-point root search that lies outside the trusted path, so the last few
digits move with the SciPy version while the cell counts and the certified
inequality do not.  The MPFR checker has no such seeding and is deterministic.
`verification/REPRODUCIBILITY_NOTES.md` gives the details and a measured
side-by-side comparison.

## Reproduce the new center certificate

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python code/run_center_verification.py
```

The LP optimizer is not needed.  The checker reconstructs every right-hand side
used by the new center certificate and treats the JSON multipliers as exact
decimal rationals.

## Reproduce the independent MPFR check

A C compiler and MPFR with its development header are needed; on Debian or
Ubuntu that is `libmpfr-dev libgmp-dev`, on macOS `brew install mpfr`.  The
release was tested with MPFR 4.2.2.

```bash
bash code/run_mpfr_verification.sh
```

The script performs both a 256-bit and a 384-bit run and requires each to end in
`CERTIFIED True`.  The source intentionally avoids a root finder and does not
share an interval library with the Python checker.

The verifier includes the real `<mpfr.h>`, so the compiler type-checks every
call against the MPFR you actually have.  For machines without the header the
source also carries hand-written declarations behind `-DMPFR_SELFDECL`, which
the wrapper falls back to automatically; that path hard-codes the `mpfr_t`
layout for the LP64 Linux ABI, announces itself loudly, and is rejected by CI.
Treat it as a convenience, not as a verification path.

## References

- Ethan P. White, *A new bound for Erdős' minimum overlap problem*, Acta Arith.
  208 (2023), 235-255, DOI 10.4064/aa220728-7-6.
- Liam Price, public Arb certificate for `c_E > 0.38055470` (2026-06-29):
  https://github.com/Leeham06972452/erdos-36-lower-bound
- Independent audit of Price's certificate:
  https://github.com/occisn/erdos-36-certified-lower-bound


## Repository

Canonical repository: https://github.com/emerardd/erdos-36-lower-bound-0380557

The verification package is frozen at the tagged release; external reproduction
is invited. If you reproduce, or fail to reproduce, any part of it, please open
an issue with your software stack, commit hash, and exact output.
