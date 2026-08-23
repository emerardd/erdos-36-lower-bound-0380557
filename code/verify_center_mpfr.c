
/*
Independent MPFR verifier for the central certificate proving c_E > 0.380557.
No mpmath, Arb, NumPy/SciPy, root finder, or numerical quadrature is used.
The program uses MPFR directed rounding and a Taylor enclosure for sign
classification. Positive cells are integrated by the exact elementary
antiderivative of q, with interval evaluation at the endpoints.

Build on Linux with:
    gcc -O3 verify_center_mpfr.c -o verify_center_mpfr -Wl,-l:libmpfr.so.6 -lm

This source declares the small part of the MPFR ABI it uses so that it can be
built even when the development header is not installed. The struct layout and
function signatures match MPFR 4.x on the supported 64-bit Linux ABI.
*/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>

typedef unsigned long mp_limb_t;
typedef long mpfr_prec_t;
typedef int mpfr_sign_t;
typedef long mpfr_exp_t;
typedef int mpfr_rnd_t;
typedef struct { mpfr_prec_t _mpfr_prec; mpfr_sign_t _mpfr_sign; mpfr_exp_t _mpfr_exp; mp_limb_t *_mpfr_d; } __mpfr_struct;
typedef __mpfr_struct mpfr_t[1];
typedef __mpfr_struct *mpfr_ptr;
typedef const __mpfr_struct *mpfr_srcptr;

enum { MPFR_RNDN=0, MPFR_RNDZ=1, MPFR_RNDU=2, MPFR_RNDD=3, MPFR_RNDA=4 };
extern void mpfr_init2(mpfr_ptr, mpfr_prec_t);
extern void mpfr_clear(mpfr_ptr);
extern int mpfr_set(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_set_str(mpfr_ptr, const char*, int, mpfr_rnd_t);
extern int mpfr_set_si(mpfr_ptr, long, mpfr_rnd_t);
extern int mpfr_set_ui(mpfr_ptr, unsigned long, mpfr_rnd_t);
extern int mpfr_add(mpfr_ptr, mpfr_srcptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_sub(mpfr_ptr, mpfr_srcptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_mul(mpfr_ptr, mpfr_srcptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_div(mpfr_ptr, mpfr_srcptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_div_ui(mpfr_ptr, mpfr_srcptr, unsigned long, mpfr_rnd_t);
extern int mpfr_div_2ui(mpfr_ptr, mpfr_srcptr, unsigned long, mpfr_rnd_t);
extern int mpfr_mul_ui(mpfr_ptr, mpfr_srcptr, unsigned long, mpfr_rnd_t);
extern int mpfr_neg(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_sin(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_cos(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_sin_cos(mpfr_ptr, mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_const_pi(mpfr_ptr, mpfr_rnd_t);
extern int mpfr_cmp(mpfr_srcptr, mpfr_srcptr);
extern int mpfr_cmp_si(mpfr_srcptr, long);
extern double mpfr_get_d(mpfr_srcptr, mpfr_rnd_t);
extern char *mpfr_get_str(char*, mpfr_exp_t*, int, size_t, mpfr_srcptr, mpfr_rnd_t);
extern void mpfr_free_str(char*);

#ifndef PREC
#define PREC 256
#endif

typedef struct { mpfr_t lo, hi; } iv;
typedef struct { iv w, c, dc, anti; } term_t;

static mpfr_t S[16];
static int scratch_ready=0;
static void scratch_init(void){ if(scratch_ready) return; for(int i=0;i<16;i++) mpfr_init2(S[i],PREC); scratch_ready=1; }
static void scratch_clear(void){ if(!scratch_ready) return; for(int i=0;i<16;i++) mpfr_clear(S[i]); scratch_ready=0; }
static void iv_init(iv *a){ mpfr_init2(a->lo,PREC); mpfr_init2(a->hi,PREC); }
static void iv_clear(iv *a){ mpfr_clear(a->lo); mpfr_clear(a->hi); }
static void iv_set(iv *r,const iv*a){ mpfr_set(r->lo,a->lo,MPFR_RNDN); mpfr_set(r->hi,a->hi,MPFR_RNDN); }
static void iv_set_si(iv*r,long x){ mpfr_set_si(r->lo,x,MPFR_RNDN); mpfr_set_si(r->hi,x,MPFR_RNDN); }
static int iv_set_dec(iv*r,const char*s){ int a=mpfr_set_str(r->lo,s,10,MPFR_RNDD); int b=mpfr_set_str(r->hi,s,10,MPFR_RNDU); return a||b; }
static void iv_set_ratio(iv*r,unsigned long p,unsigned long q){ mpfr_set_ui(r->lo,p,MPFR_RNDN); mpfr_set_ui(r->hi,p,MPFR_RNDN); mpfr_div_ui(r->lo,r->lo,q,MPFR_RNDD); mpfr_div_ui(r->hi,r->hi,q,MPFR_RNDU); }
static void iv_set_pi(iv*r){ mpfr_const_pi(r->lo,MPFR_RNDD); mpfr_const_pi(r->hi,MPFR_RNDU); }
static void iv_neg(iv*r,const iv*a){ mpfr_neg(S[0],a->hi,MPFR_RNDD); mpfr_neg(S[1],a->lo,MPFR_RNDU); mpfr_set(r->lo,S[0],MPFR_RNDN); mpfr_set(r->hi,S[1],MPFR_RNDN); }
static void iv_add(iv*r,const iv*a,const iv*b){ mpfr_add(S[0],a->lo,b->lo,MPFR_RNDD); mpfr_add(S[1],a->hi,b->hi,MPFR_RNDU); mpfr_set(r->lo,S[0],MPFR_RNDN); mpfr_set(r->hi,S[1],MPFR_RNDN); }
static void iv_sub(iv*r,const iv*a,const iv*b){ mpfr_sub(S[0],a->lo,b->hi,MPFR_RNDD); mpfr_sub(S[1],a->hi,b->lo,MPFR_RNDU); mpfr_set(r->lo,S[0],MPFR_RNDN); mpfr_set(r->hi,S[1],MPFR_RNDN); }
static void iv_mul(iv*r,const iv*a,const iv*b){
    mpfr_mul(S[0],a->lo,b->lo,MPFR_RNDD); mpfr_mul(S[1],a->lo,b->hi,MPFR_RNDD);
    mpfr_mul(S[2],a->hi,b->lo,MPFR_RNDD); mpfr_mul(S[3],a->hi,b->hi,MPFR_RNDD);
    mpfr_set(S[8],S[0],MPFR_RNDN); for(int i=1;i<4;i++) if(mpfr_cmp(S[i],S[8])<0) mpfr_set(S[8],S[i],MPFR_RNDN);
    mpfr_mul(S[4],a->lo,b->lo,MPFR_RNDU); mpfr_mul(S[5],a->lo,b->hi,MPFR_RNDU);
    mpfr_mul(S[6],a->hi,b->lo,MPFR_RNDU); mpfr_mul(S[7],a->hi,b->hi,MPFR_RNDU);
    mpfr_set(S[9],S[4],MPFR_RNDN); for(int i=5;i<8;i++) if(mpfr_cmp(S[i],S[9])>0) mpfr_set(S[9],S[i],MPFR_RNDN);
    mpfr_set(r->lo,S[8],MPFR_RNDN); mpfr_set(r->hi,S[9],MPFR_RNDN);
}
static void iv_square(iv*r,const iv*a){
    if(mpfr_cmp_si(a->lo,0)>=0){ mpfr_mul(r->lo,a->lo,a->lo,MPFR_RNDD); mpfr_mul(r->hi,a->hi,a->hi,MPFR_RNDU); return; }
    if(mpfr_cmp_si(a->hi,0)<=0){ mpfr_mul(r->lo,a->hi,a->hi,MPFR_RNDD); mpfr_mul(r->hi,a->lo,a->lo,MPFR_RNDU); return; }
    mpfr_set_si(r->lo,0,MPFR_RNDN); mpfr_mul(S[0],a->lo,a->lo,MPFR_RNDU); mpfr_mul(S[1],a->hi,a->hi,MPFR_RNDU);
    mpfr_set(r->hi, mpfr_cmp(S[0],S[1])>0?S[0]:S[1], MPFR_RNDN);
}
static void iv_div_pos(iv*r,const iv*a,const iv*b){
    if(mpfr_cmp_si(b->lo,0)<=0){ fprintf(stderr,"division by interval containing zero\n"); exit(2); }
    iv rec; iv_init(&rec); mpfr_set_ui(rec.lo,1,MPFR_RNDN); mpfr_set_ui(rec.hi,1,MPFR_RNDN);
    mpfr_div(rec.lo,rec.lo,b->hi,MPFR_RNDD); mpfr_div(rec.hi,rec.hi,b->lo,MPFR_RNDU); iv_mul(r,a,&rec); iv_clear(&rec);
}
static void iv_abs_upper(mpfr_ptr out,const iv*a){
    if(mpfr_cmp_si(a->lo,0)>=0){ mpfr_set(out,a->hi,MPFR_RNDU); return; }
    if(mpfr_cmp_si(a->hi,0)<=0){ mpfr_neg(out,a->lo,MPFR_RNDU); return; }
    mpfr_neg(S[0],a->lo,MPFR_RNDU); mpfr_set(out,mpfr_cmp(S[0],a->hi)>0?S[0]:a->hi,MPFR_RNDU);
}
static void iv_width_up(mpfr_ptr out,const iv*a){ mpfr_sub(out,a->hi,a->lo,MPFR_RNDU); }
static void iv_sincos(iv*s,iv*c,const iv*z){
    mpfr_sin_cos(S[0],S[1],z->lo,MPFR_RNDD); /* sin low, cos low at left endpoint */
    mpfr_sin_cos(S[2],S[3],z->lo,MPFR_RNDU); /* sin high, cos high */
    iv_width_up(S[4],z);
    mpfr_sub(s->lo,S[0],S[4],MPFR_RNDD); mpfr_add(s->hi,S[2],S[4],MPFR_RNDU);
    mpfr_sub(c->lo,S[1],S[4],MPFR_RNDD); mpfr_add(c->hi,S[3],S[4],MPFR_RNDU);
    if(mpfr_cmp_si(s->lo,-1)<0) mpfr_set_si(s->lo,-1,MPFR_RNDN);
    if(mpfr_cmp_si(s->hi,1)>0) mpfr_set_si(s->hi,1,MPFR_RNDN);
    if(mpfr_cmp_si(c->lo,-1)<0) mpfr_set_si(c->lo,-1,MPFR_RNDN);
    if(mpfr_cmp_si(c->hi,1)>0) mpfr_set_si(c->hi,1,MPFR_RNDN);
}
static void iv_sin(iv*s,const iv*z){
    mpfr_sin(S[0],z->lo,MPFR_RNDD); mpfr_sin(S[1],z->lo,MPFR_RNDU); iv_width_up(S[2],z);
    mpfr_sub(s->lo,S[0],S[2],MPFR_RNDD); mpfr_add(s->hi,S[1],S[2],MPFR_RNDU);
    if(mpfr_cmp_si(s->lo,-1)<0) mpfr_set_si(s->lo,-1,MPFR_RNDN);
    if(mpfr_cmp_si(s->hi,1)>0) mpfr_set_si(s->hi,1,MPFR_RNDN);
}
static void iv_set_dyadic(iv*r,unsigned long num,unsigned depth){ mpfr_set_ui(r->lo,num,MPFR_RNDN); mpfr_set_ui(r->hi,num,MPFR_RNDN); mpfr_div_2ui(r->lo,r->lo,depth,MPFR_RNDD); mpfr_div_2ui(r->hi,r->hi,depth,MPFR_RNDU); }
static void print_mpfr(const char*label,mpfr_srcptr x,mpfr_rnd_t rnd){
    mpfr_exp_t e; char *s=mpfr_get_str(NULL,&e,10,55,x,rnd); if(!s){fprintf(stderr,"mpfr_get_str failed\n");exit(2);} int neg=s[0]=='-'; char *d=s+neg;
    printf("%s%s",label,neg?"-":"");
    long n=(long)strlen(d); if(e<=0){ printf("0."); for(long k=0;k<-e;k++) putchar('0'); printf("%s",d); }
    else if(e>=n){ printf("%s",d); for(long k=n;k<e;k++) putchar('0'); }
    else { fwrite(d,1,e,stdout); putchar('.'); printf("%s",d+e); }
    putchar('\n'); mpfr_free_str(s);
}
#define NCOS 67
static const char *COS_XI[NCOS] = {
  "5.94",
  "8.4575",
  "12.375",
  "15.5725",
  "19.5425",
  "26.995",
  "239.0",
  "236.0",
  "241.0",
  "34.175",
  "238.0",
  "233.0",
  "230.0",
  "34.18",
  "45.9",
  "53.105",
  "223.0",
  "41.745",
  "60.34",
  "227.0",
  "71.975",
  "315.0",
  "248.0",
  "216.0",
  "384.0",
  "396.0",
  "79.125",
  "254.0",
  "386.0",
  "393.0",
  "318.0",
  "64.42",
  "394.0",
  "387.0",
  "204.0",
  "251.0",
  "91.0",
  "395.0",
  "197.0",
  "220.0",
  "398.0",
  "178.0",
  "98.0",
  "185.0",
  "377.0",
  "171.0",
  "65.0",
  "266.0",
  "53.0",
  "319.0",
  "110.0",
  "273.0",
  "303.0",
  "117.0",
  "314.0",
  "330.0",
  "152.0",
  "337.0",
  "159.0",
  "363.0",
  "296.0",
  "129.0",
  "136.0",
  "133.0",
  "344.0",
  "280.0",
  "277.0",
};
static const char *COS_LAM[NCOS] = {
  "1.0230933146835715",
  "0.47535617303305511",
  "0.051009114495356889",
  "0.034527751929396409",
  "0.016889780247218395",
  "0.010021649031901293",
  "0.0042329485203203105",
  "0.0044917626716982984",
  "0.0032967230726984394",
  "0.0020033279127706864",
  "0.003736546544791752",
  "0.0016447611914560442",
  "0.0012733766318358904",
  "0.0020625174466540608",
  "0.0011979613976897978",
  "0.00094121674820510869",
  "0.00036076325204575276",
  "0.00040230617624297297",
  "0.00037692749584266504",
  "0.00016216251030171217",
  "0.00027244592112089593",
  "0.0002496954101366998",
  "0.0005514611374958636",
  "0.00013676463902173632",
  "0.00011443041185031464",
  "0.00025071127763396907",
  "0.00016528412807061512",
  "0.00018882940339776976",
  "0.0001209130590590535",
  "0.00019297757342074203",
  "0.00010591489483309285",
  "0.00010811954124585025",
  "0.0001170794231096379",
  "7.7182419046665173e-05",
  "6.6713775507927593e-05",
  "0.00029633597187699398",
  "9.2181610899834548e-05",
  "0.00013487416224809454",
  "5.1571211412524556e-05",
  "2.2260861152019126e-05",
  "0.00012140566834728751",
  "5.0717056588485439e-05",
  "6.4655203518422841e-05",
  "4.6753725264613114e-05",
  "1.0559396964939274e-05",
  "2.7148023408066858e-05",
  "3.6161816690576719e-05",
  "5.6641557565643058e-05",
  "4.7450365440641277e-05",
  "4.8485428923194814e-05",
  "4.3341886065436888e-05",
  "4.3270574645282114e-05",
  "2.730543899463523e-05",
  "3.4617499446360873e-05",
  "3.9501228880864125e-05",
  "1.9360903830070443e-05",
  "1.0246317346047647e-05",
  "1.2375042636550744e-05",
  "2.2176122829166203e-05",
  "2.4277320505726663e-06",
  "1.9414513494100157e-05",
  "2.6879476724131092e-05",
  "2.5130467526573969e-05",
  "1.8764991268726487e-06",
  "1.01390347727792e-05",
  "2.0825872274814842e-05",
  "2.2563234384125296e-06",
};
static const char *T2_LAM = "0.88381079229395987";
static const char *PV_LAM = "0.00042782508050180287";
#define PV_N 100


static term_t TERMS[NCOS+PV_N];
static int NTERMS=0;
static iv QCONST, QB2, PIIV;
static mpfr_t M2UP;

static void prepared_init(void){
    scratch_init(); iv_init(&QCONST); iv_init(&QB2); iv_init(&PIIV); mpfr_init2(M2UP,PREC); iv_set_si(&QCONST,1); iv_set_si(&QB2,0); iv_set_pi(&PIIV); mpfr_set_si(M2UP,0,MPFR_RNDN);
    iv lam,tmp,B,s,c,sinc,w,ccoef,dc,anti;
    iv_init(&lam);iv_init(&tmp);iv_init(&B);iv_init(&s);iv_init(&c);iv_init(&sinc);iv_init(&w);iv_init(&ccoef);iv_init(&dc);iv_init(&anti);
    /* t^2 row */
    iv_set_dec(&lam,T2_LAM); if(mpfr_cmp_si(lam.lo,0)<0){fprintf(stderr,"negative t2 lambda\n");exit(2);} 
    iv_set_ratio(&B,2,3); iv_set_ratio(&tmp,1,204800); iv_add(&B,&B,&tmp); mpfr_set(B.lo,B.hi,MPFR_RNDN); /* choose certified upper RHS */
    iv_mul(&tmp,&lam,&B); iv_add(&QCONST,&QCONST,&tmp); iv_sub(&QB2,&QB2,&lam);
    /* individual cosine rows */
    for(int j=0;j<NCOS;j++){
        iv_set_dec(&w,COS_XI[j]); iv_set_dec(&lam,COS_LAM[j]); if(mpfr_cmp_si(lam.lo,0)<0){fprintf(stderr,"negative cosine lambda\n");exit(2);} 
        iv_sincos(&s,&c,&w); iv_div_pos(&sinc,&s,&w); iv_square(&B,&sinc); mpfr_set(B.lo,B.hi,MPFR_RNDN);
        iv_mul(&tmp,&lam,&B); iv_add(&QCONST,&QCONST,&tmp);
        term_t *t=&TERMS[NTERMS++]; iv_init(&t->w);iv_init(&t->c);iv_init(&t->dc);iv_init(&t->anti); iv_set(&t->w,&w); iv_neg(&ccoef,&lam); iv_set(&t->c,&ccoef);
        iv_mul(&dc,&ccoef,&w); iv_neg(&dc,&dc); iv_set(&t->dc,&dc); iv_div_pos(&anti,&ccoef,&w); iv_set(&t->anti,&anti);
    }
    /* Parseval row: q contribution lambda*(1/2 + sum_{n=1}^N cos(n pi t)). */
    iv_set_dec(&lam,PV_LAM); if(mpfr_cmp_si(lam.lo,0)<0){fprintf(stderr,"negative parseval lambda\n");exit(2);} iv_set_ratio(&B,1,2); iv_mul(&tmp,&lam,&B); iv_add(&QCONST,&QCONST,&tmp);
    for(int n=1;n<=PV_N;n++){
        term_t*t=&TERMS[NTERMS++]; iv_init(&t->w);iv_init(&t->c);iv_init(&t->dc);iv_init(&t->anti);
        iv_set_si(&tmp,n); iv_mul(&w,&PIIV,&tmp); iv_set(&t->w,&w); iv_set(&t->c,&lam); iv_mul(&dc,&lam,&w); iv_neg(&dc,&dc); iv_set(&t->dc,&dc); iv_div_pos(&anti,&lam,&w); iv_set(&t->anti,&anti);
    }
    /* M2 >= sup |q''| = 2|b2| + sum |c| w^2. */
    iv_abs_upper(S[0],&QB2); mpfr_mul_ui(M2UP,S[0],2,MPFR_RNDU);
    for(int j=0;j<NTERMS;j++){
        iv_abs_upper(S[0],&TERMS[j].c); iv_abs_upper(S[1],&TERMS[j].w); mpfr_mul(S[2],S[1],S[1],MPFR_RNDU); mpfr_mul(S[3],S[0],S[2],MPFR_RNDU); mpfr_add(M2UP,M2UP,S[3],MPFR_RNDU);
    }
    iv_clear(&lam);iv_clear(&tmp);iv_clear(&B);iv_clear(&s);iv_clear(&c);iv_clear(&sinc);iv_clear(&w);iv_clear(&ccoef);iv_clear(&dc);iv_clear(&anti);
}
static void prepared_clear(void){ for(int j=0;j<NTERMS;j++){iv_clear(&TERMS[j].w);iv_clear(&TERMS[j].c);iv_clear(&TERMS[j].dc);iv_clear(&TERMS[j].anti);} iv_clear(&QCONST);iv_clear(&QB2);iv_clear(&PIIV);mpfr_clear(M2UP);scratch_clear(); }

static void q_eval(iv*q,iv*qd,const iv*x){
    iv x2,z,s,c,tmp;iv_init(&x2);iv_init(&z);iv_init(&s);iv_init(&c);iv_init(&tmp);
    iv_square(&x2,x); iv_mul(&tmp,&QB2,&x2); iv_add(q,&QCONST,&tmp); iv_mul(&tmp,&QB2,x); iv_add(qd,&tmp,&tmp);
    for(int j=0;j<NTERMS;j++){ iv_mul(&z,&TERMS[j].w,x); iv_sincos(&s,&c,&z); iv_mul(&tmp,&TERMS[j].c,&c); iv_add(q,q,&tmp); iv_mul(&tmp,&TERMS[j].dc,&s); iv_add(qd,qd,&tmp); }
    iv_clear(&x2);iv_clear(&z);iv_clear(&s);iv_clear(&c);iv_clear(&tmp);
}
static void Q_eval(iv*out,const iv*x){
    iv x2,x3,z,s,tmp;iv_init(&x2);iv_init(&x3);iv_init(&z);iv_init(&s);iv_init(&tmp);
    iv_mul(out,&QCONST,x); iv_square(&x2,x); iv_mul(&x3,&x2,x); iv_mul(&tmp,&QB2,&x3); mpfr_div_ui(tmp.lo,tmp.lo,3,MPFR_RNDD); mpfr_div_ui(tmp.hi,tmp.hi,3,MPFR_RNDU); iv_add(out,out,&tmp);
    for(int j=0;j<NTERMS;j++){ iv_mul(&z,&TERMS[j].w,x); iv_sin(&s,&z); iv_mul(&tmp,&TERMS[j].anti,&s); iv_add(out,out,&tmp); }
    iv_clear(&x2);iv_clear(&x3);iv_clear(&z);iv_clear(&s);iv_clear(&tmp);
}

typedef struct { uint32_t i; uint16_t d; } cell_t;
int main(int argc,char**argv){
    int base_depth=8, terminal_depth=17; long max_nodes=2000000; const char*target_s="0.380557";
    for(int a=1;a<argc;a++){ if(!strcmp(argv[a],"--base-depth")&&a+1<argc)base_depth=atoi(argv[++a]); else if(!strcmp(argv[a],"--terminal-depth")&&a+1<argc)terminal_depth=atoi(argv[++a]); else if(!strcmp(argv[a],"--target")&&a+1<argc)target_s=argv[++a]; else if(!strcmp(argv[a],"--max-nodes")&&a+1<argc)max_nodes=atol(argv[++a]); else {fprintf(stderr,"usage: %s [--base-depth 8] [--terminal-depth 17] [--target 0.380557] [--max-nodes N]\n",argv[0]);return 2;} }
    if(base_depth<1||terminal_depth<base_depth||terminal_depth>29){fprintf(stderr,"bad depths\n");return 2;}
    prepared_init();
    iv target,one,tD;iv_init(&target);iv_init(&one);iv_init(&tD);iv_set_dec(&target,target_s);iv_set_si(&one,1);iv_div_pos(&tD,&one,&target);
    cell_t *stack=malloc((size_t)max_nodes*sizeof(cell_t)); if(!stack){fprintf(stderr,"alloc failed\n");return 2;} long sp=0; for(uint32_t i=0;i<(1u<<base_depth);i++)stack[sp++]=(cell_t){i,(uint16_t)base_depth};
    mpfr_t Dhalf,rad,r,r2,hi,lo,contrib,D,Dmargin; mpfr_init2(Dhalf,PREC);mpfr_init2(rad,PREC);mpfr_init2(r,PREC);mpfr_init2(r2,PREC);mpfr_init2(hi,PREC);mpfr_init2(lo,PREC);mpfr_init2(contrib,PREC);mpfr_init2(D,PREC);mpfr_init2(Dmargin,PREC);mpfr_set_si(Dhalf,0,MPFR_RNDN);
    iv x,q,qd,Qa,Qb;iv_init(&x);iv_init(&q);iv_init(&qd);iv_init(&Qa);iv_init(&Qb);
    long nodes=0,pos=0,neg=0,amb=0; long maxsp=sp; clock_t t0=clock();
    while(sp){ cell_t z=stack[--sp]; nodes++; if(nodes>max_nodes){fprintf(stderr,"max_nodes exceeded\n");return 2;} uint32_t i=z.i;unsigned d=z.d;
        iv_set_dyadic(&x,(unsigned long)(2u*i+1u),d); mpfr_set_ui(r,1,MPFR_RNDN);mpfr_div_2ui(r,r,d,MPFR_RNDU); q_eval(&q,&qd,&x); iv_abs_upper(S[0],&qd); mpfr_mul(rad,S[0],r,MPFR_RNDU); mpfr_mul(r2,r,r,MPFR_RNDU); mpfr_mul(S[1],M2UP,r2,MPFR_RNDU);mpfr_div_ui(S[1],S[1],2,MPFR_RNDU);mpfr_add(rad,rad,S[1],MPFR_RNDU); mpfr_add(hi,q.hi,rad,MPFR_RNDU);mpfr_sub(lo,q.lo,rad,MPFR_RNDD);
        if(mpfr_cmp_si(hi,0)<=0){neg++;continue;} if(mpfr_cmp_si(lo,0)>=0){
            iv_set_dyadic(&x,(unsigned long)(2u*i),d);Q_eval(&Qa,&x);iv_set_dyadic(&x,(unsigned long)(2u*(i+1u)),d);Q_eval(&Qb,&x);mpfr_sub(contrib,Qb.hi,Qa.lo,MPFR_RNDU); if(mpfr_cmp_si(contrib,0)<0){fprintf(stderr,"negative positive-cell integral?\n");return 2;} mpfr_add(Dhalf,Dhalf,contrib,MPFR_RNDU);pos++;continue; }
        if((int)d>=terminal_depth){ mpfr_set_ui(S[0],2,MPFR_RNDN);mpfr_div_2ui(S[0],S[0],d,MPFR_RNDU);mpfr_mul(contrib,S[0],hi,MPFR_RNDU);mpfr_add(Dhalf,Dhalf,contrib,MPFR_RNDU);amb++;continue; }
        if(sp+2>=max_nodes){fprintf(stderr,"stack overflow\n");return 2;} stack[sp++]=(cell_t){2u*i+1u,(uint16_t)(d+1)};stack[sp++]=(cell_t){2u*i,(uint16_t)(d+1)};if(sp>maxsp)maxsp=sp;
        if(nodes%10000==0)fprintf(stderr,"nodes=%ld stack=%ld pos=%ld neg=%ld amb=%ld Dhalf<=%.17g\n",nodes,sp,pos,neg,amb,mpfr_get_d(Dhalf,MPFR_RNDU));
    }
    mpfr_mul_ui(D,Dhalf,2,MPFR_RNDU); mpfr_sub(Dmargin,tD.lo,D,MPFR_RNDD); int ok=mpfr_cmp(D,tD.lo)<0;
    printf("MPFR independent verifier\n");printf("terms: %d (67 individual cosine + 100 Parseval modes)\n",NTERMS);print_mpfr("M2_upper: ",M2UP,MPFR_RNDU);print_mpfr("D_upper: ",D,MPFR_RNDU);print_mpfr("target_D_lower: ",tD.lo,MPFR_RNDD);print_mpfr("margin_lower: ",Dmargin,MPFR_RNDD);printf("nodes: %ld\npositive_cells: %ld\nnegative_cells: %ld\nambiguous_terminal_cells: %ld\nbase_depth: %d\nterminal_depth: %d\nmax_stack: %ld\nelapsed_cpu_seconds: %.6f\n",nodes,pos,neg,amb,base_depth,terminal_depth,maxsp,(double)(clock()-t0)/CLOCKS_PER_SEC);printf("CERTIFIED %s\n",ok?"True":"False");
    free(stack);iv_clear(&x);iv_clear(&q);iv_clear(&qd);iv_clear(&Qa);iv_clear(&Qb);mpfr_clear(Dhalf);mpfr_clear(rad);mpfr_clear(r);mpfr_clear(r2);mpfr_clear(hi);mpfr_clear(lo);mpfr_clear(contrib);mpfr_clear(D);mpfr_clear(Dmargin);iv_clear(&target);iv_clear(&one);iv_clear(&tD);prepared_clear();return ok?0:1;
}
