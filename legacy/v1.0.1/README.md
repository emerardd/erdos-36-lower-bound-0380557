# Legacy v1.0.1 proof package (`c_E > 0.380557`)

This directory preserves the proof objects, verifier sources, and archived outputs used by releases `v1.0.0` and `v1.0.1` for the earlier certified bound

```text
c_E > 0.380557
```

They are retained for provenance and historical reproducibility only. They are **not** part of the trusted proof path for the current `v1.1.0` theorem `c_E > 0.38056070`.

The current proof path lives at repository root and uses:

- `certificate/weighted_center_combined_038056070.txt`
- `code/check_weighted_combined_certificate.py`
- `code/verify_weighted_center_mpfr.c`
- `code/run_weighted_mpfr_verification.py`
- `verification/weighted_038056070_center_manifest.csv`
- `verification/weighted_038056070_mpfr_result.txt`

For the exact historical release state, the immutable Git tags `v1.0.0` and `v1.0.1` remain authoritative.
