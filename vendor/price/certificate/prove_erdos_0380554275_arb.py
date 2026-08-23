#!/usr/bin/env python3
"""
Arb/ball-arithmetic verifier for the Erdős minimum-overlap certificate.

The script verifies the finite dual certificate

    q_I(t) = 1 + sum_j lambda_j (B_j - phi_j(t)),  lambda_j >= 0,

for each mean bin I.  For correctness, B_j is recomputed as an outward Arb upper
bound for the corresponding mathematical RHS; the stored B values are not trusted.
Floating-point root searches are used only to seed a subdivision.  Every interval
in the final subdivision is certified using Arb balls and the Taylor majorant

    q(x) <= q(c) + |q'(c)| r + M2 r^2/2.
"""
from __future__ import annotations

import argparse, csv, json, math, time
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import brentq
from flint import arb, ctx


def A(x: Any) -> arb:
    return arb(str(x))


def D(x: Any) -> Decimal:
    return Decimal(str(x))


def upper(x: arb) -> arb:
    return x.upper()


def pos_upper(x: arb) -> arb:
    return arb(0) if x <= 0 else x.upper()


def sinc(x: arb) -> arb:
    if x.contains(arb(0)):
        return x.sinc()
    return x.sin() / x


def sqrt_max0_upper(x: arb) -> arb:
    if x <= 0:
        return arb(0)
    u = x.upper()
    if u <= 0:
        return arb(0)
    return u.sqrt()


def rhs_expected(kind: str, param: Any, lo_raw: Any, hi_raw: Any) -> Optional[arb]:
    loD, hiD = D(lo_raw), D(hi_raw)
    lo, hi = A(lo_raw), A(hi_raw)
    if loD <= 0 <= hiD:
        min_mu2 = arb(0)
    else:
        min_mu2 = A(min(loD * loD, hiD * hiD))
    max_mu2 = A(max(loD * loD, hiD * hiD))
    m2_lo = arb(2) / 3 + min_mu2 / 2
    m2_hi = arb(2) / 3 + max_mu2 / 2

    if kind == "t":
        return hi
    if kind == "-t":
        return -lo
    if kind == "t2":
        return m2_hi
    if kind == "-t2":
        return -m2_lo
    if kind == "cos":
        s = sinc(A(param)); return s * s
    if kind == "-cos":
        s = sinc(A(param)); return arb(1) - 2 * s * s
    if kind in ("sin", "-sin"):
        s = sinc(A(param))
        return 2 * s.abs_upper() * sqrt_max0_upper(arb(1) - s * s)
    if kind == "cos+asin":
        xi, alpha = A(param[0]), A(param[1])
        s = sinc(xi)
        return (arb(1) + alpha * alpha) * s * s
    return None


class Term:
    __slots__ = ("kind", "param", "lam", "B", "xi", "alpha")
    def __init__(self, kind: str, param: Any, lam: arb, B: arb):
        self.kind = kind; self.param = param; self.lam = lam; self.B = B
        self.xi = None; self.alpha = None
        if kind in ("cos", "-cos", "sin", "-sin"):
            self.xi = A(param)
        elif kind == "cos+asin":
            self.xi = A(param[0]); self.alpha = A(param[1])


def phi_float(kind: str, param: Any, x: float) -> float:
    if kind == "t": return x
    if kind == "-t": return -x
    if kind == "t2": return x*x
    if kind == "-t2": return -x*x
    if kind == "cos": return math.cos(float(param)*x)
    if kind == "-cos": return -math.cos(float(param)*x)
    if kind == "sin": return math.sin(float(param)*x)
    if kind == "-sin": return -math.sin(float(param)*x)
    if kind == "cos+asin":
        xi, alpha = float(param[0]), float(param[1])
        return math.cos(xi*x) + alpha*math.sin(xi*x)
    raise ValueError(kind)


def phi_vec(kind: str, param: Any, x: np.ndarray) -> np.ndarray:
    if kind == "t": return x
    if kind == "-t": return -x
    if kind == "t2": return x*x
    if kind == "-t2": return -x*x
    if kind == "cos": return np.cos(float(param)*x)
    if kind == "-cos": return -np.cos(float(param)*x)
    if kind == "sin": return np.sin(float(param)*x)
    if kind == "-sin": return -np.sin(float(param)*x)
    if kind == "cos+asin":
        xi, alpha = float(param[0]), float(param[1])
        return np.cos(xi*x) + alpha*np.sin(xi*x)
    raise ValueError(kind)


def prepare_bin(cert: Dict[str, Any], rhs_inflate: arb) -> Tuple[List[Term], List[Tuple[str, Any, float, float]], arb, int]:
    terms: List[Term] = []
    fterms: List[Tuple[str, Any, float, float]] = []
    M2 = arb(0)
    adjusted = 0
    for j, raw in enumerate(cert["active"]):
        kind, param = raw["kind"], raw.get("param")
        if D(raw["lambda"]) < 0:
            raise ValueError(f"negative multiplier in bin {cert['lo']},{cert['hi']} term {j}")
        lam = A(raw["lambda"])
        e = rhs_expected(kind, param, cert["lo"], cert["hi"])
        if e is None:
            B = A(raw["B"]) + rhs_inflate
        else:
            B = e.upper() + rhs_inflate
            adjusted += 1
        terms.append(Term(kind, param, lam, B))
        fterms.append((kind, param, float(raw["lambda"]), float(B)))
        # global bound for |q''|
        lu = lam.abs_upper()
        if kind in ("t", "-t"):
            pass
        elif kind in ("t2", "-t2"):
            M2 += 2 * lu
        elif kind in ("cos", "-cos", "sin", "-sin"):
            xi = A(param)
            M2 += lu * xi.abs_upper() * xi.abs_upper()
        elif kind == "cos+asin":
            xi, alpha = A(param[0]), A(param[1])
            amp = (arb(1) + alpha * alpha).sqrt()
            M2 += lu * xi.abs_upper() * xi.abs_upper() * amp.abs_upper()
        else:
            raise ValueError(f"unknown term kind {kind}")
    return terms, fterms, M2.upper(), adjusted


def q_float(fterms: Sequence[Tuple[str, Any, float, float]], x: float) -> float:
    parts = [1.0]
    for kind, param, lam, B in fterms:
        if lam:
            parts.append(lam * (B - phi_float(kind, param, x)))
    return math.fsum(parts)


def q_vec(fterms: Sequence[Tuple[str, Any, float, float]], x: np.ndarray) -> np.ndarray:
    out = np.ones_like(x, dtype=float)
    for kind, param, lam, B in fterms:
        if lam:
            out += lam * (B - phi_vec(kind, param, x))
    return out


def speed_roots(fterms: Sequence[Tuple[str, Any, float, float]], samples: int) -> List[float]:
    if samples <= 1:
        return []
    xs = np.linspace(-2.0, 2.0, samples)
    ys = q_vec(fterms, xs)
    roots: List[float] = []
    for i in range(samples - 1):
        fa, fb = float(ys[i]), float(ys[i+1])
        if fa == 0.0:
            roots.append(float(xs[i]))
        elif fa * fb < 0.0:
            try:
                roots.append(brentq(lambda z: q_float(fterms, z), float(xs[i]), float(xs[i+1]), xtol=1e-14, rtol=1e-14, maxiter=100))
            except Exception:
                pass
    if float(ys[-1]) == 0.0:
        roots.append(2.0)
    roots.sort()
    out: List[float] = []
    for r in roots:
        if not out or abs(r - out[-1]) > 1e-8:
            out.append(r)
    return out


def initial_intervals(roots: Sequence[float], pad: float) -> List[Tuple[str, str]]:
    if not roots:
        return [("-2.0", "2.0")]
    ans: List[Tuple[str, str]] = []
    last = -2.0
    for r in roots:
        a, b = max(-2.0, r - pad), min(2.0, r + pad)
        if a > last:
            ans.append((repr(last), repr(a)))
        if b > a:
            ans.append((repr(a), repr(b)))
        last = max(last, b)
    if last < 2.0:
        ans.append((repr(last), "2.0"))
    return ans


def q_qd(terms: Sequence[Term], x: arb) -> Tuple[arb, arb]:
    q, qd = arb(1), arb(0)
    for t in terms:
        lam = t.lam
        if lam == 0:
            continue
        k = t.kind
        if k == "t":
            phi, phid = x, arb(1)
        elif k == "-t":
            phi, phid = -x, -arb(1)
        elif k == "t2":
            phi, phid = x*x, 2*x
        elif k == "-t2":
            phi, phid = -x*x, -2*x
        elif k in ("cos", "-cos", "sin", "-sin"):
            xi = t.xi
            s, c = (xi * x).sin_cos()
            if k == "cos":
                phi, phid = c, -xi*s
            elif k == "-cos":
                phi, phid = -c, xi*s
            elif k == "sin":
                phi, phid = s, xi*c
            else:
                phi, phid = -s, -xi*c
        elif k == "cos+asin":
            xi, alpha = t.xi, t.alpha
            s, c = (xi * x).sin_cos()
            phi = c + alpha*s
            phid = -xi*s + alpha*xi*c
        else:
            raise ValueError(k)
        q += lam * (t.B - phi)
        qd += -lam * phid
    return q, qd


def Q(terms: Sequence[Term], x: arb) -> arb:
    val = x
    for t in terms:
        lam = t.lam
        if lam == 0:
            continue
        k = t.kind
        val += lam * t.B * x
        if k == "t":
            anti = x*x/2
        elif k == "-t":
            anti = -x*x/2
        elif k == "t2":
            anti = x*x*x/3
        elif k == "-t2":
            anti = -x*x*x/3
        elif k in ("cos", "-cos", "sin", "-sin"):
            xi = t.xi
            s, c = (xi * x).sin_cos()
            if k == "cos":
                anti = s / xi
            elif k == "-cos":
                anti = -s / xi
            elif k == "sin":
                anti = -c / xi
            else:
                anti = c / xi
        elif k == "cos+asin":
            xi, alpha = t.xi, t.alpha
            s, c = (xi * x).sin_cos()
            anti = s / xi - alpha * c / xi
        else:
            raise ValueError(k)
        val -= lam * anti
    return val


def upper_integral_bin(cert: Dict[str, Any], cell_width: Decimal, root_pad: float, samples: int, max_nodes: int, rhs_inflate: arb) -> Tuple[arb, Dict[str, Any]]:
    terms, fterms, M2, adjusted = prepare_bin(cert, rhs_inflate)
    roots = speed_roots(fterms, samples)
    stack = initial_intervals(roots, root_pad)
    Dtot = arb(0)
    nodes = amb = pos = neg = 0
    half = arb(1) / 2
    while stack:
        a_s, b_s = stack.pop()
        aD, bD = Decimal(a_s), Decimal(b_s)
        if bD <= aD:
            continue
        nodes += 1
        if nodes > max_nodes:
            raise RuntimeError(f"max_nodes exceeded in bin [{cert['lo']},{cert['hi']}]")
        a, b = A(a_s), A(b_s)
        c, r = (a+b)/2, (b-a)/2
        qc, qdc = q_qd(terms, c)
        rad = qdc.abs_upper() * r + half * M2 * r * r
        lo, hi = qc - rad, qc + rad
        if hi <= 0:
            neg += 1
            continue
        if lo >= 0:
            Dtot += pos_upper(Q(terms, b) - Q(terms, a))
            pos += 1
            continue
        if bD - aD <= cell_width:
            Dtot += (b-a) * pos_upper(hi)
            amb += 1
            continue
        mD = (aD + bD) / 2
        m_s = format(mD, "f")
        stack.append((m_s, b_s)); stack.append((a_s, m_s))
    info = {
        "nodes": nodes,
        "ambiguous_cells": amb,
        "positive_cells": pos,
        "negative_cells": neg,
        "speed_roots": len(roots),
        "rhs_adjusted": adjusted,
        "M2": M2.str(30),
    }
    return Dtot, info


def repair_tiny_bin_gaps(data: Dict[str, Any], max_gap: Decimal = Decimal("1e-12")) -> int:
    bins = data["bins"]
    if not bins:
        return 0
    changed = 0
    lo0 = D(bins[0]["lo"])
    if lo0 > Decimal("-1"):
        gap = lo0 - Decimal("-1")
        if gap <= max_gap:
            bins[0]["lo"] = "-1"
            changed += 1
        else:
            raise ValueError(f"initial uncovered mean gap: {gap}")
    prev = D(bins[0]["hi"])
    for i in range(1, len(bins)):
        lo = D(bins[i]["lo"])
        if lo > prev:
            gap = lo - prev
            if gap <= max_gap:
                bins[i]["lo"] = format(prev, "f")
                changed += 1
            else:
                raise ValueError(f"uncovered mean gap before bin {i}: {gap}")
        hi = D(bins[i]["hi"])
        if hi > prev:
            prev = hi
    if prev < Decimal("1"):
        gap = Decimal("1") - prev
        if gap <= max_gap:
            bins[-1]["hi"] = "1"; changed += 1
        else:
            raise ValueError(f"final uncovered mean gap: {gap}")
    return changed


def parse_bins(s: Optional[str], n: int) -> List[int]:
    if not s:
        return list(range(n))
    ans: List[int] = []
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            ans.extend(range(int(a), int(b)+1))
        else:
            ans.append(int(part))
    return ans


def verify(data: Dict[str, Any], target_s: str, bins: List[int], cell_width_s: str, root_pad: float, samples: int, max_nodes: int, rhs_inflate_s: str, csv_path: Optional[Path]) -> Dict[str, Any]:
    targetD = arb(1) / A(target_s)
    cell_width = Decimal(cell_width_s)
    rhs_inflate = A(rhs_inflate_s)
    rows = []
    failures = []
    worst_i = None
    worst_D = None
    total_nodes = total_amb = max_roots = 0
    t0 = time.time()
    for i in bins:
        cert = data["bins"][i]
        U, info = upper_integral_bin(cert, cell_width, root_pad, samples, max_nodes, rhs_inflate)
        ok = U < targetD
        if worst_D is None or U > worst_D:
            worst_D = U; worst_i = i
        total_nodes += info["nodes"]; total_amb += info["ambiguous_cells"]; max_roots = max(max_roots, info["speed_roots"])
        row = {
            "bin_index": i, "lo": cert["lo"], "hi": cert["hi"],
            "D_upper_ball": U.str(50), "D_upper_float": float(U.upper()),
            "proved": bool(ok), **info,
        }
        rows.append(row)
        if not ok:
            failures.append(row)
        print(f"bin {i:3d}: D <= {U.upper().str(24)}  {'OK' if ok else 'FAIL'}  nodes={info['nodes']} amb={info['ambiguous_cells']} roots={info['speed_roots']}", flush=True)
    if csv_path and rows:
        with csv_path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    lower_bound = arb(1) / worst_D if worst_D is not None else None
    return {
        "target": target_s,
        "target_D": targetD.str(60),
        "worst_bin_index": worst_i,
        "worst_bin": [data["bins"][worst_i]["lo"], data["bins"][worst_i]["hi"]] if worst_i is not None else None,
        "worst_D_upper_ball": worst_D.upper().str(60) if worst_D is not None else None,
        "certified_lower_bound_ball": lower_bound.str(60) if lower_bound is not None else None,
        "certified_lower_bound_lower_float": float(lower_bound.lower()) if lower_bound is not None else None,
        "proved_all_checked_bins": len(failures) == 0,
        "failures": failures,
        "checked_bins": bins,
        "total_nodes": total_nodes,
        "total_ambiguous_cells": total_amb,
        "max_speed_roots": max_roots,
        "elapsed_seconds": time.time() - t0,
        "arb_precision_bits": ctx.prec,
        "cell_width": cell_width_s,
        "root_pad": root_pad,
        "samples": samples,
        "rhs_inflate": rhs_inflate_s,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate_json", type=Path)
    ap.add_argument("--target", default="0.380554275")
    ap.add_argument("--prec", type=int, default=160)
    ap.add_argument("--cell-width", default="0.0001")
    ap.add_argument("--root-pad", type=float, default=1e-4)
    ap.add_argument("--samples", type=int, default=120001)
    ap.add_argument("--max-nodes", type=int, default=50000000)
    ap.add_argument("--rhs-inflate", default="1e-14")
    ap.add_argument("--only-bins", default=None)
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--json-report", type=Path)
    args = ap.parse_args(argv)
    ctx.prec = args.prec
    getcontext().prec = 80
    data = json.loads(args.certificate_json.read_text(), parse_float=str, parse_int=str)
    repaired = repair_tiny_bin_gaps(data)
    if repaired:
        print(f"Repaired {repaired} tiny bin endpoint gap(s) conservatively.")
    bins = parse_bins(args.only_bins, len(data["bins"]))
    result = verify(data, args.target, bins, args.cell_width, args.root_pad, args.samples, args.max_nodes, args.rhs_inflate, args.csv)
    if args.json_report:
        args.json_report.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print("\nArb verification summary")
    for k in ["target", "target_D", "worst_D_upper_ball", "certified_lower_bound_ball", "worst_bin_index", "worst_bin", "total_nodes", "total_ambiguous_cells", "max_speed_roots", "elapsed_seconds", "arb_precision_bits"]:
        print(f"  {k}: {result[k]}")
    if result["proved_all_checked_bins"]:
        print("SUCCESS: every checked bin certifies the target.")
        return 0
    print("FAILED bins:")
    for row in result["failures"][:20]:
        print(row)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
