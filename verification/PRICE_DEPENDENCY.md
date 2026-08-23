# Reused noncentral certificate

The theorem reuses Liam Price's public 172-bin Arb certificate, repository:

https://github.com/Leeham06972452/erdos-36-lower-bound

Public result: `c_E > 0.38055470`, posted 2026-06-29 and independently
re-run/audited by `occisn/erdos-36-certified-lower-bound`.

For the new target `0.380557`, bins 85 and 86 are replaced by our new even
center certificate. In Price's published per-bin Arb outputs, the largest
`D_upper` among all *other* bins is bin 77 (mirrored by bin 94):

    bin 77: [-0.0375, -0.025]
    D_upper <= 2.627538530873375790090272175878307131812586378...

    bin 94: [0.025, 0.0375]
    D_upper <= 2.627538530873375771654040843928987325849471441...

Both are below

    1 / 0.380557 = 2.62772725242210759492007767561758...

The adjacent bins are also comfortably below target:

    bin 84: D_upper <= 2.6273364604202817814730808626904...
    bin 87: D_upper <= 2.6273364604202817817384520815850...

Source files in Price's repository:

- `certificate/arb_0_84_0380554700.csv`
- `certificate/arb_85_88_0380554700.csv`
- `certificate/arb_89_171_0380554700.csv`

For the strongest release, independently rerun Price's Arb checker at target
`0.380557` on bins `0-84`, `87-88`, and `89-171`, rather than relying only on
these archived per-bin outputs.
