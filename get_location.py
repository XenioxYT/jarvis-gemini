import requests
import json

def get_location():
    # Get public IP address
    ip_response = requests.get("https://whatismyip.akamai.com")
    public_ip = ip_response.text.strip()

    # Get location data
    url = f"http://ip-api.com/json/{public_ip}"
    response = requests.get(url)
    data = json.loads(response.text)
    
    return f"{data['city']}, {data['country']}"

# Example usage
if __name__ == "__main__":
    location = get_location()
    print(location)