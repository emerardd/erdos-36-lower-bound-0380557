# What is reproducible, and to how many digits

Read this before reporting a mismatch.

## Short version

Two things are asserted by this repository:

```text
integral of q_+ over [-2,2]  <=  2.6277192  <  1/0.380557
```

and the analogous inequality for the MPFR checker.  **Only the inequalities are
claims.**  The individual trailing digits printed by the Python checker are not,
and they are expected to differ between environments.

## Why the Python checker's last digits move

`code/verify_center_chunked.py` proposes its initial subdivision of `[0,2]` with
a floating-point root search (`numpy.linspace` sampling plus `scipy.optimize.
brentq`).  That search is explicitly outside the trusted path: a missed root is
still caught by the interval sign test and by bisection, so correctness does not
depend on it.  But the roots it returns *do* set the rational cell boundaries,
and different SciPy versions return roots that differ in the last bits.  The
accumulated upper bound `Dacc` is a sum over those cells, so its tail digits
move with them.

Observed, same certificate, same machine-independent logic:

| Environment | nodes / pos / neg / amb | `FINAL Dupper` |
|---|---|---|
| pinned `requirements.txt` (numpy 2.3.5, scipy 1.17.0) | 4851 / 1220 / 1118 / 175 | `2.6277191078658615742268756` |
| numpy 1.26.4, scipy 1.17.1 | 4851 / 1220 / 1118 / 175 | `2.62771910786586157416260956` |

The cell counts are identical and both bounds are below `1/0.380557` by more
than `8.1e-6`.  The certificate is unaffected.

If you want the exact digits recorded in `verification/center_result.txt` and
`verification/ci_center_mpmath.txt`, install the pinned versions from
`requirements.txt`.  If you get the same cell counts and `CERTIFIED True` with
different tail digits, that is a successful reproduction, not a discrepancy.

## The MPFR checker is bit-reproducible

`code/verify_center_mpfr.c` has no floating-point seeding.  It starts from a
fixed dyadic subdivision and uses only MPFR with explicit directed rounding, so
its output is deterministic:

```text
D_upper: 2.627722684051132572474851527168563565889667723367257198
```

identical at both 256-bit and 384-bit precision, and identical across machines
with the same MPFR major version.  A difference here *would* be worth
reporting.

## Vendored upstream reports

The Arb reports under `vendor/price/certificate/` are archived byte-for-byte
from upstream and are not regenerated here.  `code/check_vendored_price_reports.py`
re-reads their published ball strings with `Decimal` and checks that every
noncentral bin clears the stronger target; `.github/workflows/verify-global.yml`
additionally re-runs Price's Arb verifier from scratch at target `0.380557`.

## Hash manifests

`SHA256SUMS.txt` at the repository root covers this repository's own files.
`vendor/price/SHA256SUMS.txt` covers the redistributed package, and the upstream
`vendor/price/certificate/SHA256SUMS.txt` is Price's own manifest.  The last of
these was generated with CRLF line endings, so check it as:

```bash
cd vendor/price/certificate && sed 's/\r$//' SHA256SUMS.txt | sha256sum -c
```

The repository sets `* -text` in `.gitattributes`.  Without it, a clone on
Windows converts line endings on checkout and every one of these manifests
fails for reasons that have nothing to do with the mathematics.
