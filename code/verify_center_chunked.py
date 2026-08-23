from fractions import Fraction
from decimal import Decimal, getcontext, ROUND_CEILING
import json, math, time, os
from pathlib import Path
import mpmath as mp
import numpy as np
from scipy.optimize import brentq

mp.iv.dps=45; mp.mp.dps=80; getcontext().prec=90
HERE=Path(__file__).resolve().parent
CERT=str(HERE.parent/'certificate'/'center_certificate.json'); STATE=str(HERE/'iv_state_direct3_45.json')
d=json.load(open(CERT))
def Fdec(s): return Fraction(str(s))
def ivf(q): return mp.iv.mpf(q.numerator)/q.denominator
def iv_upper_frac(x, places=26):
    s=mp.iv.nstr(x.b,70).strip('[]').split(',')[0].strip()
    val=Decimal(s); q=Decimal(1).scaleb(-places)
    return Fraction(val.quantize(q,rounding=ROUND_CEILING))
def upper_safe_decimal(ivx,places=24): return iv_upper_frac(ivx,places)
# q representation
const=Fraction(1); b2=Fraction(0); int_cos={};special_cos={};pi_cos={}
for a in d['active']:
    lam=Fdec(a['lambda']); k=a['kind']; p=a['param']; assert lam>=0
    if k=='t2':
        aa=Fraction(1,320);B=Fraction(2,3)+aa*aa/2;const+=lam*B;b2-=lam
    elif k=='cos_u':
        xi=Fdec(p);x=ivf(xi);exact=(mp.iv.sin(x)/x)**2
        B=upper_safe_decimal(exact,24)+Fraction(1,10**23);assert (ivf(B)-exact)>0
        const+=lam*B
        if xi.denominator==1:int_cos[xi.numerator]=int_cos.get(xi.numerator,Fraction(0))-lam
        else:special_cos[xi]=special_cos.get(xi,Fraction(0))-lam
    elif k=='parseval0':
        N=int(p);const+=lam*Fraction(1,2)
        for n in range(1,N+1):pi_cos[n]=pi_cos.get(n,Fraction(0))+lam
int_cos={k:v for k,v in int_cos.items() if v};special_cos={k:v for k,v in special_cos.items() if v};pi_cos={k:v for k,v in pi_cos.items() if v}
maxK=max(int_cos);maxN=max(pi_cos);needK=set(int_cos);needN=set(pi_cos)
# M2
M2=ivf(2*abs(b2))
for k,c in int_cos.items():M2+=ivf(abs(c))*k*k
for x,c in special_cos.items():M2+=ivf(abs(c))*ivf(x*x)
for n,c in pi_cos.items():M2+=ivf(abs(c))*(mp.iv.pi*n)**2
M2u=M2.b
M3=mp.iv.mpf(0)
for k,c in int_cos.items(): M3+=ivf(abs(c))*k**3
for x,c in special_cos.items(): M3+=ivf(abs(c))*ivf(abs(x)**3)
for n,c in pi_cos.items(): M3+=ivf(abs(c))*(mp.iv.pi*n)**3
M3u=M3.b

def q_qd_at(xq):
    x=ivf(xq);q=ivf(const)+ivf(b2)*x*x;qd=ivf(2*b2)*x;qdd=ivf(2*b2)
    for k,c0 in int_cos.items():
        cc=ivf(c0);z=k*x;cz=mp.iv.cos(z);sz=mp.iv.sin(z);q+=cc*cz;qd+=-cc*k*sz;qdd+=-cc*k*k*cz
    for xi,c0 in special_cos.items():
        cc=ivf(c0);w=ivf(xi);z=w*x;cz=mp.iv.cos(z);sz=mp.iv.sin(z);q+=cc*cz;qd+=-cc*w*sz;qdd+=-cc*w*w*cz
    for n,c0 in pi_cos.items():
        cc=ivf(c0);w=mp.iv.pi*n;z=w*x;cz=mp.iv.cos(z);sz=mp.iv.sin(z);q+=cc*cz;qd+=-cc*w*sz;qdd+=-cc*w*w*cz
    return q,qd,qdd

def Q_at(xq):
    x=ivf(xq);v=ivf(const)*x+ivf(b2)*x*x*x/3
    for k,c0 in int_cos.items():v+=ivf(c0)*mp.iv.sin(k*x)/k
    for xi,c0 in special_cos.items():
        w=ivf(xi);v+=ivf(c0)*mp.iv.sin(w*x)/w
    for n,c0 in pi_cos.items():
        w=mp.iv.pi*n;v+=ivf(c0)*mp.iv.sin(w*x)/w
    return v

def encf(q): return [q.numerator,q.denominator]
def decf(a): return Fraction(a[0],a[1])
if os.path.exists(STATE):
    st=json.load(open(STATE));stack=[(decf(a),decf(b)) for a,b in st['stack']];Dacc=decf(st['Dacc']);nodes0=st['nodes'];pos=st['pos'];neg=st['neg'];amb=st['amb']
    print('RESUME',nodes0,'stack',len(stack),'Dhalf',float(Dacc),flush=True)
else:
    # float seed roots, untrusted; only partitions [0,2]
    constf=float(const);b2f=float(b2);xs=np.linspace(0,2,120001);ys=np.full(xs.shape,constf)+b2f*xs*xs
    for k,c in int_cos.items():ys+=float(c)*np.cos(k*xs)
    for x,c in special_cos.items():ys+=float(c)*np.cos(float(x)*xs)
    for n,c in pi_cos.items():ys+=float(c)*np.cos(n*np.pi*xs)
    def qf(t):return constf+b2f*t*t+sum(float(c)*math.cos(k*t) for k,c in int_cos.items())+sum(float(c)*math.cos(float(x)*t) for x,c in special_cos.items())+sum(float(c)*math.cos(n*math.pi*t) for n,c in pi_cos.items())
    roots=[]
    for i in range(len(xs)-1):
        if ys[i]*ys[i+1]<0:
            try:roots.append(brentq(qf,float(xs[i]),float(xs[i+1])))
            except:pass
    rr=[]
    for r in roots:
        if not rr or abs(r-rr[-1])>1e-8:rr.append(r)
    roots=rr;pad=Fraction(1,25000);bounds=[Fraction(0)]
    for r in roots:
        rq=Fraction(Decimal(f'{r:.12f}'));a=max(Fraction(0),rq-pad);b=min(Fraction(2),rq+pad)
        if a>bounds[-1]:bounds.append(a)
        if b>bounds[-1]:bounds.append(b)
    if bounds[-1]<2:bounds.append(Fraction(2))
    bounds=sorted(set(bounds));stack=[(bounds[i],bounds[i+1]) for i in range(len(bounds)-1)];Dacc=Fraction(0);nodes0=pos=neg=amb=0
    print('INIT roots',len(roots),'stack',len(stack),flush=True)
max_width=Fraction(1,50000) # 2e-5
limit=700;done=0;start=time.time();nodes=nodes0
while stack and done<limit:
    a,b=stack.pop();nodes+=1;done+=1;c=(a+b)/2;r=(b-a)/2
    qc,qdc,qddc=q_qd_at(c);rad=abs(qdc).b*ivf(r)+abs(qddc).b*ivf(r*r)/2+M3u*ivf(r*r*r)/6;lo=qc.a-rad;hi=qc.b+rad
    if hi<0:neg+=1;continue
    if lo>0:
        vv=Q_at(b)-Q_at(a);Dacc+=iv_upper_frac(vv,26);pos+=1;continue
    if b-a<=max_width:
        if hi>0:Dacc+=iv_upper_frac(ivf(b-a)*hi,26)
        amb+=1;continue
    m=(a+b)/2;stack.append((m,b));stack.append((a,m))
st={'stack':[[encf(a),encf(b)] for a,b in stack],'Dacc':encf(Dacc),'nodes':nodes,'pos':pos,'neg':neg,'amb':amb}
json.dump(st,open(STATE,'w'))
print('CHUNK done',done,'nodes',nodes,'stack',len(stack),'pos',pos,'neg',neg,'amb',amb,'Dhalf',float(Dacc),'sec',time.time()-start,flush=True)
if not stack:
    D=2*Dacc;target=Fraction(1000000,380557);margin=target-D
    print('FINAL Dupper',Decimal(D.numerator)/Decimal(D.denominator))
    print('TARGET',Decimal(target.numerator)/Decimal(target.denominator))
    print('MARGIN',Decimal(margin.numerator)/Decimal(margin.denominator))
    print('CERTIFIED',margin>0)
