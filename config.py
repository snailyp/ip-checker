# 读取JSON配置文件
import json

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
