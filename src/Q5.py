"""
plot_correlation.py
Compare mom vs child language metrics via Pearson correlation heatmap.

需要: pip install matplotlib numpy
用法: python plot_correlation.py child.csv mom.csv
输出: correlation_heatmap.png
"""

import csv
import sys
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


# ── Metrics to include ──────────────────────────────────────────────────────
METRICS = [
    ('Total_Utts',      'Total Utts'),
    ('MLU_Utts',        'MLU (Utts)'),
    ('MLU_Words',       'MLU (Words)'),
    ('MLU_Morphemes',   'MLU (Morphemes)'),
    ('FREQ_types',      'Freq Types'),
    ('FREQ_tokens',     'Freq Tokens'),
    ('FREQ_TTR',        'TTR'),
    ('Verbs_Utt',       'Verbs/Utt'),
    ('%_Nouns',         '% Nouns'),
    ('%_Plurals',       '% Plurals'),
    ('%_Verbs',         '% Verbs'),
    ('%_Aux',           '% Aux'),
    ('%_PAST',          '% Past'),
    ('%_PRESP',         '% PresP'),
    ('%_prep',          '% Prep'),
    ('%_adj',           '% Adj'),
    ('%_adv',           '% Adv'),
    ('%_det',           '% Det'),
    ('%_pro',           '% Pro'),
]


# ── Helpers ─────────────────────────────────────────────────────────────────
def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def safe_float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def pearson(xs, ys):
    """Return (r, n) using only rows where both values are non-None."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 3:
        return None, n
    xs2, ys2 = zip(*pairs)
    mx, my = sum(xs2) / n, sum(ys2) / n
    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx  = math.sqrt(sum((x - mx) ** 2 for x in xs2))
    dy  = math.sqrt(sum((y - my) ** 2 for y in ys2))
    if dx == 0 or dy == 0:
        return None, n
    return num / (dx * dy), n


# ── Main ─────────────────────────────────────────────────────────────────────
def main(child_path='child.csv', mom_path='mom.csv'):
    child_rows = read_csv(child_path)
    mom_rows   = read_csv(mom_path)

    child_by_file = {r['File']: r for r in child_rows}
    mom_by_file   = {r['File']: r for r in mom_rows}
    files = sorted(set(child_by_file) & set(mom_by_file))
    print(f"Matched dyads: {len(files)}")

    keys   = [m[0] for m in METRICS]
    labels = [m[1] for m in METRICS]
    n_met  = len(keys)

    # Build n_met × n_met matrix: row = child metric, col = mom metric
    matrix = np.full((n_met, n_met), np.nan)
    n_mat  = np.zeros((n_met, n_met), dtype=int)

    for i, ck in enumerate(keys):
        c_vals = [safe_float(child_by_file[f].get(ck)) for f in files]
        for j, mk in enumerate(keys):
            m_vals = [safe_float(mom_by_file[f].get(mk)) for f in files]
            r, n   = pearson(c_vals, m_vals)
            if r is not None:
                matrix[i, j] = r
            n_mat[i, j] = n

    # ── Plot ────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 11))

    cmap = plt.get_cmap('RdYlGn')
    im   = ax.imshow(matrix, cmap=cmap, vmin=-1, vmax=1, aspect='auto')

    # Axis ticks
    ax.set_xticks(range(n_met))
    ax.set_yticks(range(n_met))
    ax.set_xticklabels([f'{l}' for l in labels], fontsize=8, rotation=45, ha='right')
    ax.set_yticklabels([f'{l}' for l in labels], fontsize=8)

    # Cell annotations
    for i in range(n_met):
        for j in range(n_met):
            val = matrix[i, j]
            if np.isnan(val):
                txt, color = 'NA', '#aaaaaa'
            else:
                txt   = f'{val:.2f}'
                color = 'white' if abs(val) > 0.6 else '#111111'
            ax.text(j, i, txt, ha='center', va='center',
                    fontsize=7, color=color, fontweight='bold')

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label('Pearson r', fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    ax.set_title(
        f'Mom × Child Language Metrics — Pearson Correlation Matrix\n'
        f'(n = {len(files)} dyads;  rows = child,  cols = mom)',
        fontsize=12, fontweight='bold', pad=14
    )

    plt.tight_layout()
    out = 'correlation_heatmap.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    print(f"Saved → {out}")

    # ── Print top correlations to console ───────────────────────────────────
    print("\nTop 10 cross-role correlations (|r| largest):")
    pairs_list = []
    for i, ck in enumerate(keys):
        for j, mk in enumerate(keys):
            if not np.isnan(matrix[i, j]):
                pairs_list.append((abs(matrix[i, j]), matrix[i, j],
                                   labels[i], labels[j], n_mat[i, j]))
    pairs_list.sort(reverse=True)
    for rank, (_, r, cl, ml, n) in enumerate(pairs_list[:10], 1):
        print(f"  {rank:2d}. Child {cl:15s} × Mom {ml:15s}  r = {r:+.3f}  (n={n})")


if __name__ == '__main__':
    child_path = sys.argv[1] if len(sys.argv) > 1 else 'child.csv'
    mom_path   = sys.argv[2] if len(sys.argv) > 2 else 'mom.csv'
    main(child_path, mom_path)