#!/usr/bin/env python3
"""Aggregate rigorously rounded MPFR chunk bounds for the weighted-Parseval center certificate.

Each chunk log must contain
  chunk: i/N xidx=[lo,hi]
  Dhalf_upper: <decimal>
  CERTIFIED True
where xidx is on the common DGRID=24 lattice for x in [0,2].

The script checks that the supplied chunks form an exact, gap-free, non-overlapping
cover of [0,2], sums the printed upward-rounded decimal bounds exactly as rational
numbers, doubles the half-domain integral, and compares against 1/target exactly.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from pathlib import Path
import re

DGRID = 24
XMAX = 2 << DGRID
CHUNK_RE = re.compile(r"chunk:\s*\d+/\d+\s+xidx=\[(\d+),(\d+)\]")
D_RE = re.compile(r"Dhalf_upper:\s*([0-9]+(?:\.[0-9]+)?)")


def parse_decimal_fraction(s: str) -> Fraction:
    return Fraction(s)


def parse_log(path: Path):
    text = path.read_text(encoding="utf-8", errors="strict")
    if "CERTIFIED True" not in text:
        raise ValueError(f"{path}: missing CERTIFIED True")
    cm = CHUNK_RE.search(text)
    dm = D_RE.search(text)
    if not cm or not dm:
        raise ValueError(f"{path}: missing chunk range or Dhalf_upper")
    lo, hi = map(int, cm.groups())
    if not (0 <= lo < hi <= XMAX):
        raise ValueError(f"{path}: invalid xidx range [{lo},{hi}]")
    return lo, hi, parse_decimal_fraction(dm.group(1)), dm.group(1)


def decimal_string(q: Fraction, digits: int = 90) -> str:
    # Long division, truncating only for display. Logical comparisons below use Fraction.
    sign = "-" if q < 0 else ""
    q = abs(q)
    whole, rem = divmod(q.numerator, q.denominator)
    out = [sign + str(whole), "."]
    for _ in range(digits):
        rem *= 10
        d, rem = divmod(rem, q.denominator)
        out.append(str(d))
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+", type=Path)
    ap.add_argument("--target", default="0.38056068")
    args = ap.parse_args()

    rows = []
    for p in args.logs:
        lo, hi, d, printed = parse_log(p)
        rows.append((lo, hi, d, printed, p))
    rows.sort(key=lambda r: (r[0], r[1]))

    cursor = 0
    for lo, hi, *_ in rows:
        if lo != cursor:
            relation = "gap" if lo > cursor else "overlap"
            raise ValueError(f"coverage {relation}: expected next lo={cursor}, got {lo}")
        cursor = hi
    if cursor != XMAX:
        raise ValueError(f"coverage incomplete: ended at {cursor}, expected {XMAX}")

    dhalf = sum((r[2] for r in rows), Fraction(0))
    dfull = 2 * dhalf
    target = Fraction(args.target)
    target_d = 1 / target
    margin = target_d - dfull

    print(f"chunks: {len(rows)}")
    print(f"coverage_xidx: [0,{XMAX}] exact")
    print(f"Dhalf_upper_sum: {decimal_string(dhalf)}")
    print(f"D_upper: {decimal_string(dfull)}")
    print(f"target: {args.target}")
    print(f"target_D_exact: {decimal_string(target_d)}")
    print(f"margin_D: {decimal_string(margin)}")
    if dfull > 0:
        print(f"implied_bound_from_D: {decimal_string(1/dfull)}")
    ok = margin > 0
    print(f"CERTIFIED {'True' if ok else 'False'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
