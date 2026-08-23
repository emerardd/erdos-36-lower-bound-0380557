# Erdős problem 36: final Arb certificate package for `c > 0.38055470`

This archive contains the reproducible computer-assisted certificate files for the theorem-target lower bound

```text
c_E > 0.38055470
```

## Trusted proof inputs

The mathematical proof uses only:

- `erdos_aug_central_gridF400.json` — dual certificate: mean bins and nonnegative multipliers.
- `prove_erdos_0380554275_arb.py` — Arb / `python-flint` verifier.

The optimizer that found the certificate is not included and is not part of the proof.

## Reproduce the verification

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run all theorem-target chunks and recombine them:

```bash
./run_arb_verification_chunks.sh
```

The script runs the verifier with `--target 0.38055470` on the bin ranges `0-84`, `85-88`, and `89-171`, then runs `combine_theorem_target_reports.py`.

## Expected combined result

The combined output file is:

```text
erdos_0380554700_theorem_target_aggregate.json
```

The included run records:

```text
proved_all_bins: true
worst_bin_index: 85
worst_bin: [-0.003125, -0.0]
worst_D_upper_ball: [2.62774311482846645939819018339449857080232449839865340139440 +/- 6.60e-61]
target_D_decimal: 2.6277431339042718431804941576073032339371974646483146838023548257320169741695477680343982087200604801359699407
D_margin_decimal: 1.90758053837823039742128046631348729662496612824079541657320169741695477680343982087200604801359699407E-8
inverse_worst_D_upper_bound_decimal: 0.38055470276259401237458368772220489926456967965679470955827690763950453612958247345867463051771252116633685163
```

`combine_theorem_target_reports.py` uses the upper endpoint `m+r` when reading a printed Arb ball `[m +/- r]`, rather than only the displayed midpoint.

## Included generated reports

- `arb_0_84_0380554700.{csv,json,out}`
- `arb_85_88_0380554700.{csv,json,out}`
- `arb_89_171_0380554700.{csv,json,out}`
- `erdos_0380554700_theorem_target_per_bin.csv`
- `erdos_0380554700_theorem_target_aggregate.json`

Rerunning the verifier will overwrite the chunk reports and may change wall-clock timing fields, so hashes of generated `.json` / `.out` report files may differ after a fresh run. The certificate and verifier hashes should remain fixed.

## Historical combiner file

`combine_arb_reports.py` is preserved unchanged from the previous archive so that its SHA-256 hash matches the hash already printed in the TeX proof note. It is not used by `run_arb_verification_chunks.sh`. The theorem-target recombination file is `combine_theorem_target_reports.py`.

## Hashes

See `SHA256SUMS.txt` for hashes of every file in this archive. The principal hashes are:

```text
a2c723d375073bd124c04a690200ca9bf8f598eac506656e1ac9a883e6f4f217  erdos_aug_central_gridF400.json
a825b28f0dd8b8db8f225bcd8af48374c013f2f59de97bdb3d8d8cd62a49f11e  prove_erdos_0380554275_arb.py
759f097684e7f3e678e67a47accdfc8189ef22687d07ac93b624a674fb2e3597  combine_arb_reports.py
```
