"""
Test prediction with different injury scenarios.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.predictor import GamePredictor
from api_client_nba import NBAAPIClient
from datetime import datetime
import json
from pathlib import Path
import config

def test_prediction_scenarios():
    """Test predictions with different injury scenarios."""
    print("=" * 60)
    print("Testing Predictions with Different Injury Scenarios")
    print("=" * 60)
    
    # Initialize API client and get games data
    print("\n1. Loading games data...")
    api_client = NBAAPIClient()
    games_data = api_client.get_all_games()
    print(f"   Loaded {len(games_data)} games")
    
    # Initialize predictor
    print("\n2. Loading model...")
    try:
        pred = GamePredictor(games_data=games_data)
        print("   Model loaded successfully")
    except Exception as e:
        print(f"   ERROR loading model: {e}")
        return
    
    # Test teams (Lakers vs Celtics)
    home_team_id = 1610612747  # Lakers
    visitor_team_id = 1610612738  # Celtics
    game_date = datetime.now()
    
    print(f"\n3. Testing predictions:")
    print(f"   Home: Los Angeles Lakers ({home_team_id})")
    print(f"   Visitor: Boston Celtics ({visitor_team_id})")
    
    # Test scenarios
    scenarios = [
        {
            "name": "No injuries",
            "injury_data": None
        },
        {
            "name": "1 injured player (home team)",
            "injury_data": {
                "home": {
                    "key_players_available": 2,
                    "star_player_available": 1
                },
                "visitor": {
                    "key_players_available": 3,
                    "star_player_available": 1
                }
            }
        },
        {
            "name": "Star player injured (home team)",
            "injury_data": {
                "home": {
                    "key_players_available": 3,
                    "star_player_available": 0
                },
                "visitor": {
                    "key_players_available": 3,
                    "star_player_available": 1
                }
            }
        },
        {
            "name": "Multiple injuries (both teams)",
            "injury_data": {
                "home": {
                    "key_players_available": 1,
                    "star_player_available": 0
                },
                "visitor": {
                    "key_players_available": 2,
                    "star_player_available": 1
                }
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        try:
            prediction = pred.predict(
                home_team_id=home_team_id,
                visitor_team_id=visitor_team_id,
                game_date=game_date,
                injury_data=scenario['injury_data']
            )
            
            home_prob = prediction['home_win_probability'] * 100
            visitor_prob = prediction['visitor_win_probability'] * 100
            winner = prediction['predicted_winner']
            
            print(f"      ✓ SUCCESS")
            print(f"      Home Win Prob: {home_prob:.1f}%")
            print(f"      Visitor Win Prob: {visitor_prob:.1f}%")
            print(f"      Predicted Winner: {winner}")
            print(f"      Confidence: {prediction['confidence']*100:.1f}%")
            
        except Exception as e:
            print(f"      ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_prediction_scenarios()


