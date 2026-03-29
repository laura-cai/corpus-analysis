import re
from collections import defaultdict, Counter

# 输入文件路径
filename = "free20_output.txt"

# 要统计的Top N
TOP_N = 10

# 初始化字典
data = {"MOT": Counter(), "CHI": Counter()}

current_speaker = None

# 正则匹配行格式: "frequency pos|word"
line_re = re.compile(r"\s*(\d+)\s+([^\|]+)\|(.+)")

with open(filename, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("Speaker:"):
            if "*MOT" in line:
                current_speaker = "MOT"
            elif "*CHI" in line:
                current_speaker = "CHI"
            else:
                current_speaker = None
        elif current_speaker:
            m = line_re.match(line)
            if m:
                freq = int(m.group(1))
                pos = m.group(2)
                word = m.group(3)
                data[current_speaker][(word, pos)] += freq

# 输出Top N词表
for speaker in ["MOT", "CHI"]:
    print(f"\nTop {TOP_N} words & POS for {speaker}:")
    top_words = data[speaker].most_common(TOP_N)
    print(f"{'Word':<15}{'POS':<15}{'Frequency':<10}")
    print("-"*40)
    for (word, pos), freq in top_words:
        print(f"{word:<15}{pos:<15}{freq:<10}")

