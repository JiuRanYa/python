import json
import csv

# 读取JSON文件
with open('result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 准备CSV文件
with open('result.csv', 'w', encoding='utf-8', newline='') as f:
    # 定义CSV表头
    writer = csv.writer(f)
    writer.writerow(['title', 'description', 'url', 'tags'])
    
    # 写入数据
    for item in data:
        # 将tags列表转换为字符串
        tags_str = '|'.join(item['tags'])
        writer.writerow([
            item['title'],
            item['description'],
            item['url'],
            tags_str
        ])

print(f"已成功将{len(data)}条数据转换为CSV格式") 