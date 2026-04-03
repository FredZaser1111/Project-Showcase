"""
Test to capture the exact 500 error.
"""
import requests
import json
import traceback

url = "http://localhost:5000/api/predict"
data = {
    "home_team_id": 1610612747,
    "visitor_team_id": 1610612738
}

print("Testing prediction endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 500:
        try:
            error_data = response.json()
            print(f"\nError: {error_data.get('error', 'Unknown error')}")
            if 'traceback' in error_data:
                print(f"\nTraceback:\n{error_data['traceback']}")
        except:
            print(f"\nFull response: {response.text}")
except Exception as e:
    print(f"\nRequest failed: {e}")
    traceback.print_exc()

