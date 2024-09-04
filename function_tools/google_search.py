import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def google_search(query: str) -> list:
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cse_id:
        return [{"error": "Google API key or CSE ID not found"}]

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id, gl="uk", num=5).execute()
    except Exception as e:
        return [{"error": f"Google Search API request failed: {str(e)}"}]
    
    results = []
    for item in res.get("items", []):
        try:
            results.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item["snippet"]
            })
        except KeyError:
            results.append({"error": "Invalid response from Google Search API"})
    
    return results