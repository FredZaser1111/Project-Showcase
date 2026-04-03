import requests
import json
import time
import sys

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

print("=" * 70)
print("TESTING PREDICTION WITH DETAILED TIMING")
print("=" * 70)
print(f"\nRequest: {json.dumps(data, indent=2)}")
print("\nSending request...")
print("Watch Flask terminal for detailed logs...")
print("-" * 70)

start = time.time()
try:
    response = requests.post(url, json=data, timeout=35)
    elapsed = time.time() - start
    print(f"\nResponse received in {elapsed:.2f} seconds")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            pred = result.get('prediction', {})
            print(f"\n[SUCCESS] Prediction completed!")
            print(f"  Home Win: {pred.get('home_win_probability', 0):.2%}")
            print(f"  Visitor Win: {pred.get('visitor_win_probability', 0):.2%}")
        else:
            print(f"\n[FAILED] {result.get('error', 'Unknown error')}")
    else:
        print(f"\n[ERROR] Status {response.status_code}")
        print(f"Response: {response.text[:500]}")
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f"\n[TIMEOUT] Request timed out after {elapsed:.2f} seconds")
    print("Check Flask terminal logs to see where it hung")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n[ERROR] After {elapsed:.2f} seconds: {e}")
    import traceback
    traceback.print_exc()
