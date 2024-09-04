import json
import os
from datetime import datetime
from fuzzywuzzy import fuzz

def take_notes(notes: str = None, search: bool = False, query: str = None) -> str:
    notes_file = "user_notes.json"
    
    # Ensure the JSON file exists
    if not os.path.exists(notes_file):
        with open(notes_file, "w") as f:
            json.dump([], f)
    
    if not search:
        # Taking a new note
        if not notes:
            return "Error: No notes provided to save."
        
        timestamp = datetime.now().isoformat()
        new_note = {"date": timestamp, "content": notes}
        
        try:
            with open(notes_file, "r+") as f:
                data = json.load(f)
                data.append(new_note)
                f.seek(0)
                json.dump(data, f, indent=2)
        except json.JSONDecodeError:
            return "Error: Failed to read notes file."
        except IOError:
            return "Error: Failed to write to notes file."
        
        return f"Note saved: {notes}"
    
    else:
        # Searching notes
        if not query:
            return "Error: No search query provided."
        
        try:
            with open(notes_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return "Error: Failed to read notes file."
        except IOError:
            return "Error: Failed to open notes file."
        
        results = []
        for note in data:
            date_match = fuzz.partial_ratio(query, note["date"])
            content_match = fuzz.partial_ratio(query, note["content"])
            
            if date_match > 70 or content_match > 70:
                results.append(note)
        
        # Sort results by date and limit to 5
        results.sort(key=lambda x: x["date"], reverse=True)
        results = results[:5]
        
        if not results:
            return "No matching notes found."
        
        output = "Matching notes (up to 5 most recent):\n\n"
        for note in results:
            date = datetime.fromisoformat(note["date"]).strftime("%Y-%m-%d %H:%M:%S")
            output += f"Date: {date}\nContent: {note['content']}\n\n"
        
        return output.strip()