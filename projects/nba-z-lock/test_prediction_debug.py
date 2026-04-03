"""
Debug script to test prediction endpoint and identify issues.
"""
import requests
import json
import time
from datetime import datetime

def test_prediction(home_team_id=1610612747, visitor_team_id=1610612738, injury_data=None):
    """Test prediction endpoint with detailed logging."""
    url = "http://localhost:5000/api/predict"
    
    data = {
        "home_team_id": home_team_id,
        "visitor_team_id": visitor_team_id,
        "injury_data": injury_data
    }
    
    print("\n" + "=" * 60)
    print("TESTING PREDICTION ENDPOINT")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print(f"URL: {url}")
    print(f"Request Data:")
    print(json.dumps(data, indent=2))
    print("\nSending request...")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=data, timeout=120)
        elapsed = time.time() - start_time
        
        print(f"\nResponse received in {elapsed:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"\nResponse Data:")
            print(json.dumps(response_data, indent=2))
            
            if response_data.get('success'):
                print("\n[SUCCESS] Prediction completed successfully!")
                pred = response_data.get('prediction', {})
                print(f"  Home Win Probability: {pred.get('home_win_probability', 0):.2%}")
                print(f"  Visitor Win Probability: {pred.get('visitor_win_probability', 0):.2%}")
                print(f"  Predicted Winner: {pred.get('predicted_winner', 'unknown')}")
            else:
                print("\n[FAILURE] Prediction failed!")
                print(f"  Error: {response_data.get('error', 'Unknown error')}")
                if 'traceback' in response_data:
                    print("\n  Traceback:")
                    print(response_data['traceback'])
        except json.JSONDecodeError:
            print(f"\n[ERROR] Response is not valid JSON")
            print(f"Response text: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"\n[TIMEOUT] Request timed out after {elapsed:.2f} seconds")
        print("The server is taking too long to respond.")
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to server")
        print("Make sure Flask is running on http://localhost:5000")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] Exception occurred after {elapsed:.2f} seconds")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nTraceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    print("=" * 60)
    print("NBA Z-LOCK PREDICTION DEBUG TEST")
    print("=" * 60)
    
    # Test 1: No injuries
    print("\n" + "-" * 60)
    print("TEST 1: Prediction without injuries")
    print("-" * 60)
    test_prediction()
    
    # Test 2: With injuries (empty)
    print("\n" + "-" * 60)
    print("TEST 2: Prediction with empty injury data")
    print("-" * 60)
    test_prediction(injury_data={"injured_players": {"home": [], "visitor": []}})
    
    print("\n" + "=" * 60)
    print("DEBUG TEST COMPLETE")
    print("=" * 60)
    print("\nCheck the Flask server terminal for detailed backend logs.")
    print("Check this output for frontend/network issues.")


