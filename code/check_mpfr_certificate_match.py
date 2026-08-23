#!/usr/bin/env python3
"""Check that the certificate constants embedded in verify_center_mpfr.c exactly match the JSON."""
from pathlib import Path
import json, re, sys
HERE=Path(__file__).resolve().parent
cert=json.loads((HERE.parent/'certificate'/'center_certificate.json').read_text())
src=(HERE/'verify_center_mpfr.c').read_text()

def c_string_array(name):
    m=re.search(rf'static const char \*{name}\[NCOS\] = \{{(.*?)\}};',src,re.S)
    if not m: raise SystemExit(f'missing C array {name}')
    return re.findall(r'"([^"]+)"',m.group(1))

def c_string(name):
    m=re.search(rf'static const char \*{name} = "([^"]+)";',src)
    if not m: raise SystemExit(f'missing C string {name}')
    return m.group(1)

def c_int_macro(name):
    m=re.search(rf'#define\s+{name}\s+(\d+)',src)
    if not m: raise SystemExit(f'missing C macro {name}')
    return int(m.group(1))

cos=[r for r in cert['active'] if r['kind']=='cos_u']
t2=[r for r in cert['active'] if r['kind']=='t2']
pv=[r for r in cert['active'] if r['kind']=='parseval0']
assert len(cos)==67 and len(t2)==1 and len(pv)==1
checks={
    'COS_XI': (c_string_array('COS_XI'), [str(r['param']) for r in cos]),
    'COS_LAM': (c_string_array('COS_LAM'), [str(r['lambda']) for r in cos]),
    'T2_LAM': (c_string('T2_LAM'), str(t2[0]['lambda'])),
    'PV_LAM': (c_string('PV_LAM'), str(pv[0]['lambda'])),
    'PV_N': (c_int_macro('PV_N'), int(pv[0]['param'])),
}
for name,(got,want) in checks.items():
    if got!=want:
        print(f'MISMATCH {name}',file=sys.stderr)
        print('C   =',got,file=sys.stderr)
        print('JSON=',want,file=sys.stderr)
        raise SystemExit(1)
print('MATCH True')
print('cosine_rows 67')
print('t2_rows 1')
print('parseval_rows 1')
