Subject: Candidate certified improvement for Erdős minimum overlap: c_E > 0.380557

Dear [Name],

I have a short computer-assisted proof that appears to improve the certified
lower bound for Erdős' minimum-overlap problem from 0.38055470 to 0.380557.

The new step is deliberately modest: it keeps the mean-bin dual framework of
Liam Price's 2026 certificate, replaces only the two binding central bins, and
adds White's already-known Parseval energy constraint to those bins. I am not
claiming the Parseval inequality itself is new.

The release candidate contains a short proof note, a 69-row JSON certificate,
and a standalone interval checker. The optimizer is not in the trusted path.
A fresh run gives

    D <= 2.6277192
      < 1/0.380557 = 2.6277272524221075949...

Would you be willing to sanity-check the analytic reduction and, if convenient,
run or independently reimplement the center verifier? I would prefer to have an
external reproduction before advertising the result as a new record.

Repository / archive: [LINK]

Best,
Deng Haowen
