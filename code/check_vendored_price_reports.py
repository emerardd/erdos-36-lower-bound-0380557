#!/usr/bin/env python3
"""Check the vendored Price Arb reports against the stronger target 0.380557.

This does not replace rerunning Price's Arb verifier.  It checks, using Decimal
arithmetic and the full Arb ball strings (midpoint + radius), that the already
published certified upper bounds for every noncentral bin imply the stronger
theorem target used in this repository.
"""
from __future__ import annotations

import csv
import re
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 100
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "vendor" / "price" / "certificate"
TARGET = Decimal("0.380557")
TARGET_D = Decimal(1) / TARGET
BALL = re.compile(r"^\[\s*([^ ]+)\s*\+/-\s*([^\]]+)\s*\]$")


def ball_upper(s: str) -> Decimal:
    m = BALL.match(s.strip())
    if not m:
        raise ValueError(f"unrecognized Arb ball: {s!r}")
    return Decimal(m.group(1)) + Decimal(m.group(2))


rows = []
for fn in [
    "arb_0_84_0380554700.csv",
    "arb_85_88_0380554700.csv",
    "arb_89_171_0380554700.csv",
]:
    with (P / fn).open(newline="") as f:
        rows.extend(csv.DictReader(f))

noncentral = [r for r in rows if int(r["bin_index"]) not in (85, 86)]
indices = [int(r["bin_index"]) for r in noncentral]
expected = list(range(85)) + list(range(87, 172))
assert indices == expected, (indices[:5], indices[-5:], len(indices))
assert all(r["proved"].strip().lower() == "true" for r in noncentral)

uppers = [(ball_upper(r["D_upper_ball"]), int(r["bin_index"]), r) for r in noncentral]
worst, worst_i, worst_row = max(uppers, key=lambda x: x[0])
margin = TARGET_D - worst
assert margin > 0, (worst, TARGET_D)

print("VENDORED PRICE REPORT CHECK")
print(f"target = {TARGET}")
print(f"target_D = {TARGET_D}")
print(f"noncentral bins checked = {len(noncentral)} / 170")
print(f"worst bin = {worst_i} [{worst_row['lo']}, {worst_row['hi']}]")
print(f"worst certified D upper = {worst}")
print(f"D-side margin = {margin}")
print("PRICE NONCENTRAL REPORTS CERTIFY TARGET True")
