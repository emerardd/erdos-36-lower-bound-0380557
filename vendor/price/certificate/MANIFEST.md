# Manifest

## Source / verifier files

- `erdos_aug_central_gridF400.json`: certificate file.
- `prove_erdos_0380554275_arb.py`: Arb verifier. Despite the historical name, it accepts an explicit `--target` argument and is run here with `0.38055470`.
- `run_arb_verification_chunks.sh`: three-chunk theorem-target reproduction script.
- `combine_theorem_target_reports.py`: exact-target report combiner; uses `m+r` for printed Arb balls.
- `combine_arb_reports.py`: historical combiner preserved unchanged for hash compatibility with the proof note; not used by the run script.
- `requirements.txt`: Python dependencies.

## Included theorem-target reports

- `arb_0_84_0380554700.csv`, `arb_0_84_0380554700.json`, `arb_0_84_0380554700.out`.
- `arb_85_88_0380554700.csv`, `arb_85_88_0380554700.json`, `arb_85_88_0380554700.out`.
- `arb_89_171_0380554700.csv`, `arb_89_171_0380554700.json`, `arb_89_171_0380554700.out`.
- `erdos_0380554700_theorem_target_per_bin.csv`: combined 172-bin CSV.
- `erdos_0380554700_theorem_target_aggregate.json`: combined aggregate report.
