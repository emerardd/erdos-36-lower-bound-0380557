# Experimental progress: weighted spectral Parseval

This branch now contains a **rigorously certified experimental center bound** and a global consistency check against the vendored Price/Arb noncentral bins. The theorem on `main` remains unchanged pending an independent second implementation and proof-note update.

## Main idea

The current published center certificate uses the hard Parseval prefix

\[
-\sum_{n=1}^{100} C_{n\pi}\le\frac12.
\]

The same Parseval argument gives the larger valid family

\[
-\sum_n w_n C_{n\pi}\le\frac12,
\qquad 0\le w_n\le1,
\]

because

\[
C_{n\pi}=-|H(n\pi)|^2,
\qquad
\sum_{n\ge1}|H(n\pi)|^2\le\frac12.
\]

The numerical search learns a spectral window, freezes it as exact decimal data, then re-optimizes the remaining dual multipliers. Exact harmonic rows

\[
C_{n\pi}\le0
\]

are also included.

## Numerical search

`experiments/spectral_window_search.py` performs:

1. coarse LP search for a 400-harmonic spectral window;
2. freeze the window;
3. re-optimize ordinary cosine and harmonic rows;
4. prune inactive rows;
5. refine on a 4001-point grid;
6. locate continuous zeros of `q` and integrate `q_+` by explicit antiderivative.

The resulting floating candidate was

\[
D_{\rm cont}\approx2.62770156514568,
\qquad
1/D_{\rm cont}\approx0.38056072016099.
\]

## Rigorous MPFR certification

The frozen center certificate was evaluated with a direct-MPFR interval verifier using directed rounding and third-order Taylor sign enclosures. Floating root locations are used only to seed subdivisions; they have no logical role.

The half-domain `[0,2]` was split into 42 independent chunks on a common `DGRID=24` lattice. Every chunk produced a rigorous upward-rounded `Dhalf_upper`. `code/aggregate_weighted_mpfr_chunks.py` checks exact coverage with no gaps or overlaps and sums the printed decimal upper bounds exactly as rational numbers.

The aggregate is

\[
D_{\rm half}\le
1.3138507825728395442428956748544499786830163606399557484440466310341,
\]

hence

\[
\boxed{D\le2.6277015651456790884857913497088999573660327212799114968880932620682}.
\]

For the conservative target

\[
C=0.38056070,
\]

we have

\[
1/C-D\approx1.39207923\times10^{-7}>0.
\]

Therefore the same frozen center certificate rigorously clears

\[
\boxed{c_{\rm center}>0.38056070}.
\]

The archived aggregate file was originally evaluated at `0.38056068`; because its `D_upper` is itself rigorous, the stronger decimal target `0.38056070` follows by exact arithmetic without rerunning the interval integration. Even `0.38056072` is below the reciprocal of the certified `D_upper`, but with only about `1.1e-9` of D-side margin, so `0.38056070` is the preferred experimental theorem target.

## Noncentral bins

`code/check_noncentral_target.py` checks the vendored Price/Arb per-bin CSV after excluding the replaced center bins 85 and 86.

All 170 remaining bins clear the new target. The worst archived noncentral D upper occurs at bin 77/94 and is about

\[
2.627538530873376,
\]

corresponding to a reciprocal near

\[
0.3805843333.
\]

Thus the center certificate remains the global bottleneck.

## Current experimental global result

Combining the certified center bound with the existing rigorous noncentral Price/Arb bounds gives

\[
\boxed{c_E>0.38056070}
\]

**within this experimental branch's proof chain.**

The result should not replace the theorem on `main` until:

1. the frozen certificate and MPFR verifier source are fully archived in-repo;
2. an independent second verifier reproduces the center bound;
3. the proof note is updated with the weighted-Parseval lemma and new theorem target.

Relevant archived files currently include:

- `verification/weighted_038056068_manifest.csv`
- `verification/weighted_038056068_aggregate.txt`
- `verification/WEIGHTED_038056068_SUMMARY.md`
- `code/aggregate_weighted_mpfr_chunks.py`
- `code/check_noncentral_target.py`
