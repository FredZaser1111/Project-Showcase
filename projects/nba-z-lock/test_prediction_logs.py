import requests
import json

# Test prediction
url = "http://localhost:5000/api/predict"
data = {
    "home_team_id": 1610612747,  # Lakers
    "visitor_team_id": 1610612738,  # Celtics
    "injury_data": None
}

print("Sending prediction request...")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"\nError: {e}")
