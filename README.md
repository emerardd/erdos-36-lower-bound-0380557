# Erdős #36: certified lower-bound package for `c_E > 0.380557`

This repository package contains a proof note and a machine-checkable center-bin
certificate for the lower bound

```text
c_E > 0.380557
```

for Erdős' minimum-overlap problem.

## Status

The center certificate has now been verified by **two separate interval-arithmetic implementations**.
The original 45-decimal-digit `mpmath.iv` checker returns:

```text
FINAL Dupper 2.6277191078658615742268756
TARGET 2.6277272524221075949200776756175815975...
MARGIN 0.0000081445562460206932020756175815975...
CERTIFIED True
```

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

- `paper.tex` / `paper.pdf` - complete proof note.
- `certificate/center_certificate.json` - 69 nonzero exact-decimal dual multipliers.
- `code/verify_center_chunked.py` - interval verifier, checkpointed in short chunks.
- `code/run_center_verification.py` - one-command wrapper for the Python verifier.
- `code/verify_center_mpfr.c` - independent MPFR/C verifier.
- `code/run_mpfr_verification.sh` - compile-and-run wrapper for the MPFR verifier.
- `verification/center_verification_full.log` - fresh 45-digit verification transcript.
- `verification/PRICE_DEPENDENCY.md` - exact statement of what is reused from Price.
- `PUBLICATION_CHECKLIST.md` - staged release instructions.
- `CITATION.cff` - citation metadata for this repository.
- `LICENSE` - MIT license for the verification code and repository utilities.
- `SHA256SUMS.txt` - hashes for the release files.

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

On the tested Linux x86-64 path, only a C compiler and the MPFR runtime library
are needed.  The release was tested with MPFR 4.2.2.

```bash
bash code/run_mpfr_verification.sh
```

The script performs both a 256-bit and a 384-bit run and requires each to end in
`CERTIFIED True`.  The source intentionally avoids a root finder and does not
share an interval library with the Python checker.

## References

- Ethan P. White, *A new bound for Erdős' minimum overlap problem*, Acta Arith.
  208 (2023), 235-255, DOI 10.4064/aa220728-7-6.
- Liam Price, public Arb certificate for `c_E > 0.38055470` (2026-06-29):
  https://github.com/Leeham06972452/erdos-36-lower-bound
- Independent audit of Price's certificate:
  https://github.com/occisn/erdos-36-certified-lower-bound


## Repository

Canonical repository: https://github.com/emerardd/erdos-36-lower-bound-0380557

The repository may remain private during pre-publication review. Public release should be made only after the verification package has been frozen and external reproduction has been invited.
