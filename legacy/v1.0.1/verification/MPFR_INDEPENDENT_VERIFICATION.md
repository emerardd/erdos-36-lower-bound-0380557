# Independent MPFR verification of the center certificate

A second implementation was written to reduce dependence on the first
`mpmath.iv` checker. It is `code/verify_center_mpfr.c`.

## Independence from the first checker

The MPFR verifier:

- calls `libmpfr.so.6` directly with `MPFR_RNDD` and `MPFR_RNDU`;
- does not import or call `mpmath`, NumPy, SciPy, Arb, or the Python verifier;
- uses no floating-point root search;
- starts from a dyadic partition of `[0,2]` and bisects ambiguous cells;
- certifies signs with a global `M2 >= sup |q''|` Taylor enclosure;
- integrates certified-positive cells using its own outward interval evaluation
  of the elementary antiderivative;
- charges terminal ambiguous cells by width times a certified upper bound.

The source expands the Parseval row into its 100 cosine modes. Before compilation,
`code/check_mpfr_certificate_match.py` compares every embedded decimal frequency
and multiplier against `certificate/center_certificate.json` as exact strings.
This closes the transcription gap between the machine-readable certificate and
the static C verifier.

## Reproduced runs

Test platform: Linux x86-64, MPFR 4.2.2.

Both 256-bit and 384-bit runs, with base dyadic depth 7 and terminal depth 14,
returned exactly the same printed bound and cell counts:

```text
M2_upper: 2946.949041231920116358738875923087247336127080484874312
D_upper: 2.627722684051132572474851527168563565889667723367257198
target_D_lower: 2.627727252422107594920077675617581597500505837496091255
margin_lower: 0.000004568370975022445226148449018031610838114128834058127384
nodes: 10092
positive_cells: 1009
negative_cells: 1164
ambiguous_terminal_cells: 2937
CERTIFIED True
```

The MPFR upper bound is weaker (larger) than the first checker's
`2.6277191078658615742268756`, as expected from its coarser quadratic Taylor
enclosure, but remains below `1/0.380557` by more than `4.5e-6`.

This is an independent *software implementation*, not an external third-party
audit. External reproduction remains desirable before using the phrase
"independently verified by another researcher".
