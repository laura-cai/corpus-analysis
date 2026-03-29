import glob
import os
import re

def count_turn_taking(file_path):
    """
    计算一个 .cha 文件中的 turn-taking
    每行开头是 '*XXX' 且内容不为 '0' 才算一个 turn
    """
    speakers = []

    pattern = re.compile(r'^\*(\w+)')  # 匹配 *CHI, *MOT 等
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            if match:
                speaker = match.group(0)  # '*CHI', '*MOT'
                # 内容在冒号之后
                if ':' in line:
                    content = line.split(':', 1)[1].strip()
                    if not re.search(r'\b0\b', content): # 单个0出现就说明这句话孩子没有说
                        speakers.append(speaker)

    # 计算 turn-taking：连续 speaker 不同才算一次
    switches = 0
    for i in range(1, len(speakers)):
        if speakers[i] != speakers[i-1]:
            switches += 1

    # 文件名去掉 .cha 作为 child_name
    child_name = os.path.basename(file_path).replace('.cha','')

    return child_name, switches

def main():
    cha_files = glob.glob('free20/*.cha')
    results = []

    for file_path in cha_files:
        child_name, switches = count_turn_taking(file_path)
        results.append((child_name, switches))

    # 输出结果
    for child_name, switches in results:
        print(f"{child_name} {switches}")

if __name__ == "__main__":
    main()