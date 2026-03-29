import xml.etree.ElementTree as ET

# ── 读取数据 ──────────────────────────────────────────────
with open('child.eval.xls', 'r', encoding='utf-8') as f:
    content = f.read()

tree = ET.fromstring(content)
ns_map = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
ws = tree.findall('.//ss:Worksheet', ns_map)[0]
rows = ws.findall('.//ss:Row', ns_map)

all_rows = []
for row in rows:
    cells = row.findall('ss:Cell', ns_map)
    vals = [c.find('ss:Data', ns_map).text if c.find('ss:Data', ns_map) is not None else '' for c in cells]
    all_rows.append(vals)

headers = all_rows[0]

# ── 列索引 ────────────────────────────────────────────────
idx = {col: headers.index(col) for col in
       ['File', 'Total_Utts', 'FREQ_TTR', 'MLU_Words', 'FREQ_tokens']}

METRICS = {
    'FREQ_TTR'    : 'Lexical Diversity',
    'MLU_Words'   : 'Utterance Length',
    'FREQ_tokens' : 'Total Word Tokens',
}

# ── 过滤：Total_Utts > 10 ─────────────────────────────────
data = []
for row in all_rows[1:]:
    if len(row) <= max(idx.values()):
        continue
    child = row[idx['File']].replace('.cha', '')
    try:
        total_utts = int(row[idx['Total_Utts']])
    except ValueError:
        continue
    if total_utts <= 10:
        continue
    entry = {'child': child, 'Total_Utts': total_utts}
    valid = True
    for col in METRICS:
        try:
            entry[col] = float(row[idx[col]])
        except ValueError:
            valid = False
            break
    if valid:
        data.append(entry)

# ── 输出结果 ──────────────────────────────────────────────
print(f"符合条件的儿童数（Total_Utts > 10）: {len(data)}\n")
print(f"{'Child':<16} {'Total_Utts':>11} {'FREQ_TTR':>10} {'MLU_Words':>10} {'FREQ_tokens':>12}")
print('─' * 64)
for d in sorted(data, key=lambda x: x['child']):
    print(f"{d['child']:<16} {d['Total_Utts']:>11} {d['FREQ_TTR']:>10.3f} {d['MLU_Words']:>10.3f} {d['FREQ_tokens']:>12.0f}")

print()
for col, label in METRICS.items():
    best = max(data, key=lambda x: x[col])
    print(f" {label} ({col}): {best['child']}  →  {best[col]:.3f}  (Total_Utts = {best['Total_Utts']})")