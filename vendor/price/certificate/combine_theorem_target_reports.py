#!/usr/bin/env python3
"""Combine theorem-target Arb verification chunks for the Erdős 36 certificate.

This combiner is intentionally conservative when reading Arb ball strings:
for a ball printed as ``[m +/- r]`` it uses the decimal upper endpoint ``m+r``
when comparing D-bounds and computing the final margin.
"""
from __future__ import annotations

import csv
import json
import re
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 110

CHUNKS = [
    (Path("arb_0_84_0380554700.csv"), Path("arb_0_84_0380554700.json")),
    (Path("arb_85_88_0380554700.csv"), Path("arb_85_88_0380554700.json")),
    (Path("arb_89_171_0380554700.csv"), Path("arb_89_171_0380554700.json")),
]
PER_BIN_OUT = Path("erdos_0380554700_theorem_target_per_bin.csv")
AGGREGATE_OUT = Path("erdos_0380554700_theorem_target_aggregate.json")

_NUM = r"[+-]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][+-]?\d+)?"
_BALL_RE = re.compile(rf"^\s*\[?\s*({_NUM})\s*(?:\+/-\s*({_NUM}))?\s*\]?\s*$")


def arb_mid_radius(ball: str) -> tuple[Decimal, Decimal]:
    """Return the printed midpoint and radius from a simple Arb ball string."""
    m = _BALL_RE.match(ball)
    if not m:
        raise ValueError(f"cannot parse Arb ball string: {ball!r}")
    mid = Decimal(m.group(1))
    rad = Decimal(m.group(2) or "0")
    if rad < 0:
        raise ValueError(f"negative radius in Arb ball string: {ball!r}")
    return mid, rad


def arb_upper_endpoint_decimal(ball: str) -> Decimal:
    mid, rad = arb_mid_radius(ball)
    return mid + rad


def main() -> None:
    rows: list[dict[str, str]] = []
    reports: list[dict] = []

    for csv_path, json_path in CHUNKS:
        if not csv_path.exists():
            raise SystemExit(f"missing chunk CSV: {csv_path}")
        if not json_path.exists():
            raise SystemExit(f"missing chunk JSON report: {json_path}")
        with csv_path.open(newline="") as f:
            rows.extend(csv.DictReader(f))
        reports.append(json.loads(json_path.read_text()))

    rows.sort(key=lambda r: int(r["bin_index"]))
    expected = list(range(172))
    actual = [int(r["bin_index"]) for r in rows]
    if actual != expected:
        raise SystemExit("per-bin reports do not cover exactly bins 0..171")
    if not all(r["proved"] == "True" for r in rows):
        raise SystemExit("at least one per-bin row is not proved")
    if not all(r.get("proved_all_checked_bins", False) for r in reports):
        raise SystemExit("at least one chunk report did not prove all checked bins")

    targets = {str(r["target"]) for r in reports}
    if targets != {"0.38055470"}:
        raise SystemExit(f"unexpected chunk target(s): {sorted(targets)}")
    target = Decimal("0.38055470")
    target_D = Decimal(1) / target

    # Use the upper endpoint, not merely the displayed midpoint, of each Arb ball.
    worst_report = max(
        reports,
        key=lambda r: arb_upper_endpoint_decimal(r["worst_D_upper_ball"]),
    )
    worst_D_upper_endpoint = arb_upper_endpoint_decimal(worst_report["worst_D_upper_ball"])
    if not worst_D_upper_endpoint < target_D:
        raise SystemExit("combined worst D upper endpoint does not certify the target")

    with PER_BIN_OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    aggregate = {
        "statement": "Arb ball-arithmetic verification at theorem target c > 0.38055470",
        "target": str(target),
        "proved_all_bins": True,
        "bin_ranges_verified": [[0, 84], [85, 88], [89, 171]],
        "row_coverage": "0..171 exactly",
        "worst_bin_index": worst_report["worst_bin_index"],
        "worst_bin": worst_report["worst_bin"],
        "worst_D_upper_ball": worst_report["worst_D_upper_ball"],
        "worst_D_upper_bound_including_reported_radius_decimal": str(worst_D_upper_endpoint),
        "target_D_decimal": str(target_D),
        "D_margin_decimal": str(target_D - worst_D_upper_endpoint),
        "inverse_worst_D_upper_bound_decimal": str(Decimal(1) / worst_D_upper_endpoint),
        "certified_lower_bound_ball_from_worst_chunk": worst_report.get("certified_lower_bound_ball"),
        "total_nodes": sum(int(r["total_nodes"]) for r in reports),
        "total_ambiguous_cells": sum(int(r["total_ambiguous_cells"]) for r in reports),
        "max_speed_roots": max(int(r["max_speed_roots"]) for r in reports),
        "arb_precision_bits": reports[0]["arb_precision_bits"],
        "cell_width": reports[0]["cell_width"],
        "root_pad": reports[0]["root_pad"],
        "samples": reports[0]["samples"],
        "rhs_inflate": reports[0]["rhs_inflate"],
        "chunk_reports": [str(path) for _, path in CHUNKS],
        "chunk_csvs": [str(path) for path, _ in CHUNKS],
        "combiner_note": "For each printed Arb ball [m +/- r], comparisons use m+r.",
    }
    AGGREGATE_OUT.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(aggregate, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
