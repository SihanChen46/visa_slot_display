import re
import json
from collections import defaultdict
from datetime import datetime, timedelta

def parse_log_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    error_pattern = re.compile(r"脚本发生错误")
    date_pattern = re.compile(r"\['(.*?)'\]")
    timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    # Define the time window for the last 24 hours
    now = datetime.now()
    time_window_start = now - timedelta(hours=24)

    # Dictionary to store dates found within each hour
    hourly_dates = defaultdict(set)
    results = []

    # Iterate over the lines in the log file and collect dates by hour
    for line in lines:
        if error_pattern.search(line):
            continue  # Skip error lines

        timestamp_match = timestamp_pattern.search(line)
        if timestamp_match:
            timestamp = datetime.strptime(timestamp_match.group(), "%Y-%m-%d %H:%M:%S")
            if timestamp < time_window_start:
                continue  # Skip logs older than 24 hours

            hour = timestamp.replace(minute=0, second=0, microsecond=0)
            
            date_match = date_pattern.search(line)
            if date_match:
                dates = set(date_match.group(1).split("', '"))
                hourly_dates[hour].update(dates)

    # Sort the hours and find unique dates for each hour
    sorted_hours = sorted(hourly_dates.keys(), reverse=True)
    for i in range(1, len(sorted_hours)):
        current_hour = sorted_hours[i]
        previous_hour = sorted_hours[i - 1]

        if current_hour >= now.replace(minute=0, second=0, microsecond=0):
            continue  # Skip the latest, unfinished hour

        # Calculate the difference between the current hour's dates and the previous hour's dates
        new_dates = hourly_dates[current_hour] - hourly_dates[previous_hour]
        if new_dates:
            results.append({
                "hour": current_hour.strftime("%Y-%m-%d %H:%M:%S"),
                "new_dates": sorted(new_dates)
            })

    # Write results to a JSON file
    with open("./data/new_slots_hourly.json", "w", encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    print("Results written to parsed_results.json")

# Path to your log file
file_path = 'data/appointment_log.txt'
parse_log_file(file_path)
