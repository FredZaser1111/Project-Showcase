import requests
import json
import time

url = "http://localhost:5000/api/predict"
data = {
    "home_team_id": 1610612747,
    "visitor_team_id": 1610612738,
    "injury_data": {
        "injured_players": {
            "home": ["LeBron James"],
            "visitor": []
        }
    }
}

print("Testing prediction with injury data...")
print(f"Data: {json.dumps(data, indent=2)}")
start = time.time()

try:
    response = requests.post(url, json=data, timeout=30)
    elapsed = time.time() - start
    print(f"\nResponse in {elapsed:.2f} seconds")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            pred = result.get('prediction', {})
            print(f"Home Win: {pred.get('home_win_probability', 0):.2%}")
    else:
        print(f"Error: {response.text[:200]}")
except requests.exceptions.Timeout:
    print(f"\nTIMEOUT after {time.time() - start:.2f} seconds")
except Exception as e:
    print(f"\nError: {e}")
