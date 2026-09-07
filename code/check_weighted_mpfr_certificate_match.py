#!/usr/bin/env python3
"""Check the compact MPFR coefficient file against the frozen JSON proof object."""
from decimal import Decimal
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
J=ROOT/'certificate'/'weighted_center_certificate_038056070.json'
C=ROOT/'certificate'/'weighted_center_coefficients_038056070.txt'
d=json.loads(J.read_text())
lines=C.read_text().splitlines()
assert lines[0]=='FORMAT weighted-center-coefficients-v1'
t2=lines[1].split(); win=lines[2].split()
assert t2==['T2',d['second_moment_lambda']]
assert win==['WINDOW',d['window_lambda']]
cos=[]; pi={}
for line in lines[3:]:
    a=line.split()
    if a[0]=='COS': cos.append((a[1],a[2]))
    elif a[0]=='PI': pi[int(a[1])]=Decimal(a[2])
    else: raise SystemExit(f'bad tag {a[0]}')
expected_cos=[(r['xi'],r['lambda']) for r in d['cosine_rows']]
wl=Decimal(d['window_lambda']); weights=[Decimal(x) for x in d['window_weights']]
h={int(r['n']):Decimal(r['lambda']) for r in d['harmonic_rows']}
expected_pi={n:wl*weights[n-1]-h.get(n,Decimal(0)) for n in range(1,len(weights)+1)}
checks={
 'T2': t2==['T2',d['second_moment_lambda']],
 'WINDOW': win==['WINDOW',d['window_lambda']],
 'COS': cos==expected_cos,
 'PI': pi==expected_pi,
}
for k,v in checks.items(): print(f'{k}: {v}')
ok=all(checks.values())
print(f'MATCH {ok}')
raise SystemExit(0 if ok else 1)
