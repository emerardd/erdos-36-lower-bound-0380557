#!/usr/bin/env python3
"""Numerical search for a stronger central-bin dual certificate.

Experimental only: this is NOT an Arb/MPFR verifier and does not prove a new
bound by itself.

It replaces the hard Parseval prefix with a fixed spectral window
    -sum_n w_n C_{n*pi} <= 1/2,  0 <= w_n <= 1,
which is valid because C_{n*pi}=-|H(n*pi)|^2 and
sum_{n>=1}|H(n*pi)|^2 <= 1/2.

Pipeline:
  coarse LP (learn w_n) -> freeze window -> 2001-grid LP -> prune active rows
  -> 4001-grid LP -> continuous root/antiderivative integration of q_+.
"""

import argparse, json
from pathlib import Path
import numpy as np
from scipy.optimize import brentq, linprog
from scipy.sparse import coo_matrix, csr_matrix, eye, hstack, vstack

B2 = 2/3 + 1/(2*320**2)
BESPOKE = [5.94,8.4575,12.375,15.5725,19.5425,26.995,34.175,34.18,
           41.745,45.9,53.0,53.105,60.34,64.42,65.0,71.975,79.125]

def freqs():
    return np.array(sorted(set(BESPOKE + [float(n) for n in range(80,401)])))

def trap(n):
    t=np.linspace(0,2,n); d=t[1]-t[0]
    w=np.full(n,d); w[[0,-1]]*=0.5
    return t,w

def coarse(xis,M=400,Mh=400,N=801):
    t,quad=trap(N); sx=np.sinc(xis/np.pi)**2
    i_lp=1+len(xis); i_a=i_lp+1; i_h=i_a+M; nmain=i_h+Mh
    ns=np.arange(1,M+1.0); hs=np.arange(1,Mh+1.0)
    main=np.hstack([
        (B2-t*t)[:,None],
        sx[None,:]-np.cos(t[:,None]*xis[None,:]),
        np.full((N,1),0.5),
        np.cos(np.pi*t[:,None]*ns[None,:]),
        -np.cos(np.pi*t[:,None]*hs[None,:]),
    ])
    Agrid=hstack([csr_matrix(main),-eye(N,format="csr")],format="csr")
    rows=[]; cols=[]; data=[]
    for k in range(M):
        rows += [k,k]; cols += [i_a+k,i_lp]; data += [1.,-1.]
    Acap=coo_matrix((data,(rows,cols)),shape=(M,nmain+N)).tocsr()
    A=vstack([Agrid,Acap],format="csr")
    b=np.r_[np.full(N,-1.),np.zeros(M)]
    c=np.zeros(nmain+N); c[nmain:]=2*quad
    r=linprog(c,A_ub=A,b_ub=b,bounds=(0,None),method="highs",
              options={"presolve":True})
    if not r.success: raise RuntimeError(r.message)
    lp=r.x[i_lp]
    if lp<=0: raise RuntimeError("weighted Parseval row inactive")
    weights=np.clip(r.x[i_a:i_a+M]/lp,0,1)
    return r,weights

def fixed(xis,weights,harmonics,N):
    t,quad=trap(N); sx=np.sinc(xis/np.pi)**2
    ns=np.arange(1,len(weights)+1.0)
    hs=np.asarray(harmonics,dtype=float)
    i_w=1+len(xis); i_h=i_w+1; nmain=i_h+len(hs)
    window=(0.5+np.cos(np.pi*t[:,None]*ns[None,:]).dot(weights))[:,None]
    blocks=[(B2-t*t)[:,None],
            sx[None,:]-np.cos(t[:,None]*xis[None,:]),
            window]
    if len(hs): blocks.append(-np.cos(np.pi*t[:,None]*hs[None,:]))
    main=np.hstack(blocks)
    A=hstack([csr_matrix(main),-eye(N,format="csr")],format="csr")
    c=np.zeros(nmain+N); c[nmain:]=2*quad
    r=linprog(c,A_ub=A,b_ub=np.full(N,-1.),bounds=(0,None),
              method="highs",options={"presolve":True})
    if not r.success: raise RuntimeError(r.message)
    return r,{"xis":xis,"weights":weights,"harmonics":np.asarray(harmonics),
              "i_w":i_w,"i_h":i_h,"nmain":nmain,"N":N}

def prune(r,m,tol=1e-10):
    lc=r.x[1:1+len(m["xis"])]
    lh=r.x[m["i_h"]:m["i_h"]+len(m["harmonics"])]
    return m["xis"][lc>tol],m["harmonics"][lh>tol]

def funcs(r,m):
    xis=m["xis"]; w=m["weights"]; hs=m["harmonics"].astype(float)
    sx=np.sinc(xis/np.pi)**2; ns=np.arange(1,len(w)+1.0)
    l2=r.x[0]; lc=r.x[1:1+len(xis)]; lw=r.x[m["i_w"]]
    lh=r.x[m["i_h"]:m["i_h"]+len(hs)]
    def q(t):
        v=1+l2*(B2-t*t)+np.dot(lc,sx-np.cos(xis*t))
        v+=lw*(0.5+np.dot(w,np.cos(np.pi*ns*t)))
        if len(hs): v-=np.dot(lh,np.cos(np.pi*hs*t))
        return float(v)
    def Q(t):
        v=t+l2*(B2*t-t**3/3)+np.dot(lc,sx*t-np.sin(xis*t)/xis)
        v+=lw*(0.5*t+np.dot(w,np.sin(np.pi*ns*t)/(np.pi*ns)))
        if len(hs): v-=np.dot(lh,np.sin(np.pi*hs*t)/(np.pi*hs))
        return float(v)
    return q,Q

def continuous(r,m,scan=150000):
    q,Q=funcs(r,m)
    t=np.linspace(0,2,scan+1)
    vals=np.fromiter((q(float(x)) for x in t),float,count=len(t))
    idx=np.flatnonzero(vals[:-1]*vals[1:]<0)
    roots=[brentq(q,float(t[i]),float(t[i+1]),xtol=1e-14,rtol=1e-14)
           for i in idx]
    pts=[0.]+roots+[2.]; area=0.
    for a,b in zip(pts[:-1],pts[1:]):
        if q((a+b)/2)>0: area += Q(b)-Q(a)
    return 2*area,roots

def dump(r,m,D,roots,path):
    lc=r.x[1:1+len(m["xis"])]
    lh=r.x[m["i_h"]:m["i_h"]+len(m["harmonics"])]
    obj={
      "status":"numerical candidate only; NOT interval certified",
      "center_bins":[["-1/320","0"],["0","1/320"]],
      "grid_points":m["N"],"grid_D":float(r.fun),"grid_bound":float(1/r.fun),
      "continuous_D":float(D),"continuous_bound":float(1/D),
      "root_count_on_0_2":len(roots),
      "second_moment_lambda":float(r.x[0]),
      "window_lambda":float(r.x[m["i_w"]]),
      "window_weights":[float(x) for x in m["weights"]],
      "cosine_rows":[{"xi":float(x),"lambda":float(l)}
                     for x,l in zip(m["xis"],lc) if l>1e-12],
      "harmonic_rows":[{"n":int(n),"lambda":float(l)}
                       for n,l in zip(m["harmonics"],lh) if l>1e-12],
    }
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--coarse-grid",type=int,default=801)
    ap.add_argument("--middle-grid",type=int,default=2001)
    ap.add_argument("--final-grid",type=int,default=4001)
    ap.add_argument("--scan",type=int,default=150000)
    ap.add_argument("--output",default="experiments/spectral_window_candidate.json")
    a=ap.parse_args()
    x=freqs(); hs=np.arange(1,401)
    r0,w=coarse(x,N=a.coarse_grid)
    print("coarse",r0.fun,1/r0.fun,"window-nnz",np.count_nonzero(w>1e-8))
    r1,m1=fixed(x,w,hs,a.middle_grid)
    print("middle",r1.fun,1/r1.fun)
    xa,ha=prune(r1,m1)
    print("active cosine",len(xa),"harmonic",len(ha))
    r2,m2=fixed(xa,w,ha,a.final_grid)
    print("final-grid",r2.fun,1/r2.fun)
    D,roots=continuous(r2,m2,a.scan)
    print("continuous",D,1/D,"roots",len(roots))
    dump(r2,m2,D,roots,a.output)
    print("wrote",a.output)

if __name__=="__main__":
    main()
