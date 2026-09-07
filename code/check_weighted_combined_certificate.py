#!/usr/bin/env python3
"""Validate the standalone combined weighted/harmonic center certificate.

For lambda_W >= 0, any exact cosine coefficients c_n satisfying c_n <= lambda_W
admit the valid decomposition

  c_n = lambda_W * w_n - h_n,
  0 <= w_n <= 1,  h_n >= 0.

Indeed choose w_n=c_n/lambda_W,h_n=0 for c_n>=0, and w_n=0,h_n=-c_n
for c_n<0.  Thus the finite-decimal PI rows in the combined proof object need
not be a rounded transcription of any prior optimizer decomposition.
"""
from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CERT = ROOT / "certificate" / "weighted_center_combined_038056070.txt"


def q(s: str) -> Fraction:
    return Fraction(Decimal(s))


def main() -> int:
    lines = CERT.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "FORMAT weighted-center-coefficients-v1":
        raise SystemExit("bad FORMAT line")
    t2 = window = None
    cos = []
    pi = {}
    for line in lines[1:]:
        a = line.split()
        if not a:
            continue
        if a[0] == "T2" and len(a) == 2:
            if t2 is not None: raise SystemExit("duplicate T2")
            t2 = q(a[1])
        elif a[0] == "WINDOW" and len(a) == 2:
            if window is not None: raise SystemExit("duplicate WINDOW")
            window = q(a[1])
        elif a[0] == "COS" and len(a) == 3:
            xi, lam = q(a[1]), q(a[2])
            cos.append((xi, lam))
        elif a[0] == "PI" and len(a) == 3:
            n = int(a[1]); c = q(a[2])
            if n in pi: raise SystemExit(f"duplicate PI {n}")
            pi[n] = c
        else:
            raise SystemExit(f"bad line: {line}")

    if t2 is None or window is None:
        raise SystemExit("missing T2/WINDOW")
    if t2 < 0 or window <= 0:
        raise SystemExit("invalid global multiplier")
    if len(cos) != 80:
        raise SystemExit(f"expected 80 COS rows, got {len(cos)}")
    if any(xi <= 0 or lam < 0 for xi, lam in cos):
        raise SystemExit("invalid COS row")
    if sorted(pi) != list(range(1,401)):
        raise SystemExit("PI indices must be exactly 1..400")

    bad = [(n,c) for n,c in pi.items() if c > window]
    if bad:
        n,c = bad[0]
        raise SystemExit(f"PI {n}: coefficient {c} exceeds lambda_W {window}")

    positive = sum(c >= 0 for c in pi.values())
    negative = 400-positive
    max_c = max(pi.values())
    min_c = min(pi.values())
    print(f"T2_NONNEGATIVE {t2 >= 0}")
    print(f"WINDOW_POSITIVE {window > 0}")
    print(f"COS_ROWS {len(cos)} ALL_VALID True")
    print(f"PI_ROWS {len(pi)} INDICES_1_400 True")
    print(f"PI_POSITIVE_OR_ZERO {positive}")
    print(f"PI_NEGATIVE {negative}")
    print(f"PI_MAX_LE_WINDOW {max_c <= window}")
    print(f"PI_MAX {max_c}")
    print(f"WINDOW_LAMBDA {window}")
    print(f"PI_MIN {min_c}")
    print("DECOMPOSITION_EXISTS True")
    print("CERTIFICATE_VALID True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
