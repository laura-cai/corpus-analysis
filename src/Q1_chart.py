import matplotlib.pyplot as plt
from collections import defaultdict

# 数据
mot_data = [
    ("the", "det:art", 414),
    ("be&3S", "cop", 383),
    ("you", "pro:per", 352),
    ("it", "pro:per", 238),
    ("a", "det:art", 202),
    ("put&ZERO", "v", 176),
    ("in", "prep", 160),
    ("that", "pro:dem", 159),
    ("to", "inf", 155),
    ("can", "mod", 153)
]

chi_data = [
    ("ball", "n", 82),
    ("no", "co", 44),
    ("ah", "co", 33),
    ("yeah", "co", 28),
    ("chair", "n", 23),
    ("oh", "co", 20),
    ("okay", "co", 20),
    ("where", "pro:int", 19),
    ("uhoh", "co", 17),
    ("O", "n:prop", 16)
]

# 颜色表，每个词性固定颜色
pos_colors = {
    "det:art": "#1f77b4",
    "cop": "#ff7f0e",
    "pro:per": "#2ca02c",
    "v": "#d62728",
    "prep": "#9467bd",
    "pro:dem": "#8c564b",
    "inf": "#e377c2",
    "mod": "#7f7f7f",
    "n": "#17becf",
    "co": "#bcbd22",
    "pro:int": "#ff9896",
    "n:prop": "#c49c94"
}

def group_by_pos(data):
    pos_groups = defaultdict(list)
    for word, pos, freq in data:
        pos_groups[pos].append((word, freq))
    return pos_groups

def plot_grouped_pie(data, title):
    pos_groups = group_by_pos(data)
    
    # 为了饼图顺序，同词性连续
    ordered_words = []
    ordered_colors = []
    ordered_labels = []
    
    for pos, items in pos_groups.items():
        for word, freq in items:
            ordered_words.append(freq)
            ordered_colors.append(pos_colors.get(pos, "#333333"))
            ordered_labels.append(f"{word} ({pos})")
    
    plt.figure(figsize=(6,6))
    plt.pie(ordered_words, labels=ordered_labels, colors=ordered_colors, autopct='%1.1f%%', startangle=140, wedgeprops={"edgecolor":"w"})
    plt.title(title, pad=30)
    plt.axis('equal')

# 绘制
plot_grouped_pie(mot_data, "Top 10 Words - MOT")
plt.show()

plot_grouped_pie(chi_data, "Top 10 Words - CHI")
plt.show()