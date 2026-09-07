# Weighted spectral-Parseval certification at 0.38056068

This branch contains an experimental strengthened certificate for the two central mean bins. The original theorem on `main` remains unchanged until the proof text and an independent second verifier are updated.

## Center bins 85 and 86

The new center certificate uses a fixed weighted Parseval row

\[
-\sum_{n=1}^{400} w_n C_{n\pi}\le \frac12,
\qquad 0\le w_n\le1,
\]

plus the second-moment row, ordinary cosine rows, and exact harmonic rows `C_{n*pi} <= 0`.

A root-seeded direct-MPFR verifier was run in 42 chunks covering `x in [0,2]`. Floating root locations only seed subdivisions; every accepted chunk is justified by directed-rounding interval evaluation, Taylor sign enclosures, and exact elementary antiderivative bounds for positive cells.

The 42 printed upward-rounded `Dhalf_upper` values form an exact, gap-free, non-overlapping cover on the common `DGRID=24` lattice. Exact rational aggregation gives

\[
D_{\rm half}\le
1.3138507825728395442428956748544499786830163606399557484440466310341,
\]

hence

\[
D\le
2.6277015651456790884857913497088999573660327212799114968880932620682.
\]

For the target

\[
C=0.38056068,
\qquad
1/C=2.6277018424499346595659856399247552322010776310363960880036266489748\ldots,
\]

the rigorous D-side margin is

\[
2.7730425557108019429021585527483504490975\times10^{-7}>0.
\]

Therefore the new center certificate clears `0.38056068`.

The reciprocal of the aggregated center D upper is about

\[
0.3805607201609899186452897932\ldots,
\]

but this is only headroom; the theorem target certified by this branch is the conservative decimal `0.38056068`.

## Remaining 170 mean bins

Bins 85 and 86 are replaced by the center certificate above. The vendored Price/Arb per-bin report is checked directly by `code/check_noncentral_target.py`.

Among the other 170 bins, the worst archived D upper occurs at the near-center outer bins 77/94. Bin 77 has

\[
D\in[2.627538530873375790090272175878307131812586378\pm8.26\times10^{-46}],
\]

so even its upper endpoint is far below `1/0.38056068`. Its reciprocal is about `0.3805843333028524`.

Thus the noncentral bins have ample margin and the new global bottleneck remains the weighted center certificate.

## Current status

Combining the new center certification with the existing rigorous Price/Arb noncentral certificates gives the experimental global target

\[
\boxed{c_E>0.38056068}.
\]

This branch should still be treated as experimental until:

1. the frozen weighted certificate and MPFR verifier are fully archived in-repo;
2. an independent second implementation reproduces the center bound;
3. the proof note is updated with the weighted-Parseval lemma and new theorem target.

Files already archived here:

- `verification/weighted_038056068_manifest.csv`
- `verification/weighted_038056068_aggregate.txt`
- `code/aggregate_weighted_mpfr_chunks.py`
- `code/check_noncentral_target.py`
