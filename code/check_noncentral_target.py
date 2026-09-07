#!/usr/bin/env python3
"""Check that Price's 170 noncentral Arb reports clear a stronger target.

The vendored CSV stores Arb balls as `[mid +/- rad]`.  For each noncentral bin
we use `mid + rad` as a rigorous decimal upper bound for D, skip bins 85 and 86
(which are replaced by the weighted-Parseval center certificate), and require
D_upper < 1/target.
"""
from __future__ import annotations

import argparse, csv, re
from fractions import Fraction
from pathlib import Path

BALL_RE = re.compile(r"^\[\s*([0-9eE+\-.]+)\s*\+/-\s*([0-9eE+\-.]+)\s*\]$")


def frac_decimal(s: str) -> Fraction:
    from decimal import Decimal
    return Fraction(Decimal(s))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--target", default="0.38056068")
    ap.add_argument("--skip", default="85,86")
    a = ap.parse_args()
    skip = {int(x) for x in a.skip.split(",") if x}
    target_d = 1 / Fraction(a.target)

    worst = None
    count = 0
    with a.csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            idx = int(row["bin_index"])
            if idx in skip:
                continue
            if row.get("proved") != "True":
                raise SystemExit(f"bin {idx}: proved != True")
            m = BALL_RE.match(row["D_upper_ball"].strip())
            if not m:
                raise SystemExit(f"bin {idx}: cannot parse Arb ball {row['D_upper_ball']!r}")
            mid, rad = map(frac_decimal, m.groups())
            upper = mid + rad
            if upper >= target_d:
                raise SystemExit(f"bin {idx}: fails target; D_upper >= 1/target")
            count += 1
            if worst is None or upper > worst[0]:
                worst = (upper, idx, row["lo"], row["hi"])

    if count != 170:
        raise SystemExit(f"expected 170 noncentral bins, checked {count}")
    assert worst is not None
    upper, idx, lo, hi = worst
    margin = target_d - upper
    print(f"checked_noncentral_bins: {count}")
    print(f"worst_bin: {idx} [{lo},{hi}]")
    print(f"worst_D_upper_float: {float(upper):.17g}")
    print(f"target_D: {float(target_d):.17g}")
    print(f"margin_D_float: {float(margin):.17g}")
    print("CERTIFIED True")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
