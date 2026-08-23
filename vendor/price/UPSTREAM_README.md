# Erdős Problem 36 Lower Bound Certificate

This repository contains a proof note and reproducible certificate package for the theorem-target lower bound

```text
c_E > 0.38055470
```

for Erdős' minimum overlap problem.

## Contents

- `36-lower-bound.tex`: proof note reducing the result to the certified Arb verifier run.
- `minimum_overlap.pdf`: compiled PDF version of the proof note.
- `erdos36_0380554700_certificate_final.zip`: archival ZIP package of the certificate and generated verification reports.
- `certificate/`: expanded copy of the ZIP contents for direct inspection, diffing, and reproduction.

## Reproducing The Verification

From the expanded certificate directory:

```bash
cd certificate
python3 -m pip install -r requirements.txt
./run_arb_verification_chunks.sh
```

The script runs `prove_erdos_0380554275_arb.py` at target `0.38055470` on all 172 mean bins, then recombines the chunk reports with `combine_theorem_target_reports.py`.

The included aggregate report records:

```text
proved_all_bins: true
worst_bin_index: 85
worst_bin: [-0.003125, -0.0]
D_margin_decimal: 1.90758053837823039742128046631348729662496612824079541657320169741695477680343982087200604801359699407E-8
inverse_worst_D_upper_bound_decimal: 0.38055470276259401237458368772220489926456967965679470955827690763950453612958247345867463051771252116633685163
```

The optimizer used to find the certificate is not part of the trusted proof. The trusted inputs are the certificate JSON, the verifier, and Arb / `python-flint` ball arithmetic.

## Hashes

The expanded package includes `certificate/SHA256SUMS.txt` for its files. The ZIP uploaded here has SHA-256:

```text
4bb5526e4808c5c9300b0aa9385d06e2840c53ad6dc4dd2358f3d87b7aca5859
```
