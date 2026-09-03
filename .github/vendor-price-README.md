# Vendored Price certificate package

This directory is a byte-for-byte copy of the `certificate/` directory
from Liam Price's public repository `Leeham06972452/erdos-36-lower-bound`,
pinned at the commit recorded in `UPSTREAM_COMMIT.txt`.

The files are included for reproducibility and provenance.  The noncentral
mean-bin certificates are due to Price.  This repository's new contribution
replaces only bins 85 and 86 with the hybrid Parseval certificate.

## Attribution and licensing

Upstream: https://github.com/Leeham06972452/erdos-36-lower-bound
Author:   Liam Price
Commit:   see `UPSTREAM_COMMIT.txt`

At the time of vendoring the upstream repository carried no explicit license
file.  Nothing in this directory is covered by the MIT license at the root of
this repository; all rights remain with the original author.  The material is
reproduced here unmodified and with attribution so that the noncentral bins of
the theorem can be inspected and re-verified against exactly the bytes that
were used.  It is not offered for redistribution or reuse under any terms of
this repository's choosing.  If you want to reuse it, ask the original author.

If you are the upstream author and would prefer a different arrangement -
a license file, a narrower subset, or removal in favour of a fetch script -
please open an issue on this repository and it will be honoured.

## Verifying the hashes

`SHA256SUMS.txt` here covers every file in this directory; the upstream
`certificate/SHA256SUMS.txt` covers the files Price shipped.  The upstream
manifest was generated with CRLF line endings, so strip them before checking:

```bash
cd vendor/price/certificate
sed 's/\r$//' SHA256SUMS.txt | sha256sum -c
```

The repository sets `* -text` in `.gitattributes`, so a clone reproduces these
bytes exactly on every platform, Windows included.
