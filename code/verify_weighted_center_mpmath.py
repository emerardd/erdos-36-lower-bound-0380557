#!/usr/bin/env python3
"""Independent mpmath.iv verifier for the frozen weighted center certificate.

Trusted arithmetic path:
  * exact Fraction arithmetic for every decimal multiplier and spectral weight;
  * mpmath.iv interval sin/cos and outward interval operations;
  * Taylor sign enclosures (order 3 or 6) with a global next-derivative bound;
  * exact elementary antiderivative on cells proved positive;
  * conservative width*upper(q) charge on terminal ambiguous cells.

SciPy/NumPy are used only to propose floating root seeds.  The seeds are not
trusted: every seeded or unseeded cell is certified by interval Taylor bounds,
and a missed root merely causes additional bisection.
"""
from __future__ import annotations
from fractions import Fraction
from decimal import Decimal, getcontext, ROUND_CEILING
import argparse, json, math, time
from pathlib import Path
import mpmath as mp
import numpy as np
from scipy.optimize import brentq

mp.iv.dps=40
mp.mp.dps=70
getcontext().prec=100
B2=Fraction(2,3)+Fraction(1,204800)

def F(s): return Fraction(str(s))
def ivf(q): return mp.iv.mpf(q.numerator)/q.denominator

def iv_upper_frac(x, places=30):
    s=mp.iv.nstr(x.b,90).strip('[]').split(',')[0].strip()
    val=Decimal(s); quantum=Decimal(1).scaleb(-places)
    return Fraction(val.quantize(quantum,rounding=ROUND_CEILING))

def load_certificate(path):
    d=json.load(open(path,encoding='utf-8'))
    l2=F(d['second_moment_lambda']); lw=F(d['window_lambda'])
    if l2<0 or lw<0: raise ValueError('negative global multiplier')
    if any(not (0<=F(w)<=1) for w in d['window_weights']): raise ValueError('window weight outside [0,1]')
    const=Fraction(1)+l2*B2+lw*Fraction(1,2); b2=-l2
    ordinary=[]
    for a in d['cosine_rows']:
        xi=F(a['xi']); lam=F(a['lambda'])
        if lam<0 or xi<=0: raise ValueError('bad cosine row')
        x=ivf(xi)
        # Choose an exact decimal B strictly above the interval upper endpoint.
        B=iv_upper_frac((mp.iv.sin(x)/x)**2,30)+Fraction(1,10**29)
        const += lam*B
        ordinary.append((xi,-lam))
    hmap={int(a['n']):F(a['lambda']) for a in d['harmonic_rows']}
    if any(v<0 for v in hmap.values()): raise ValueError('negative harmonic multiplier')
    picos=[]
    for n,ws in enumerate(d['window_weights'],1):
        c=lw*F(ws)-hmap.get(n,Fraction(0))
        if c: picos.append((n,c))
    return d,const,b2,ordinary,picos

def make_evaluator(const,b2,ordinary,picos,order):
    k=order+1
    Mnext=ivf(Fraction(0))
    for xi,c in ordinary: Mnext += ivf(abs(c))*ivf(abs(xi)**k)
    for n,c in picos: Mnext += ivf(abs(c))*(mp.iv.pi*n)**k
    Mnext=Mnext.b
    facts=[math.factorial(i) for i in range(order+2)]
    def derivs(xq):
        x=ivf(xq); ds=[ivf(Fraction(0)) for _ in range(order+1)]
        ds[0]=ivf(const)+ivf(b2)*x*x
        if order>=1: ds[1]=ivf(2*b2)*x
        if order>=2: ds[2]=ivf(2*b2)
        for xi,c0 in ordinary:
            w=ivf(xi); cc=ivf(c0); z=w*x; cz=mp.iv.cos(z); sz=mp.iv.sin(z); wp=mp.iv.mpf(1)
            for j in range(order+1):
                if j: wp*=w
                base=(cz,-sz,-cz,sz)[j&3]
                ds[j]+=cc*wp*base
        for n,c0 in picos:
            w=mp.iv.pi*n; cc=ivf(c0); z=w*x; cz=mp.iv.cos(z); sz=mp.iv.sin(z); wp=mp.iv.mpf(1)
            for j in range(order+1):
                if j: wp*=w
                base=(cz,-sz,-cz,sz)[j&3]
                ds[j]+=cc*wp*base
        return ds
    def Q(xq):
        x=ivf(xq); val=ivf(const)*x+ivf(b2)*x*x*x/3
        for xi,c0 in ordinary:
            w=ivf(xi); val+=ivf(c0)*mp.iv.sin(w*x)/w
        for n,c0 in picos:
            w=mp.iv.pi*n; val+=ivf(c0)*mp.iv.sin(w*x)/w
        return val
    return derivs,Q,Mnext,facts

def floating_roots(d):
    l2=float(d['second_moment_lambda']); lw=float(d['window_lambda'])
    xis=np.array([float(a['xi']) for a in d['cosine_rows']]); lams=np.array([float(a['lambda']) for a in d['cosine_rows']]); sx=np.sinc(xis/np.pi)**2
    weights=np.array([float(x) for x in d['window_weights']]); ns=np.arange(1,len(weights)+1.)
    hs=np.array([int(a['n']) for a in d['harmonic_rows']],dtype=float); hl=np.array([float(a['lambda']) for a in d['harmonic_rows']])
    def qf(t):
        v=1+l2*(float(B2)-t*t)+np.dot(lams,sx-np.cos(xis*t))+lw*(0.5+np.dot(weights,np.cos(np.pi*ns*t)))
        if len(hs): v-=np.dot(hl,np.cos(np.pi*hs*t))
        return float(v)
    xs=np.linspace(0,2,160001); ys=np.array([qf(x) for x in xs]); idx=np.flatnonzero(ys[:-1]*ys[1:]<0); rr=[]
    for i in idx:
        r=brentq(qf,float(xs[i]),float(xs[i+1]))
        if not rr or abs(r-rr[-1])>1e-10: rr.append(r)
    return rr

class WeightedVerifier:
    def __init__(self, cert_path):
        self.d,self.const,self.b2,self.ordinary,self.picos=load_certificate(cert_path)
        self.roots=floating_roots(self.d)
        self.evals={}
    def evaluator(self,order):
        if order not in self.evals: self.evals[order]=make_evaluator(self.const,self.b2,self.ordinary,self.picos,order)
        return self.evals[order]
    def verify(self,lo,hi,order=6,max_width=Fraction(1,20000),pad=Fraction(1,200000),max_nodes=500000,root_seed=True,verbose=True):
        loq=F(lo); hiq=F(hi); derivs,Q,Mnext,facts=self.evaluator(order); bounds=[loq]
        if root_seed:
            for r in self.roots:
                rq=Fraction(Decimal(f'{r:.15f}')); a=max(loq,rq-pad); b=min(hiq,rq+pad)
                if loq<a<hiq and a>bounds[-1]: bounds.append(a)
                if loq<b<hiq and b>bounds[-1]: bounds.append(b)
        if bounds[-1]<hiq: bounds.append(hiq)
        stack=[(bounds[i],bounds[i+1]) for i in range(len(bounds)-1)]; D=Fraction(0); nodes=pos=neg=amb=0; t0=time.time()
        while stack:
            a,b=stack.pop(); nodes+=1
            if nodes>max_nodes: raise RuntimeError('max_nodes exceeded')
            c=(a+b)/2; r=(b-a)/2; ds=derivs(c); rad=mp.iv.mpf(0); rp=ivf(Fraction(1)); rr=ivf(r)
            for j in range(1,order+1): rp*=rr; rad+=abs(ds[j]).b*rp/facts[j]
            rp*=rr; rad+=Mnext*rp/facts[order+1]
            loiv=ds[0].a-rad; hiiv=ds[0].b+rad
            if hiiv<0: neg+=1; continue
            if loiv>0: D+=iv_upper_frac(Q(b)-Q(a),30); pos+=1; continue
            if b-a<=max_width:
                if hiiv>0: D+=iv_upper_frac(ivf(b-a)*hiiv,30)
                amb+=1; continue
            m=(a+b)/2; stack.append((m,b)); stack.append((a,m))
        if verbose: print(f'chunk [{lo},{hi}] order={order} nodes={nodes} pos={pos} neg={neg} amb={amb} Dhalf_upper={D} sec={time.time()-t0:.3f}')
        return D

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('cert'); ap.add_argument('--lo',default='0'); ap.add_argument('--hi',default='2'); ap.add_argument('--order',type=int,default=6); ap.add_argument('--no-root-seed',action='store_true'); a=ap.parse_args()
    v=WeightedVerifier(a.cert); D=v.verify(a.lo,a.hi,a.order,root_seed=not a.no_root_seed); print('Dhalf_upper_fraction:',D); return 0
if __name__=='__main__': raise SystemExit(main())
