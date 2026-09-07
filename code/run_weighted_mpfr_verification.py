#!/usr/bin/env python3
"""Compile and rerun the independent direct-MPFR weighted-center verifier.

The frozen subdivision is read only for exact [lo,hi] endpoints; archived
upper bounds are ignored.  Each subprocess recomputes its own rigorous
Dhalf_upper from the frozen coefficient transcription. Printed upward-rounded
decimals are parsed as exact Fractions and aggregated without floating-point arithmetic.
"""
from __future__ import annotations
import argparse,csv,os,re,subprocess,tempfile
from concurrent.futures import ThreadPoolExecutor,as_completed
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'code'/'verify_weighted_center_mpfr.c'
COEFF=ROOT/'certificate'/'weighted_center_coefficients_038056070.txt'
MAN=ROOT/'verification'/'weighted_038056070_mpmath_manifest.csv'
TARGET=Fraction('0.38056070')
DRE=re.compile(r'^Dhalf_upper:\s*([0-9]+(?:\.[0-9]+)?)\s*$',re.M)
def units(s):
    q=Fraction(Decimal(s))*10000
    if q.denominator!=1: raise ValueError(f'endpoint not on 1e-4 grid: {s}')
    return q.numerator
def compile(exe,prec):
    cc=os.environ.get('CC','gcc')
    p=subprocess.run([cc,'-O3',f'-DPREC={prec}',str(SRC),'-o',str(exe),'-lmpfr','-lgmp','-lm'],capture_output=True,text=True)
    if p.returncode==0:return 'system mpfr.h'
    p2=subprocess.run([cc,'-O3',f'-DPREC={prec}','-DMPFR_SELFDECL',str(SRC),'-o',str(exe),'-Wl,-l:libmpfr.so.6','-lm'],capture_output=True,text=True)
    if p2.returncode: raise RuntimeError('compile failed\n'+p.stderr+'\n'+p2.stderr)
    return 'MPFR_SELFDECL LP64 fallback'
def run(exe,lo,hi,maxdepth):
    p=subprocess.run([str(exe),str(COEFF),str(lo),str(hi),str(maxdepth)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    if p.returncode or 'CHUNK_CERTIFIED True' not in p.stdout: raise RuntimeError(p.stdout)
    m=DRE.search(p.stdout)
    if not m: raise RuntimeError('missing Dhalf_upper\n'+p.stdout)
    return lo,hi,Fraction(m.group(1)),p.stdout
def dec(q,digits=90):
    sign='-' if q<0 else '';q=abs(q);a,r=divmod(q.numerator,q.denominator);out=sign+str(a)+'.'
    for _ in range(digits):r*=10;d,r=divmod(r,q.denominator);out+=str(d)
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--jobs',type=int,default=max(1,min(8,os.cpu_count() or 1)));ap.add_argument('--prec',type=int,default=192);ap.add_argument('--max-depth',type=int,default=20);ap.add_argument('--save-dir',type=Path);a=ap.parse_args()
    rows=[]
    for r in csv.DictReader(MAN.open(newline='')): rows.append((units(r['lo']),units(r['hi']),r['lo'],r['hi']))
    rows.sort();cur=0
    for lo,hi,_,_ in rows:
        if lo!=cur:raise ValueError(f'coverage gap/overlap at {cur}->{lo}')
        cur=hi
    if cur!=20000:raise ValueError(f'coverage ends {cur}')
    with tempfile.TemporaryDirectory(prefix='erdos36-mpfr6-') as td:
        exe=Path(td)/'verify';mode=compile(exe,a.prec);print('compile_mode:',mode,flush=True)
        res=[]
        with ThreadPoolExecutor(max_workers=a.jobs) as ex:
            fut={ex.submit(run,exe,lo,hi,a.max_depth):(lo,hi,slo,shi) for lo,hi,slo,shi in rows}
            for f in as_completed(fut):
                lo,hi,slo,shi=fut[f];L,H,D,text=f.result();res.append((L,H,D,text,slo,shi));print(f'PASS [{slo},{shi}] Dhalf<={float(D):.17g}',flush=True)
        res.sort();tot=Fraction(0);cur=0
        if a.save_dir:a.save_dir.mkdir(parents=True,exist_ok=True)
        for i,(lo,hi,D,text,slo,shi) in enumerate(res):
            if lo!=cur:raise AssertionError('post-run coverage failure')
            cur=hi;tot+=D
            if a.save_dir:(a.save_dir/f'chunk_{i:02d}.txt').write_text(text)
        full=2*tot;td=1/TARGET;margin=td-full
        print('chunks:',len(res));print('coverage: [0,2] exact and gap-free');print('Dhalf_upper:',dec(tot));print('D_upper:',dec(full));print('target: 0.38056070');print('target_D:',dec(td));print('margin_D:',dec(margin));print('implied_bound_from_D:',dec(1/full));print('CERTIFIED',margin>0)
        return 0 if margin>0 else 1
if __name__=='__main__':raise SystemExit(main())
