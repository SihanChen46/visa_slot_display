#!/bin/bash
python3 parse_hour_update.py

# 添加更改的文件
git add new_slots_hourly.json

# 提交更改
git commit -m "自动更新 new_slots_hourly.json"

# 推送到远程仓库
git push origin main
