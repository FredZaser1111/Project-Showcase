import requests
import json
import sys

url = "http://localhost:5000/api/predict"
data = {
    "home_team_id": 1610612747,
    "visitor_team_id": 1610612738
}

print("Making test prediction request...")
try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 500:
        try:
            error_data = response.json()
            print(f"\n{'='*70}")
            print("ERROR DETAILS:")
            print(f"{'='*70}")
            print(f"Error: {error_data.get('error', 'Unknown')}")
            print(f"Error Type: {error_data.get('error_type', 'Unknown')}")
            if 'traceback' in error_data and error_data['traceback']:
                print(f"\n{'='*70}")
                print("FULL TRACEBACK:")
                print(f"{'='*70}")
                print(error_data['traceback'])
            else:
                print("\nNo traceback in response (FLASK_DEBUG might be False)")
        except Exception as e:
            print(f"Could not parse error response: {e}")
            print(f"Raw response: {response.text[:1000]}")
    else:
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Request failed: {e}")
    import traceback
    traceback.print_exc()
