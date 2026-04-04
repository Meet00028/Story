
import json
from datetime import date

try:
    with open('commit_schedule.json', 'r') as f:
        schedule = json.load(f)

    total_dates = len(schedule)
    total_files = sum(len(entry['files']) for entry in schedule.values())
    committed_dates = sum(1 for entry in schedule.values() if entry['committed'])
    
    sorted_dates = sorted(schedule.keys())
    first_date = sorted_dates[0] if sorted_dates else "N/A"
    last_date = sorted_dates[-1] if sorted_dates else "N/A"
    
    # Check specifically for today (2026-02-10)
    today_str = "2026-02-10"
    today_status = schedule.get(today_str, {}).get('committed', False)

    print(f"Total Files Scheduled: {total_files}")
    print(f"Total Dates: {total_dates}")
    print(f"Date Range: {first_date} to {last_date}")
    print(f"Committed Dates: {committed_dates}")
    print(f"Remaining Dates: {total_dates - committed_dates}")
    print(f"Status for Today ({today_str}): {'Committed' if today_status else 'Pending'}")

except FileNotFoundError:
    print("commit_schedule.json not found.")
except Exception as e:
    print(f"Error analyzing schedule: {e}")
