#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 80
chunks = [
    (Path('arb_0_84.csv'), Path('arb_0_84.json')),
    (Path('arb_85_88.csv'), Path('arb_85_88.json')),
    (Path('arb_89_171.csv'), Path('arb_89_171.json')),
]
rows = []
reports = []
for csv_path, json_path in chunks:
    with csv_path.open() as f:
        rows.extend(csv.DictReader(f))
    reports.append(json.loads(json_path.read_text()))
rows.sort(key=lambda r: int(r['bin_index']))
if [int(r['bin_index']) for r in rows] != list(range(172)):
    raise SystemExit('per-bin reports do not cover exactly bins 0..171')
if not all(r['proved'] == 'True' for r in rows):
    raise SystemExit('at least one per-bin row is not proved')
if not all(r.get('proved_all_checked_bins', False) for r in reports):
    raise SystemExit('at least one chunk report did not prove all checked bins')
with Path('erdos_0380554275_arb_per_bin_report.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
worst_report = max(reports, key=lambda r: Decimal(r['worst_D_upper_ball'].split()[0].strip('[')))
# Decimal copy of the outward upper endpoint shown in worst_report.
D_worst = Decimal(worst_report['worst_D_upper_ball'].split()[0].strip('['))
T = Decimal('0.38055470')
T_package = Decimal('0.380554275')
aggregate = {
    'statement': 'Arb ball-arithmetic verification for the improved Erdős problem 36 certificate',
    'proved_all_bins': True,
    'verified_target': str(T_package),
    'recommended_theorem_target': str(T),
    'recommended_statement': 'c > 0.38055470',
    'target_D_for_recommended_statement': str(Decimal(1) / T),
    'D_margin_for_recommended_statement': str(Decimal(1) / T - D_worst),
    'worst_bin_index': worst_report['worst_bin_index'],
    'worst_bin': worst_report['worst_bin'],
    'worst_D_upper_ball': worst_report['worst_D_upper_ball'],
    'inverse_worst_D_decimal': str(Decimal(1) / D_worst),
    'certified_lower_bound_ball': worst_report['certified_lower_bound_ball'],
    'total_nodes': sum(r['total_nodes'] for r in reports),
    'total_ambiguous_cells': sum(r['total_ambiguous_cells'] for r in reports),
    'max_speed_roots': max(r['max_speed_roots'] for r in reports),
    'arb_precision_bits': reports[0]['arb_precision_bits'],
    'cell_width': reports[0]['cell_width'],
    'root_pad': reports[0]['root_pad'],
    'samples': reports[0]['samples'],
    'rhs_inflate': reports[0]['rhs_inflate'],
    'bin_ranges_verified': [[0, 84], [85, 88], [89, 171]],
    'note': 'The verifier conservatively closes one tiny decimal endpoint gap before recomputing RHS bounds.',
}
Path('erdos_0380554700_arb_aggregate_report.json').write_text(json.dumps(aggregate, indent=2, ensure_ascii=False))
print(json.dumps(aggregate, indent=2, ensure_ascii=False))
