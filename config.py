# 读取JSON配置文件
import json

with open('config.json', 'r') as f:
    config = json.load(f)
