import os
import json
import subprocess
import math
from datetime import date, timedelta, datetime

# Configuration
START_DATE = date(2026, 2, 1)
END_DATE = date(2026, 4, 17)
EXCLUDED_DIRS = {'.git', 'node_modules', '__pycache__', '.DS_Store', 'venv', 'env'}
EXCLUDED_FILES = {'drip_feed.py', 'commit_schedule.json', '.DS_Store', 'analyze_schedule.py', 'trigger_render.py', 'verify_fix_direct.py', 'check_vfx.py', 'create_dummy_assets.py'}
SCHEDULE_FILE = 'commit_schedule.json'

def run_command(command, env=None, ignore_errors=False):
    """Run a shell command."""
    try:
        subprocess.run(command, check=True, shell=True, env=env)
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"Warning: Command failed but ignored: {command}\n{e}")
        else:
            print(f"Error running command: {command}\n{e}")
            exit(1)

def get_files(root_dir):
    """Recursively scan for real code files."""
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            if file in EXCLUDED_FILES:
                continue
            file_list.append(os.path.join(root, file))
    return sorted(file_list) # Sort for deterministic behavior before shuffling/splitting

def generate_date_range(start, end):
    """Generate a list of dates from start to end (inclusive)."""
    delta = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(delta)]

def create_schedule(files, dates):
    """Distribute files across dates."""
    total_files = len(files)
    total_dates = len(dates)
    
    if total_files == 0:
        print("No files found to schedule.")
        return {}

    batch_size = math.ceil(total_files / total_dates)
    schedule = {}
    
    file_idx = 0
    for day in dates:
        date_str = day.isoformat()
        # Determine batch for this day
        # We use a simple slice, but need to be careful not to exceed bounds
        # or leave files if batch_size is too small due to rounding.
        # math.ceil ensures we cover all files, potentially finishing early.
        
        # Better distribution: distribute remainder
        # But user said "roughly equal". ceil is fine.
        
        # Actually, let's just chunk it.
        if file_idx < total_files:
            # Calculate remaining files and remaining days to adjust batch size dynamically?
            # Or just fixed batch size?
            # Let's do dynamic to be smoother.
            remaining_files = total_files - file_idx
            remaining_days = total_dates - dates.index(day)
            current_batch_size = math.ceil(remaining_files / remaining_days)
            
            batch = files[file_idx : file_idx + current_batch_size]
            file_idx += current_batch_size
            
            schedule[date_str] = {
                "files": batch,
                "committed": False
            }
        else:
            schedule[date_str] = {
                "files": [],
                "committed": False
            }
            
    return schedule

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_schedule(schedule):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f, indent=2)

def main():
    # Ensure git repo
    if not os.path.exists('.git'):
        print("Initializing git repository...")
        run_command("git init")

    schedule = load_schedule()
    
    if not schedule:
        print("Generating new schedule...")
        files = get_files('.')
        dates = generate_date_range(START_DATE, END_DATE)
        schedule = create_schedule(files, dates)
        save_schedule(schedule)
        print(f"Scheduled {len(files)} files across {len(dates)} days.")
    else:
        print("Loaded existing schedule.")

    today = date.today()
    print(f"Today is {today}")

    # Sort dates to process in order
    sorted_dates = sorted(schedule.keys())
    
    for date_str in sorted_dates:
        entry = schedule[date_str]
        scheduled_date = date.fromisoformat(date_str)
        
        if entry['committed']:
            continue
            
        if scheduled_date > today:
            # Future date, stop processing
            print(f"Date {date_str} is in the future. Stopping.")
            break
            
        files_to_commit = entry['files']
        if not files_to_commit:
            print(f"No files scheduled for {date_str}. Marking as done.")
            entry['committed'] = True
            save_schedule(schedule)
            continue

        print(f"Processing batch for {date_str} ({len(files_to_commit)} files)...")
        
        # Prepare environment for backdating
        env = os.environ.copy()
        if scheduled_date < today:
            # Set time to noon on that day
            timestamp = f"{date_str} 12:00:00"
            env['GIT_AUTHOR_DATE'] = timestamp
            env['GIT_COMMITTER_DATE'] = timestamp
            print(f"  Backdating to {timestamp}")
        
        for file_path in files_to_commit:
            # Check if file exists (might have been deleted)
            if not os.path.exists(file_path):
                print(f"  Warning: File {file_path} not found, skipping.")
                continue
                
            # Git add
            run_command(f'git add "{file_path}"', env=env, ignore_errors=True)
            
            # Git commit
            filename = os.path.basename(file_path)
            message = f"Implement {filename} logic"
            # Use --allow-empty in case file didn't change or was already added
            run_command(f'git commit --allow-empty -m "{message}"', env=env)
        
        entry['committed'] = True
        save_schedule(schedule)
        print(f"  Completed batch for {date_str}.")

    # Push changes to GitHub
    print("Pushing changes to GitHub...")
    run_command("git push origin master", ignore_errors=True)

if __name__ == "__main__":
    main()
