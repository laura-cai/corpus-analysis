import pandas as pd

# 读取数据
mom_df = pd.read_csv('mom.csv')
child_df = pd.read_csv('child.csv')

# 提取姓名（去掉.cha）
mom_df['Name'] = mom_df['File'].str.replace('.cha', '')
child_df['Name'] = child_df['File'].str.replace('.cha', '')

# 定义指标
metrics = {
    'Word Frequency': 'FREQ_tokens',
    'Lexical Diversity': 'FREQ_TTR',
    'Utterance Length': 'MLU_Words',
    'Interactiveness': 'Total_Utts'
}

def print_table(data, title1, title2, title3):
    """打印左对齐表格"""
    print(f"{title1:<20} {title2:<10} {title3:<10}")
    print(f"{'-'*20} {'-'*10} {'-'*10}")
    for row in data:
        print(f"{row[0]:<20} {row[1]:<10} {row[2]:<10}")

# Q3：母亲
print("Q3: Which mother(s) show the highest level...")
print()
result_mom = []
for metric, col in metrics.items():
    max_row = mom_df.loc[mom_df[col].idxmax()]
    result_mom.append([metric, max_row['Name'], f"{max_row[col]:.3f}"])

print_table(result_mom, 'Metric', 'Mother', 'Value')

print("\n" + "="*60 + "\n")

# Q4：孩子
print("Q4: Which child(ren) show the highest level...")
print()
result_child = []
for metric, col in metrics.items():
    max_row = child_df.loc[child_df[col].idxmax()]
    result_child.append([metric, max_row['Name'], f"{max_row[col]:.3f}"])

print_table(result_child, 'Metric', 'Child', 'Value')