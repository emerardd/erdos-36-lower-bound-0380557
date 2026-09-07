#!/usr/bin/env python3
"""Parallel reproduction of the independent mpmath.iv weighted-center proof.

The archived manifest supplies only exact interval endpoints and Taylor order.
Every Dhalf upper bound is recomputed from the frozen certificate.  Worker
processes each build their own mpmath.iv verifier, so interval contexts are not
shared across threads.  Results are aggregated with exact Fraction arithmetic.
"""
from __future__ import annotations
import argparse,csv,multiprocessing as mp_proc,os
from fractions import Fraction
from pathlib import Path
from verify_weighted_center_mpmath import WeightedVerifier
ROOT=Path(__file__).resolve().parent.parent
CERT=ROOT/'certificate'/'weighted_center_certificate_038056070.json'
MAN=ROOT/'verification'/'weighted_038056070_mpmath_manifest.csv'
TARGET=Fraction('0.38056070')
_V=None
def init_worker():
    global _V
    _V=WeightedVerifier(CERT)
def work(task):
    i,lo,hi,order=task
    assert _V is not None
    D=_V.verify(lo,hi,order=order,verbose=False)
    return i,lo,hi,D,order
def dec(q,digits=90):
    sign='-' if q<0 else '';q=abs(q);a,r=divmod(q.numerator,q.denominator);out=sign+str(a)+'.'
    for _ in range(digits):r*=10;d,r=divmod(r,q.denominator);out+=str(d)
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--jobs',type=int,default=max(1,min(8,os.cpu_count() or 1)));ap.add_argument('--save-manifest',type=Path);a=ap.parse_args()
    tasks=[]
    for i,r in enumerate(csv.DictReader(MAN.open(newline=''))):
        tasks.append((i,r['lo'],r['hi'],int(r['taylor_order'].removeprefix('order'))))
    ctx=mp_proc.get_context('spawn')
    with ctx.Pool(processes=a.jobs,initializer=init_worker) as pool:
        results=[]
        for x in pool.imap_unordered(work,tasks,chunksize=1):
            results.append(x);print(f'PASS [{x[1]},{x[2]}] Dhalf<={float(x[3]):.17g}',flush=True)
    results.sort();cur=Fraction(0);total=Fraction(0)
    if a.save_manifest:
        a.save_manifest.parent.mkdir(parents=True,exist_ok=True)
        f=a.save_manifest.open('w',newline='');w=csv.writer(f);w.writerow(['lo','hi','Dhalf_upper','taylor_order'])
    else:f=w=None
    try:
        for i,lo,hi,D,order in results:
            L,H=Fraction(lo),Fraction(hi)
            if L!=cur:raise ValueError(f'gap/overlap expected {cur}, got {L}')
            cur=H;total+=D
            if w:w.writerow([lo,hi,f'{D.numerator}/{D.denominator}',f'order{order}'])
    finally:
        if f:f.close()
    if cur!=2:raise ValueError(f'coverage ends at {cur}')
    full=2*total;td=1/TARGET;margin=td-full
    print('chunks:',len(results));print('coverage: [0,2] exact and gap-free');print('Dhalf_upper:',dec(total));print('D_upper:',dec(full));print('target: 0.38056070');print('target_D:',dec(td));print('margin_D:',dec(margin));print('implied_bound_from_D:',dec(1/full));print('CERTIFIED',margin>0)
    return 0 if margin>0 else 1
if __name__=='__main__':raise SystemExit(main())
