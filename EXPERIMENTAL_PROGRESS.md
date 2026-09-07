# Experimental progress: weighted spectral Parseval

This branch records a **numerical candidate**, not a new certified theorem.
The certified result on `main` remains `c_E > 0.380557` until an independent
interval verifier accepts a frozen certificate.

## Main idea

The current center certificate uses the hard Parseval prefix

\[
-\sum_{n=1}^{100} C_{n\pi} \le \frac12.
\]

The same Parseval argument gives a larger family of valid rows. Since

\[
C_{n\pi}=-|H(n\pi)|^2,\qquad
\sum_{n\ge1}|H(n\pi)|^2\le\frac12,
\]

for any fixed weights `0 <= w_n <= 1`,

\[
-\sum_n w_n C_{n\pi}\le\frac12.
\]

The experimental LP therefore learns a spectral window by writing
`a_n = lambda_W w_n` and imposing `0 <= a_n <= lambda_W`. After that first
search, the window is frozen and treated as one ordinary fixed linear row.
The final proof path would not need to trust the optimizer.

The search also includes the exact harmonic rows

\[
C_{n\pi}\le0,
\]

which follow directly from `C_{n*pi} = -|H(n*pi)|^2`.

## Numerical pipeline

`experiments/spectral_window_search.py` runs:

1. 801-point coarse LP to learn a 400-harmonic spectral window.
2. Freeze those weights.
3. Re-optimize ordinary cosine rows plus `C_{n*pi} <= 0` rows on 2001 points.
4. Prune rows with tiny multipliers.
5. Re-optimize the active set on 4001 points.
6. Locate continuous zeros of the resulting trigonometric polynomial `q` and
   integrate `q_+` using its explicit antiderivative.

The ordinary cosine candidate set used in this experiment consists of the
previously useful low-frequency values

`5.94, 8.4575, 12.375, 15.5725, 19.5425, 26.995, 34.175, 34.18, 41.745, 45.9, 53.0, 53.105, 60.34, 64.42, 65.0, 71.975, 79.125`

plus every integer frequency from 80 through 400.

## Current numerical candidate

A run of the pipeline in the development environment gave, after the final
4001-point active-set solve,

\[
D_{\rm grid}\approx 2.627701556627799,
\qquad
1/D_{\rm grid}\approx 0.38056072139460434.
\]

A separate continuous zero search and antiderivative integration gave

\[
D_{\rm cont}\approx 2.6277015651456788,
\qquad
\boxed{1/D_{\rm cont}\approx 0.38056072016098996}.
\]

There were 303 detected zeros of `q` on `[0,2]` in that continuous check.
The grid/continuous difference is about `1.2e-9` on the lower-bound side.

These numbers are **not interval rigorous**. They should be read as evidence
that a target around `0.3805607` is plausible, not as a proved lower bound.
Solver versions and tolerances may also change the last digits.

## What did not help much

Two additional structural inequalities were tested before this branch was
created:

- the pointwise envelope `p(t)+p(-t) <= 2-|t|`;
- the absolute-moment row `int |t| p(t) dt >= 2/3`.

For the current even center relaxation, their numerical effect was negligible
compared with expanding the Fourier active set and replacing the hard
Parseval cutoff by a spectral window.

## Certification plan

The next step is to turn the numerical candidate into a finite proof object:

1. Freeze every window weight and dual multiplier as an exact decimal/rational
   string.
2. Extend the existing Python interval verifier with a `weighted_parseval` row
   and the exact `harmonic_cos_nonpositive` rows.
3. Recompute all ordinary cosine right-hand sides with outward rounding.
4. Check `0 <= w_n <= 1` exactly/interval-rigorously.
5. Interval-integrate the positive part of the frozen `q`.
6. First attempt the conservative theorem target `c_E > 0.38056068`; if the
   interval margin survives comfortably, try `c_E > 0.3805607`.
7. Mirror the accepted certificate in the independent MPFR verifier before
   changing the theorem statement on `main`.

The numerical value `0.380560720...` must **not** be advertised as certified
until those steps pass.
