"""Test the roster endpoint to debug the issue."""
import requests
import json

# Test with Lakers (team ID 1610612747)
team_id = 1610612747

print(f"Testing roster endpoint for team {team_id}...")
try:
    response = requests.get(f"http://localhost:5000/api/roster/{team_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

