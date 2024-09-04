import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_news(query: str = "", headlines_only: bool = False) -> dict:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    if not NEWS_API_KEY:
        return {"error": "News API key not found"}

    base_url = "https://newsdata.io/api/1/latest"
    
    params = {
        'apikey': NEWS_API_KEY,
        'country': "gb",
        'prioritydomain': 'top',
        'size': 5,
        'language': 'en'
    }
    
    if headlines_only or not query:
        params['domainurl'] = "bbc.com"
    else:
        params['q'] = query.strip()
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return {"error": f"News API request failed: {str(e)}"}
    
    if response.status_code == 200:
        simplified_results = [
            {
                "title": article.get("title"),
                "link": article.get("link"),
                "description": article.get("description")
            }
            for article in data.get('results', [])[:5]
        ]
        return {
            "status": data.get("status"),
            "totalResults": data.get("totalResults"),
            "results": simplified_results
        }
    else:
        return {"error": f"API request failed with status code {response.status_code}"}