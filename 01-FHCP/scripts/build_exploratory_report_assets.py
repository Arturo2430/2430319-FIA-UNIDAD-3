"""Build report assets from the closed, independently audited exploratory cuts."""

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'experiments/analysis/closed-explorations-20261117'
OUT = ROOT / 'docs/latex'
FAMILIES = ['ga', 'sa', 'as', 'abc', 'de', 'pso']


def read(path):
    return json.loads(path.read_text())


def number(value):
    return f'{int(value):,}'.replace(',', r'\,')


def save(name, text):
    (OUT / 'tables' / name).write_text(text + '\n', encoding='utf-8')


def table(headers, rows, widths):
    return ('\\begin{tabularx}{\\linewidth}{' + widths + '}\n\\toprule\n'
            + ' & '.join(headers) + ' \\\\ \\midrule\n'
            + '\n'.join(' & '.join(map(str, row)) + ' \\\\' for row in rows)
            + '\n\\bottomrule\\end{tabularx}')


def build_cumulative(team_graphs, guided, repaired):
    """Show certified graph coverage, keeping each observation's protocol visible."""
    distributed = list(csv.DictReader((ROOT / 'experiments/results/team-evaluation-consolidated-20261117/attempts.csv').open()))
    for row in distributed:
        row['certified_success'] = row['certified_success'] == 'True'
    phases = [('Distribuida 60 s', distributed), ('Guiada 30 s', guided), ('Reparación v4 30 s', repaired)]
    observed = {row['instance'] for _, rows in phases for row in rows}
    certified = sorted({row['instance'] for _, rows in phases for row in rows if row['certified_success']}, key=lambda g: int(g[5:]))
    assert len(certified) == 22 and len(observed) == 149
    sizes = {row['instance']: row['vertices'] for row in team_graphs}
    cumulative_rows, matrix, labels, attempts_per_cell = [], [], [], []
    cell_rows = []
    for graph in certified:
        label, rows = next((label, rows) for label, rows in phases
                           if any(r['instance'] == graph and r['certified_success'] for r in rows))
        selected = [r for r in rows if r['instance'] == graph]
        successes = sum(r['certified_success'] for r in selected)
        cumulative_rows.append([graph[5:], sizes[graph], label, f'{successes}/{len(selected)}'])
        numerator, denominator = [], []
        for family in FAMILIES:
            cells = [r for r in selected if r['algorithm'] == family]
            wins = sum(r['certified_success'] for r in cells)
            assert cells
            numerator.append(wins); denominator.append(len(cells))
            cell_rows.append({'instance': graph, 'protocol': label, 'algorithm': family,
                              'successes': wins, 'attempted': len(cells)})
        matrix.append(numerator); attempts_per_cell.append(denominator)
        labels.append(f'{graph} · ' + {'Distribuida 60 s': 'D', 'Guiada 30 s': 'G', 'Reparación v4 30 s': 'R'}[label])
    save('exploratory-cumulative-solved.tex', table(
        ['Grafo', 'Vértices', 'Protocolo del certificado', 'Éxitos/intentos'], cumulative_rows, 'lrYr'))
    with (OUT / 'tables/exploratory-cumulative-cells.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(cell_rows[0])); writer.writeheader(); writer.writerows(cell_rows)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(figsize=(8.6, 7.3), layout='constrained')
    values = np.asarray(matrix) / np.asarray(attempts_per_cell)
    im = ax.imshow(values, cmap='YlGn', vmin=0, vmax=1, aspect='auto')
    ax.set_xticks(range(6), [family.upper() for family in FAMILIES])
    ax.set_yticks(range(len(labels)), labels, fontsize=9)
    ax.set_title('22 grafos certificados · cobertura acumulada')
    ax.set_xlabel('D: distribuida 60 s · G: guiada 30 s · R: reparación v4 30 s', fontsize=9)
    for (i, j), value in np.ndenumerate(values):
        ax.text(j, i, f'{matrix[i][j]}/{attempts_per_cell[i][j]}', ha='center', va='center',
                color='white' if value > .6 else '#25343B', fontsize=9)
    fig.colorbar(im, ax=ax, label='Éxitos / intentos en el protocolo indicado', shrink=.8)
    fig.savefig(OUT / 'figures/exploratory-cumulative-heatmap.pdf', metadata={'CreationDate': None}); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9.8, 3.6), layout='constrained')
    bottoms = np.zeros(6, dtype=int); known = {family: set() for family in FAMILIES}
    coverage = []
    for (label, rows), color in zip(phases, ['#367B70', '#D8AD48', '#8C5363']):
        added = []
        for family in FAMILIES:
            found = {r['instance'] for r in rows if r['algorithm'] == family and r['certified_success']}
            added.append(len(found - known[family])); known[family].update(found)
        ax.bar([f.upper() for f in FAMILIES], added, bottom=bottoms, label=label, color=color)
        coverage.append({'protocol': label, **dict(zip(FAMILIES, added))})
        bottoms += added
    assert max(bottoms) <= len(certified)
    for i, n in enumerate(bottoms): ax.text(i, n + .35, str(n), ha='center')
    ax.set(ylabel='Grafos distintos con ciclo certificado', title='Cobertura acumulada por familia · 22 grafos en la unión', ylim=(0, 26))
    ax.legend(frameon=False, loc='upper right', fontsize=8); ax.grid(axis='y', alpha=.15); ax.set_axisbelow(True)
    fig.savefig(OUT / 'figures/exploratory-cumulative-coverage.pdf', metadata={'CreationDate': None}); plt.close(fig)
    (OUT / 'tables/exploratory-cumulative-coverage.json').write_text(json.dumps({
        'unique_observed_graphs': len(observed), 'unique_certified_graphs': len(certified),
        'certified_graph_ids': certified, 'new_graphs_by_family_by_protocol': coverage,
        'unique_certified_by_family': {family: len(known[family]) for family in FAMILIES},
        'heatmap_rule': 'First protocol with a certified success per graph; numerator and denominator within that protocol only',
    }, indent=2) + '\n')
    cumulative_costs = []
    for graph in sorted(observed, key=lambda g: int(g[5:])):
        costs = [int(r['best_cost']) for _, rows in phases for r in rows
                 if r['instance'] == graph and r['best_cost'] not in ('', None)]
        cumulative_costs.append({'instance': graph, 'vertices': int(sizes[graph]),
                                 'best_cost': min(costs) if costs else None,
                                 'certified_success': graph in certified})
    assert sum(row['certified_success'] for row in cumulative_costs) == 22
    with (OUT / 'tables/exploratory-cumulative-costs.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(cumulative_costs[0])); writer.writeheader(); writer.writerows(cumulative_costs)
    fig, ax = plt.subplots(figsize=(8.6, 3.7), layout='constrained')
    for success, color, label in [(False, '#52655D', 'Sin ciclo certificado'), (True, '#367B70', 'Con ciclo certificado (22)')]:
        points = [r for r in cumulative_costs if r['certified_success'] == success and r['best_cost'] is not None]
        ax.scatter([r['vertices'] for r in points], [r['best_cost'] / r['vertices'] for r in points],
                   color=color, label=label, s=27, alpha=.8)
    ax.set(xscale='log', xlabel='Número de vértices (escala logarítmica)', ylabel='Menor costo / número de vértices',
           title='Mejor costo observado · todas las entregas')
    ax.legend(frameon=False, fontsize=9); ax.grid(alpha=.15)
    fig.savefig(OUT / 'figures/exploratory-cumulative-cost.pdf', metadata={'CreationDate': None}); plt.close(fig)


def build():
    closure = read(DATA / 'closure.json')
    assert closure['status'] == 'closed_at_delivered_cut' and not closure['resume_planned']
    repair = read(DATA / 'repair-v4/summary.json')
    prior = read(DATA / 'prior-guided/summary.json')
    rows = read(DATA / 'repair-v4/attempts.json')
    old_rows = read(DATA / 'prior-guided/attempts.json')
    plan = read(DATA / 'repair-v4/plan.json')
    team = read(ROOT / 'experiments/results/team-evaluation-consolidated-20261117/totals.json')
    team_graphs = list(csv.DictReader((ROOT / 'experiments/results/team-evaluation-consolidated-20261117/by-graph.csv').open()))
    selection = list(csv.DictReader((DATA / 'repair-v4/selection.csv').open()))
    assert len(rows) == repair['attempted'] == 2976
    assert len({(r['instance'], r['algorithm'], r['seed']) for r in rows}) == len(rows)
    assert sum(r['certified_success'] for r in rows) == repair['successes'] == 11
    assert sum(r['status'] == 'error' for r in rows) == repair['errors'] == 4
    count = Counter(r['instance'] for r in rows)
    complete = {name for name, n in count.items() if n == 60}
    partial = {name for name, n in count.items() if 0 < n < 60}
    balanced = [r for r in rows if r['instance'] in complete]
    solved_team = {r['instance'] for r in team_graphs if int(r['solved_graphs'])}
    solved_all = solved_team | set(prior['solved_graph_ids']) | set(repair['solved_graph_ids'])
    build_cumulative(team_graphs, old_rows, rows)
    phases = [
        ['M6: evaluación y escala', '900', '0', '0'],
        ['Evaluación distribuida', number(team['attempted']), number(team['successes']), team['solved_graphs']],
        ['Exploración guiada', prior['attempted'], prior['successes'], prior['distinct_solved_graphs']],
        ['Exploración con reparación v4', number(repair['attempted']), repair['successes'], repair['distinct_solved_graphs']],
    ]
    save('exploratory-stages.tex', table(['Etapa', 'Intentos', 'Éxitos', 'Grafos HC'], phases, 'Yrrr'))
    session_seconds = sum(read(p)['session_seconds'] for p in (DATA / 'repair-v4/sessions').glob('*.json'))
    metrics = {
        'RepairAttempts': number(len(rows)), 'RepairSuccesses': repair['successes'],
        'RepairErrors': repair['errors'], 'RepairExhausted': number(sum(r['status'] == 'exhausted' for r in rows)),
        'RepairSolved': repair['distinct_solved_graphs'], 'RepairComplete': len(complete),
        'RepairPartial': len(partial), 'RepairStarted': len(count),
        'RepairUnstarted': len(selection) - len(count), 'RepairOmitted': repair['planned'] - len(rows),
        'RepairCoverage': f"{100 * len(rows) / repair['planned']:.2f}",
        'RepairBalancedDenominator': len(complete) * 10,
        'RepairSessionHours': f'{session_seconds / 3600:.2f}',
        'UnionCertifiedGraphs': len(solved_all), 'PriorAttempts': prior['attempted'],
        'PriorErrors': prior['errors'], 'PriorSuccesses': prior['successes'],
    }
    save('exploratory-metrics.tex', '\n'.join('\\newcommand{\\' + k + '}{' + str(v) + '}' for k, v in metrics.items()))
    family_rows = []
    rates = []
    for family in FAMILIES:
        selected = [r for r in rows if r['algorithm'] == family]
        full = [r for r in balanced if r['algorithm'] == family]
        assert len(full) == len(complete) * 10
        wins = sum(r['certified_success'] for r in selected)
        certified = {r['instance'] for r in selected if r['certified_success']}
        rate = 100 * sum(r['certified_success'] for r in full) / len(full)
        rates.append(rate)
        durations = [r['process_seconds'] for r in full if r['process_seconds'] is not None]
        family_rows.append([family.upper(), len(selected), wins,
                            sum(r['status'] == 'error' for r in selected),
                            len(certified), f'{rate:.2f}', f'{np.median(durations):.2f}'])
    save('exploratory-algorithms.tex', table(
        ['Familia', 'Intentos', 'Éxitos', 'Incid.', 'HC', 'Tasa bal. (\\%)', 'Mediana (s)'], family_rows, 'Yrrrrrr'))
    cert_rows = []
    for label, attempts in [('Guiada', old_rows), ('Reparación v4', rows)]:
        names = sorted({r['instance'] for r in attempts if r['certified_success']}, key=lambda n: int(n[5:]))
        for name in names:
            wins = Counter(r['algorithm'].upper() for r in attempts if r['instance'] == name and r['certified_success'])
            cert_rows.append([name[5:], label, ', '.join(f'{a}: {n}' for a, n in sorted(wins.items()))])
    save('exploratory-solved.tex', table(['Grafo', 'Exploración', 'Éxitos por familia'], cert_rows, 'lYY'))
    columns = 'lrrrrr'
    text = ('\\small\\begin{longtable}{' + columns + '}\n'
            '\\caption{Cierre de la selección v4: costo previo y final, intentos, éxitos e incidencias. El guion indica ausencia de intento.}\\label{tab:repairall}\\\\\n'
            '\\toprule Grafo & Costo previo & Costo final & Intentos/60 & Éxitos & Incid. \\\\ \\midrule\\endfirsthead\n'
            '\\toprule Grafo & Costo previo & Costo final & Intentos/60 & Éxitos & Incid. \\\\ \\midrule\\endhead\n'
            '\\midrule\\multicolumn{6}{r}{Continúa en la página siguiente}\\endfoot\\bottomrule\\endlastfoot\n')
    for entry in selection:
        selected = [r for r in rows if r['instance'] == entry['instance']]
        costs = [r['best_cost'] for r in selected if r['best_cost'] is not None]
        text += ' & '.join(map(str, [entry['instance'][5:], entry['baseline_best_cost'], min(costs) if costs else '--',
                                     f'{len(selected)}/60', sum(r['certified_success'] for r in selected),
                                     sum(r['status'] == 'error' for r in selected)])) + ' \\\\\n'
    save('exploratory-all-graphs.tex', text + '\\end{longtable}')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axs = plt.subplots(1, 2, figsize=(10.3, 3.8), layout='constrained')
    bars = axs[0].bar([f.upper() for f in FAMILIES], rates, color='#367B70')
    axs[0].set(ylabel='Éxitos certificados / intentos (%)', title='Éxito con cobertura completa', ylim=(0, max(rates) * 1.3))
    for bar, value in zip(bars, rates):
        axs[0].text(bar.get_x() + bar.get_width() / 2, value + .025, f'{value:.2f}', ha='center', fontsize=9)
    stats = []
    size = {e['id']: e['dimension'] for e in plan['instances']}
    for field, ax in [('process_seconds', axs[1])]:
        values = [[r[field] for r in balanced if r['algorithm'] == f and r[field] is not None] for f in FAMILIES]
        ax.boxplot(values, tick_labels=[f.upper() for f in FAMILIES], whis=1.5, flierprops={'markersize': 2})
        ax.set(ylabel='Tiempo de proceso (s)', title='Tiempos: todos los intentos')
    for ax in axs:
        ax.grid(axis='y', alpha=.17)
        ax.set_axisbelow(True)
    fig.savefig(OUT / 'figures/exploratory-performance.pdf', metadata={'CreationDate': None})
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8.6, 3.4), layout='constrained')
    values = [[r['best_cost'] / size[r['instance']] for r in balanced if r['algorithm'] == f and r['best_cost'] is not None] for f in FAMILIES]
    ax.boxplot(values, tick_labels=[f.upper() for f in FAMILIES], whis=1.5, flierprops={'markersize': 2})
    ax.set(ylabel='Costo final / número de vértices', title='Reparación v4: costo con cobertura completa')
    ax.grid(axis='y', alpha=.17)
    fig.savefig(OUT / 'figures/exploratory-cost-boxplots.pdf', metadata={'CreationDate': None})
    plt.close(fig)
    for field in ('process_seconds', 'best_cost'):
        for family in FAMILIES:
            values = [r[field] / (size[r['instance']] if field == 'best_cost' else 1)
                      for r in balanced if r['algorithm'] == family and r[field] is not None]
            q1, median, q3 = np.percentile(values, [25, 50, 75])
            iqr = q3 - q1
            inner = [v for v in values if q1 - 1.5 * iqr <= v <= q3 + 1.5 * iqr]
            stats.append({'field': field, 'algorithm': family, 'n': len(values), 'q1': q1,
                          'median': median, 'q3': q3, 'lower_whisker': min(inner), 'upper_whisker': max(inner),
                          'outliers': len(values) - len(inner)})
    with (OUT / 'tables/exploratory-boxplot-statistics.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(stats[0]))
        writer.writeheader()
        writer.writerows(stats)
    inputs = [p for p in DATA.rglob('*') if p.is_file()]
    manifest = read(OUT / 'asset-manifest.json')
    manifest['inputs'].update({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    manifest['inputs'][str(Path(__file__).relative_to(ROOT))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest['outputs'].update({str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for directory in ('tables', 'figures') for p in (OUT / directory).glob('exploratory-*')})
    (OUT / 'asset-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Closed exploratory report:', metrics)


if __name__ == '__main__':
    build()
