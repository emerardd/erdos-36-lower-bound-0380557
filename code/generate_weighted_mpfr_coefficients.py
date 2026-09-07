#!/usr/bin/env python3
"""Generate the direct-MPFR coefficient stream exactly from the frozen JSON.

The frozen JSON is the sole coefficient source of truth. All decimal literals
are parsed exactly with Decimal -> Fraction. Products and differences are done
with Fraction, then rendered back as terminating decimal strings without a
finite-precision Decimal context.

The original search uses the 400 harmonics n=1,...,400. The frozen JSON carries
one legacy trailing zero placeholder in window_weights. We accept that only
when it is exactly zero and normalize it away; a nonzero 401st entry is rejected.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CERT = ROOT / "certificate" / "weighted_center_certificate_038056070.json"


def rat(s: str) -> Fraction:
    return Fraction(Decimal(s))


def canonical_weights(d: dict) -> list[Fraction]:
    weights = [rat(x) for x in d["window_weights"]]
    if len(weights) == 401:
        if weights[-1] != 0:
            raise ValueError("legacy 401st window entry must be exactly zero")
        weights = weights[:-1]
    if len(weights) != 400:
        raise ValueError(f"expected 400 effective window weights, got {len(weights)}")
    return weights


def terminating_decimal(q: Fraction) -> str:
    if q == 0:
        return "0"
    sign = "-" if q < 0 else ""
    q = abs(q)
    num, den = q.numerator, q.denominator
    a = b = 0
    while den % 2 == 0:
        den //= 2
        a += 1
    while den % 5 == 0:
        den //= 5
        b += 1
    if den != 1:
        raise ValueError(f"non-terminating rational denominator: {q.denominator}")
    k = max(a, b)
    scaled = num * (2 ** (k - a)) * (5 ** (k - b))
    s = str(scaled)
    if k == 0:
        return sign + s
    if len(s) <= k:
        s = "0" * (k + 1 - len(s)) + s
    whole, frac = s[:-k], s[-k:]
    frac = frac.rstrip("0")
    return sign + whole if not frac else sign + whole + "." + frac


def build_lines() -> list[str]:
    d = json.loads(CERT.read_text(encoding="utf-8"))
    cos = d["cosine_rows"]
    weights = canonical_weights(d)
    harmonics = {int(r["n"]): rat(r["lambda"]) for r in d["harmonic_rows"]}
    if len(cos) != 80:
        raise ValueError(f"expected 80 cosine rows, got {len(cos)}")
    if any(w < 0 or w > 1 for w in weights):
        raise ValueError("window weight outside [0,1]")
    if rat(d["second_moment_lambda"]) < 0 or rat(d["window_lambda"]) < 0:
        raise ValueError("negative global multiplier")
    if any(rat(r["lambda"]) < 0 for r in cos) or any(v < 0 for v in harmonics.values()):
        raise ValueError("negative dual multiplier")
    if harmonics and max(harmonics) > 400:
        raise ValueError("harmonic row outside n=1,...,400")

    wl = rat(d["window_lambda"])
    out = [
        "FORMAT weighted-center-coefficients-v1",
        f"T2 {d['second_moment_lambda']}",
        f"WINDOW {d['window_lambda']}",
    ]
    out.extend(f"COS {r['xi']} {r['lambda']}" for r in cos)
    for n, w in enumerate(weights, start=1):
        coef = wl * w - harmonics.get(n, Fraction(0))
        out.append(f"PI {n} {terminating_decimal(coef)}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    a = ap.parse_args()
    text = "\n".join(build_lines()) + "\n"
    if a.output:
        a.output.write_text(text, encoding="utf-8")
        print(f"generated: {a.output}")
    else:
        print(text, end="")
    print("SOURCE frozen JSON")
    print("WINDOW_HARMONICS 400")
    print("TRAILING_ZERO_PLACEHOLDER normalized")
    print("COEFFICIENTS exact Fraction arithmetic")
    print("GENERATED True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
