# Publication checklist for the `c_E > 0.38056070` release

## A. Freeze and verify

- [x] Freeze `certificate/weighted_center_certificate_038056070.json`.
- [x] Verify every spectral weight satisfies `0 <= w_n <= 1` and every dual multiplier is nonnegative.
- [x] Verify the center certificate with the independent `mpmath.iv` implementation.
- [x] Verify the center certificate with the direct-MPFR/C implementation.
- [x] Verify the terminating-decimal coefficient transcription consumed by the C verifier matches the frozen JSON proof object.
- [x] Check all 170 vendored noncentral Arb balls against theorem target `0.38056070`.
- [x] Keep the LP/frequency search outside the trusted proof path.
- [ ] Obtain an external third-party reproduction before describing the new result as independently audited by another researcher.

## B. Repository release package

- [x] Update `paper.tex` to theorem target `c_E > 0.38056070` and include the weighted-Parseval lemma.
- [x] Update README and trust-model language.
- [x] Update `CITATION.cff` and `.zenodo.json` for version `1.1.0`.
- [x] Archive both verifier sources, runners, manifests, and result summaries.
- [x] Add one-command `code/run_release_verification.sh`.
- [x] Update CI to run the two center verifiers and noncentral target check.
- [ ] Confirm the PR CI uses the real `<mpfr.h>` path and ends in `CERTIFIED True` for all stages.
- [x] Rebuild `paper.pdf` reproducibly from the final source locally and in CI; attach it to the release rather than tracking it in git.
- [x] Repack `arxiv-source.zip` from the final source locally and in CI; attach it to the release rather than tracking it in git.
- [x] Configure clean-checkout CI to generate the release `SHA256SUMS.txt` after verification and upload it with the release artifacts, avoiding a stale tracked self-manifest.

## C. Review before merge

- [ ] Read `paper.pdf` line by line, especially sign conventions for `p_h`, `C_xi`, the weighted Parseval row, and the dual function.
- [ ] Review the PR diff for accidental changes under `vendor/price/` (there should be none).
- [ ] Confirm CI is green on the exact head commit.
- [ ] Keep PR as Draft until the previous three checks are complete.
- [ ] Merge to `main` only after the frozen package is internally reproducible from a clean checkout.

## D. Release and archive

- [ ] Tag the merged release commit `v1.1.0`.
- [ ] Create the GitHub Release from exactly that tag.
- [ ] Let Zenodo archive the new GitHub release.
- [ ] Insert the new version-specific Zenodo DOI only after Zenodo creates it; keep concept DOI `10.5281/zenodo.22279894` meanwhile.
- [ ] If the paper is updated on arXiv, upload the CI/release `arxiv-source.zip` from the tagged commit and inspect arXiv's generated PDF.

Suggested restrained release claim:

> We give a computer-assisted proof of `c_E > 0.38056070`. The frozen center certificate is checked by two separate interval-arithmetic implementations developed within the project, and the remaining 170 mean bins reuse Price's published Arb-certified bounds. External third-party reproduction is invited.
