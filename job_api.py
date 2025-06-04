import requests

def fetch_jobs(job_title, preferences):
    try:
        # Adzuna API parameters
        API_ID = "YOUR_API_ID"
        API_KEY = "YOUR_API_KEY"
        BASE_URL = "https://api.adzuna.com/v1/api/jobs"
        
        params = {
            "app_id": API_ID,
            "app_key": API_KEY,
            "what": job_title,
            "where": "us",  # Default location
            "remote": 1 if preferences.get("remote") else 0,
            "results_per_page": 10
        }
        
        response = requests.get(f"{BASE_URL}/us/search/1", params=params)
        response.raise_for_status()
        
        return [{
            "title": job["title"],
            "company": job["company"]["display_name"],
            "location": job["location"]["display_name"],
            "description": job["description"],
            "url": job["redirect_url"]
        } for job in response.json().get("results", [])]
    
    except Exception as e:
        raise RuntimeError(f"API call failed: {str(e)}")