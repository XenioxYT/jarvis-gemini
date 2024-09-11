import json
from datetime import datetime

def set_reminder(name: str, timestamp: str) -> str:
    """Set a reminder with the given name and timestamp. Timestamp needs to be provided in the format YYYY-MM-DD HH:MM:SS"""
    try:
        reminder_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        reminder = {
            "name": name,
            "created_at": datetime.now().timestamp(),
            "reminder_at": reminder_datetime.timestamp()
        }
        
        try:
            with open("reminders.json", "r") as f:
                reminders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            reminders = []
        
        reminders.append(reminder)
        
        with open("reminders.json", "w") as f:
            json.dump(reminders, f)
        
        return f"Set reminder '{name}' for {timestamp}"
    except ValueError:
        raise ValueError("Invalid timestamp format. Please use YYYY-MM-DD HH:MM:SS")

def get_reminders(mode: str = 'upcoming', start_date: str = None, end_date: str = None, limit: int = 10) -> list:
    """Get a list of reminders based on specified criteria."""
    try:
        with open("reminders.json", "r") as f:
            reminders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        reminders = []
    
    current_time = datetime.now().timestamp()
    
    if start_date:
        start_timestamp = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
    if end_date:
        end_timestamp = datetime.strptime(end_date, "%Y-%m-%d").timestamp()
    
    if mode == 'upcoming':
        filtered_reminders = [r for r in reminders if r['reminder_at'] > current_time]
        sorted_reminders = sorted(filtered_reminders, key=lambda x: x['reminder_at'])
    elif mode == 'recent':
        sorted_reminders = sorted(reminders, key=lambda x: x['created_at'], reverse=True)
    else:
        raise ValueError("Invalid mode. Use 'upcoming' or 'recent'.")
    
    if start_date and end_date:
        sorted_reminders = [r for r in sorted_reminders if start_timestamp <= r['reminder_at'] <= end_timestamp]
    elif start_date:
        sorted_reminders = [r for r in sorted_reminders if r['reminder_at'] >= start_timestamp]
    elif end_date:
        sorted_reminders = [r for r in sorted_reminders if r['reminder_at'] <= end_timestamp]
    
    # Convert timestamps to strings before returning
    for reminder in sorted_reminders:
        reminder['created_at'] = datetime.fromtimestamp(reminder['created_at']).strftime("%Y-%m-%d %H:%M:%S")
        reminder['reminder_at'] = datetime.fromtimestamp(reminder['reminder_at']).strftime("%Y-%m-%d %H:%M:%S")
    
    return sorted_reminders[:limit]

def get_reminders_unix() -> list:
    """Get all reminders with Unix timestamps for internal checking."""
    try:
        with open("reminders.json", "r") as f:
            reminders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        reminders = []
    
    return reminders