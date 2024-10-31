#!/bin/bash

# 无限循环
while true; do
  # 打印当前时间以便于调试
  echo "运行任务时间: $(date)"

  # 运行您的 Python 脚本
  python3 parse_hourly_update.py
  python3 parse_daily_update.py

  # 添加更改的文件
  git add data/new_slots_hourly.json
  git add data/new_slots_dayly.json

  # 提交更改
  git commit -m "自动更新 new_slots_hourly.json"

  # 推送到远程仓库
  git push origin main

  # 休眠 45 分钟（2700 秒）
  sleep 2700
done
