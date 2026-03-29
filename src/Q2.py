import matplotlib.pyplot as plt
from collections import defaultdict
import re

filename = "free20_output.txt"

# 映射到大类
def map_pos(pos):
    if pos.startswith("n"):
        return "Noun"
    elif pos.startswith("v"):
        return "Verb"
    elif pos.startswith("adj"):
        return "Adjective"
    elif pos.startswith("adv"):
        return "Adverb"
    elif pos.startswith("pro"):
        return "Pronoun"
    elif pos == "co":
        return "Interjection"
    else:
        return "Function/Other"

# 初始化
pos_count_mom = defaultdict(int)
pos_count_child = defaultdict(int)
current_speaker = None

with open(filename, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("From file") or line.startswith("-") or line.startswith("Total number"):
            continue

        m_speaker = re.match(r"Speaker: \*(MOT|CHI):", line)
        if m_speaker:
            current_speaker = m_speaker.group(1)
            continue

        m = re.match(r"(\d+)\s+([^\|]+)\|(.+)", line)
        if m:
            freq = int(m.group(1))
            pos = map_pos(m.group(2))
            if current_speaker == "MOT":
                pos_count_mom[pos] += freq
            elif current_speaker == "CHI":
                pos_count_child[pos] += freq

# 绘图函数
def plot_pos_pie(pos_count, title):
    pos_sorted = sorted(pos_count.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, v in pos_sorted]
    sizes = [v for k, v in pos_sorted]
    
    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title, y=1.05, fontsize=14, pad=10)
    plt.axis('equal')
    plt.show()

plot_pos_pie(pos_count_mom, "Mom POS Distribution")
plot_pos_pie(pos_count_child, "Child POS Distribution")