import re
import json
from collections import defaultdict
from datetime import datetime, timedelta

def parse_log_file_daily(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    error_pattern = re.compile(r"脚本发生错误")
    date_pattern = re.compile(r"\['(.*?)'\]")
    timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    # Define the time window for the last 7 days
    now = datetime.now()
    time_window_start = now - timedelta(days=7)

    # Dictionary to store dates grouped by log date and then by month
    log_dates = defaultdict(lambda: defaultdict(set))  # Use set to ensure unique dates

    # Iterate over the lines in the log file and collect dates
    for line in lines:
        if error_pattern.search(line):
            continue  # Skip error lines

        timestamp_match = timestamp_pattern.search(line)
        if timestamp_match:
            timestamp = datetime.strptime(timestamp_match.group(), "%Y-%m-%d %H:%M:%S")
            if timestamp < time_window_start:
                continue  # Skip logs older than 7 days

            log_date = timestamp.date().strftime("%Y-%m-%d")  # Use only the date part
            
            date_match = date_pattern.search(line)
            if date_match:
                dates = set(date_match.group(1).split("', '"))
                for date in dates:
                    # Parse the date to get the year and month
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    month_key = date_obj.strftime("%Y-%m")
                    log_dates[log_date][month_key].add(date)  # Use set to ensure uniqueness

    # Sort dates within each month and sort months for each log date
    sorted_log_dates = {}
    for log_date in sorted(log_dates.keys(), reverse=True):  # Sort log dates in descending order
        sorted_months = {}
        for month in sorted(log_dates[log_date].keys()):  # Sort months
            sorted_months[month] = sorted(log_dates[log_date][month])  # Sort dates within each month
        sorted_log_dates[log_date] = sorted_months

    # Write results to a JSON file with the original key-based structure
    with open("./data/new_slots_daily.json", "w", encoding='utf-8') as json_file:
        json.dump(sorted_log_dates, json_file, ensure_ascii=False, indent=4)

    print("Results written to new_slots_daily.json")

# Path to your log file
file_path = 'data/appointment_log.txt'
parse_log_file_daily(file_path)
