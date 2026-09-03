# Publication checklist

Do these in order. Do not skip directly to an arXiv announcement.

## Stage A - freeze and independently verify the result

1. Read `paper.pdf` yourself line by line. In particular verify the sign
   conventions in `p_h`, `C_xi`, and the Parseval row.
2. Run `python code/run_center_verification.py` on a clean environment and save
   the terminal output.
3. **DONE locally:** run the independent MPFR/C verifier.  It uses a separate
   interval library and different subdivision logic; both 256-bit and 384-bit
   runs end in `CERTIFIED True`.  Keep the transcripts under `verification/`.
4. Recommended before the broad announcement: rerun Liam Price's public Arb
   checker on noncentral bins 0-84 and 87-171, or have a third party reproduce
   them.  This is not mathematically required for the splice because the
   published Arb `D` upper bounds are target-independent and already lie below
   `1/0.380557`, but a fresh run improves the audit trail.
5. Obtain at least one **external** reproduction of the new center certificate
   before describing the result as independently verified by another researcher.
   Until then, say that two independent software implementations verify it.

## Stage B - prepare the GitHub repository

6. **DONE:** repository created as `emerardd/erdos-36-lower-bound-0380557`. It may remain private during pre-publication review; switch it to public before broad announcement and DOI archiving.
7. Copy the contents of this release package into the repository.
8. **DONE:** author information and canonical repository URL are filled in at root `CITATION.cff`.
9. **DONE:** MIT license added, with a scope note excluding `vendor/`.  The
    vendored upstream package is redistributed unmodified, with attribution, and
    no rights over it are claimed; see `LICENSE` and `vendor/price/README.md`.
    Upstream carried no license file at the time of vendoring.  Ask the upstream
    author to add one when convenient, and honour any preference they express
    about the redistribution.  State the paper/certificate license separately if
    desired (for example CC BY 4.0).
10. Compile `paper.tex` locally to produce `paper.pdf`, run both verifiers,
    regenerate the root manifest with `bash code/make_sha256sums.sh`, repack
    `arxiv-source.zip` from the final `paper.tex`, commit, and tag the exact
    verified commit `v1.0.0`.
11. Create a GitHub Release from `v1.0.0`. Do not alter the certificate after
    tagging; if anything changes, make `v1.0.1` or `v1.1.0`.

## Stage C - get external eyes before the broad announcement

12. Send the release link privately to Liam Price, the maintainer of
    `occisn/erdos-36-certified-lower-bound`, and ideally Ethan P. White. A review
    request template is included under `templates/`.
13. If somebody independently reproduces the result, record their name/handle,
    software stack, commit hash, and exact output in `verification/` (with their
    permission). If they find a bug, fix it before any arXiv claim.

## Stage D - archive the exact code/certificate release

14. Create a Zenodo account and link GitHub.
15. Enable the repository in Zenodo's GitHub integration.
16. Make sure `CITATION.cff` contains the final author, title and version.
17. Archive the GitHub `v1.0.0` release in Zenodo. Zenodo will create a persistent
    software record and DOI. Record that DOI in the README and, if desired, in a
    revised paper source before the arXiv submission.

## Stage E - submit the preprint to arXiv

18. Create/verify your arXiv account and ORCID information.
19. Start a new submission. Recommended primary category: `math.CO`
    (Combinatorics); reasonable cross-lists include `math.NT` and `math.OC` if
    arXiv moderation accepts them.
20. If arXiv requests endorsement, follow the endorsement workflow after you
    select the category. Prefer someone you know in the field; do not mass-email
    endorsers.
21. Upload a clean arXiv source ZIP containing only the files needed to compile
    the paper. Do **not** upload repository logs, private notes, API keys, Git
    history, or verifier checkpoints as TeX source.
22. Let arXiv compile the TeX itself and inspect its generated PDF carefully.
23. In the Comments field, use restrained wording such as:

       12 pages. Computer-assisted proof; certificate and independent verification
       code available at [GitHub/Zenodo DOI]. Improves the certified lower bound
       0.38055470 to 0.380557.

24. Submit. If the record has not yet received external reproduction, say so
    explicitly rather than calling it independently verified.

## Stage F - announce in the problem community

25. After the arXiv page is live, post a concise comment on Erdős Problems #36.
    Link the arXiv paper and the immutable Zenodo/GitHub release. State exactly
    what is new: a stronger center-bin hybrid certificate, not a new Parseval
    identity.
26. Notify the people whose work you build on. If the third-party audit was
    helpful, acknowledge it in the next arXiv version.
27. If a mathematical or implementation issue is discovered, update the GitHub
    release history transparently and submit a new arXiv version; do not silently
    replace the old evidence.

## Suggested public claim

Before independent Arb reproduction:

> We give a candidate computer-assisted proof of c_E > 0.380557. The supplied
> interval checker verifies the new center certificate; independent
> re-verification is invited.

After independent reproduction:

> We prove c_E > 0.380557. The new center certificate has been independently
> reproduced with a separate interval-arithmetic implementation.
