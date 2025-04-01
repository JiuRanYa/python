import json
import csv

# 读取JSON文件
with open('result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if not data:
    print("没有数据需要转换")
    exit()

# 获取所有可能的列名（从第一个数据项中获取所有键）
columns = list(data[0].keys())

# 准备CSV文件
with open('result.csv', 'w', encoding='utf-8', newline='') as f:
    # 定义CSV表头
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # 对所有字段使用引号
    writer.writerow(columns)
    
    # 写入数据
    for item in data:
        row = []
        for column in columns:
            value = item.get(column, '')
            # 如果值是列表，将其转换为分号分隔的字符串
            if isinstance(value, list):
                value = ';'.join(str(v) for v in value)
            row.append(value)
        writer.writerow(row)

print(f"已成功将{len(data)}条数据转换为CSV格式")
print(f"CSV列名: {', '.join(columns)}") 