"""
计算 kwal interaction.txt 的互动性指标
Usage: python interactiveness.py interaction.txt
"""

import re
import sys
from collections import defaultdict

def parse_kwal(path):
    """
    解析kwal输出，返回每个文件的话语序列。
    每条: { 'file': str, 'speaker': 'MOT'|'CHI', 'line': int, 'text': str }
    """
    utterances = defaultdict(list)  # { filename: [{'speaker','line','text'}, ...] }
    current_file = None

    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()

            m = re.match(r'From file <(.+?)>', line)
            if m:
                current_file = m.group(1).replace('.cha','')
                continue

            # 行号标记: *** File "amy.cha": line 7.
            m = re.match(r'\*\*\* File ".+?": line (\d+)\.', line)
            if m:
                current_line = int(m.group(1))
                continue

            # 话语行: *MOT: ... 或 *CHI: ...
            m = re.match(r'\*(MOT|CHI):\t(.+)', line)
            if m and current_file:
                utterances[current_file].append({
                    'speaker': m.group(1),
                    'line':    current_line,
                    'text':    m.group(2).strip()
                })

    return utterances


def compute_interactiveness(utterances):
    """
    计算每个文件的4个互动性指标。
    """
    results = {}

    for fname, utts in utterances.items():
        if len(utts) < 2:
            continue

        n = len(utts)
        mot_count = sum(1 for u in utts if u['speaker'] == 'MOT')
        chi_count = sum(1 for u in utts if u['speaker'] == 'CHI')

        # ── 1. 话轮转换次数 & 密度
        switches = sum(
            1 for i in range(1, n)
            if utts[i]['speaker'] != utts[i-1]['speaker']
        )
        switch_density = switches / (n - 1) if n > 1 else 0  # 0~1，越高越均衡

        # ── 2. MOT回应率：CHI后面紧跟MOT的比例
        chi_followed_by_mot = sum(
            1 for i in range(1, n)
            if utts[i-1]['speaker'] == 'CHI' and utts[i]['speaker'] == 'MOT'
        )
        mot_response_rate = chi_followed_by_mot / chi_count if chi_count > 0 else 0

        # ── 3. CHI回应率：MOT后面紧跟CHI的比例
        mot_followed_by_chi = sum(
            1 for i in range(1, n)
            if utts[i-1]['speaker'] == 'MOT' and utts[i]['speaker'] == 'CHI'
        )
        chi_response_rate = mot_followed_by_chi / mot_count if mot_count > 0 else 0

        # ── 4. MOT独语连续率：MOT连续≥2句的话语占MOT总话语比例
        mot_monologue_utts = 0
        i = 0
        while i < n:
            if utts[i]['speaker'] == 'MOT':
                run = 0
                while i < n and utts[i]['speaker'] == 'MOT':
                    run += 1
                    i += 1
                if run >= 2:
                    mot_monologue_utts += run
            else:
                i += 1
        mot_monologue_ratio = mot_monologue_utts / mot_count if mot_count > 0 else 0

        # ── 综合互动性得分（加权平均，可调整权重）
        # switch_density 和 chi_response_rate 越高越好
        # mot_monologue_ratio 越低越好（取反）
        composite = (
            0.35 * switch_density +
            0.35 * chi_response_rate +
            0.30 * (1 - mot_monologue_ratio)
        )

        results[fname] = {
            'n_utts':              n,
            'mot_utts':            mot_count,
            'chi_utts':            chi_count,
            'switches':            switches,
            'switch_density':      round(switch_density, 3),
            'mot_response_rate':   round(mot_response_rate, 3),
            'chi_response_rate':   round(chi_response_rate, 3),
            'mot_monologue_ratio': round(mot_monologue_ratio, 3),
            'composite_score':     round(composite, 3),
        }

    return results


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "interaction.txt"
    utterances = parse_kwal(path)
    results    = compute_interactiveness(utterances)

    # ── 排序输出
    ranked = sorted(results.items(), key=lambda x: -x[1]['composite_score'])

    print("\n" + "="*90)
    print("  INTERACTIVENESS METRICS  (from kwal output)")
    print("="*90)
    print(f"{'Dyad':<10} {'N_utts':>7} {'MOT':>5} {'CHI':>5} "
          f"{'Switch_D':>10} {'MOT_resp':>10} {'CHI_resp':>10} "
          f"{'MOT_mono':>10} {'Composite':>11}")
    print("-"*90)
    for fname, r in ranked:
        print(f"{fname:<10} {r['n_utts']:>7} {r['mot_utts']:>5} {r['chi_utts']:>5} "
              f"{r['switch_density']:>10.3f} {r['mot_response_rate']:>10.3f} "
              f"{r['chi_response_rate']:>10.3f} {r['mot_monologue_ratio']:>10.3f} "
              f"{r['composite_score']:>11.3f}")

    print("\n  Column guide:")
    print("  Switch_D   = turn-switch rate (switches / N-1); higher = more balanced")
    print("  MOT_resp   = % of CHI turns immediately followed by MOT")
    print("  CHI_resp   = % of MOT turns immediately followed by CHI  ← key measure")
    print("  MOT_mono   = % of MOT turns that are consecutive ≥2 (monologue tendency)")
    print("  Composite  = 0.35*Switch_D + 0.35*CHI_resp + 0.30*(1-MOT_mono)")

    print(f"\n  ★ Most interactive dyad:  {ranked[0][0]}  (score={ranked[0][1]['composite_score']})")
    print(f"  ★ Least interactive dyad: {ranked[-1][0]}  (score={ranked[-1][1]['composite_score']})")

    print("\nTip: python interactiveness.py interaction.txt > interact_results.txt")


if __name__ == "__main__":
    main()