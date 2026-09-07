# Publication checklist for the `c_E > 0.38056070` release

## A. Freeze and verify

- [x] Freeze `certificate/weighted_center_combined_038056070.txt` as the authoritative center proof object.
- [x] Verify the combined certificate exactly: nonnegative `T2`/`COS` multipliers, positive `WINDOW`, PI indices `1..400`, and `c_n <= lambda_W` for every PI coefficient.
- [x] Verify the center certificate with the direct-MPFR/C implementation from the frozen combined coefficients, without archived integral bounds as inputs.
- [x] Check all 170 vendored noncentral Arb balls against theorem target `0.38056070`.
- [x] Keep the LP/frequency search and historical JSON/mpmath experiments outside the trusted proof path.
- [ ] Obtain an external third-party reproduction before describing the new result as independently audited by another researcher.

## B. Repository release package

- [x] Update `paper.tex` to theorem target `c_E > 0.38056070` and include the weighted-Parseval lemma plus the combined-coefficient decomposition argument.
- [x] Update README and trust-model language to the standalone combined certificate + direct-MPFR path.
- [x] Update `CITATION.cff` and `.zenodo.json` for version `1.1.0`.
- [x] Add one-command `code/run_release_verification.sh`.
- [x] Configure CI to validate the combined certificate, verify the 170 noncentral bins, and rerun the center MPFR proof.
- [x] Require the release CI to use the real `<mpfr.h>` path.
- [x] Build `paper.pdf` reproducibly from the final source and attach it to the release rather than tracking it in git.
- [x] Build `arxiv-source.zip` from the final source and attach it rather than tracking it in git.
- [x] Generate the release `SHA256SUMS.txt` after verification in clean-checkout CI.

## C. Review before merge

- [ ] Read the locally rebuilt `paper.pdf` line by line, especially the sign conventions for `p_h`, `C_xi`, weighted Parseval, the combined decomposition, and the dual function.
- [ ] Review the PR diff for accidental changes under `vendor/price/` (there should be none).
- [ ] Confirm final CI is green on the exact head commit.
- [ ] Merge to `main` only after the final clean-checkout run succeeds.

## D. Release and archive

- [ ] Tag the merged release commit `v1.1.0`.
- [ ] Create the GitHub Release from exactly that tag.
- [ ] Let Zenodo archive the new GitHub release.
- [ ] Insert the new version-specific Zenodo DOI only after Zenodo creates it; keep concept DOI `10.5281/zenodo.22279894` meanwhile.
- [ ] If the paper is updated on arXiv, upload the release `arxiv-source.zip` from the tagged commit and inspect arXiv's generated PDF.

Suggested restrained release claim:

> We give a computer-assisted proof of `c_E > 0.38056070`. The center is certified by a standalone finite-decimal combined certificate and a directed-rounding MPFR verifier; the remaining 170 mean bins reuse Price's published Arb-certified bounds. External third-party reproduction is invited.
