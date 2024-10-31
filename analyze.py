import re
from collections import defaultdict
from datetime import datetime

# 日志文件路径
log_file_path = "./appointment_log.txt"

# 正则表达式匹配找到的日期
date_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*找到可用日期：\[(.*?)\]"
error_pattern = r"脚本发生错误|Message|Stacktrace|disconnected"

# 存储每天刷到的每个月不同位置的日期
results = defaultdict(lambda: defaultdict(set))

# 读取日志文件并解析
with open(log_file_path, 'r', encoding='utf-8') as log_file:
    for line in log_file:
        # 过滤掉错误信息
        if re.search(error_pattern, line):
            continue
        
        # 匹配找到的日期信息
        match = re.search(date_pattern, line)
        if match:
            log_datetime = match.group(1)
            found_dates = match.group(2)

            # 提取主日期
            main_date = datetime.strptime(log_datetime, "%Y-%m-%d %H:%M:%S").date()

            # 解析日期列表
            for date_str in found_dates.split(", "):
                # 去除多余的字符
                date_str = date_str.strip("'")
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                month_str = parsed_date.strftime("%Y-%m")

                # 添加到结果中
                results[main_date][month_str].add(parsed_date)

# 输出结果，按日期和年月排序
for date in sorted(results.keys()):
    print(f"{date} 刷到的月份及位置：")
    for month in sorted(results[date].keys()):
        date_list = sorted(results[date][month])
        print(f"  - {month}：{len(date_list)} 个位置：{', '.join(date.strftime('%m.%d') for date in date_list)}")
    print()
