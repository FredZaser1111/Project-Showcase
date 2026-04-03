"""Test if injury data actually affects predictions."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from models.predictor import GamePredictor
import json
from datetime import datetime

# Load predictor
games_file = Path('data/historical_games.json')
games_data = []
if games_file.exists():
    with open(games_file, 'r') as f:
        games_data = json.load(f)

try:
    predictor = GamePredictor(games_data=games_data)
    
    # Test with Lakers (1610612747) vs Warriors (1610612748)
    home_team_id = 1610612747  # Lakers
    visitor_team_id = 1610612748  # Warriors
    
    print("=" * 60)
    print("TESTING INJURY IMPACT ON PREDICTIONS")
    print("=" * 60)
    
    # Prediction WITHOUT injuries (all players available)
    print("\n1. Prediction WITHOUT injuries:")
    pred_no_injury = predictor.predict(
        home_team_id=home_team_id,
        visitor_team_id=visitor_team_id,
        game_date=datetime.now()
    )
    print(f"   Home Win Probability: {pred_no_injury['home_win_probability']:.3f}")
    print(f"   Visitor Win Probability: {pred_no_injury['visitor_win_probability']:.3f}")
    print(f"   Predicted Winner: {pred_no_injury['predicted_winner']}")
    
    # Prediction WITH star player injured (home team)
    print("\n2. Prediction WITH home star player INJURED:")
    pred_star_injured = predictor.predict(
        home_team_id=home_team_id,
        visitor_team_id=visitor_team_id,
        game_date=datetime.now(),
        injury_data={
            'home': {
                'key_players_available': 2,  # Assume 1 key player out
                'star_player_available': 0   # Star player OUT
            },
            'visitor': {
                'key_players_available': 3,
                'star_player_available': 1
            }
        }
    )
    print(f"   Home Win Probability: {pred_star_injured['home_win_probability']:.3f}")
    print(f"   Visitor Win Probability: {pred_star_injured['visitor_win_probability']:.3f}")
    print(f"   Predicted Winner: {pred_star_injured['predicted_winner']}")
    
    # Compare
    print("\n3. COMPARISON:")
    home_prob_diff = pred_star_injured['home_win_probability'] - pred_no_injury['home_win_probability']
    visitor_prob_diff = pred_star_injured['visitor_win_probability'] - pred_no_injury['visitor_win_probability']
    
    print(f"   Home Win Prob Change: {home_prob_diff:+.3f} ({home_prob_diff*100:+.1f}%)")
    print(f"   Visitor Win Prob Change: {visitor_prob_diff:+.3f} ({visitor_prob_diff*100:+.1f}%)")
    
    if abs(home_prob_diff) > 0.01:  # More than 1% change
        print("\n   ✅ INJURY DATA IS AFFECTING PREDICTIONS!")
        print(f"   The model reduces home team's win probability by {abs(home_prob_diff)*100:.1f}%")
        print(f"   when the star player is injured.")
    else:
        print("\n   ⚠️  WARNING: Injury data may not be significantly affecting predictions.")
        print("   This could mean:")
        print("   - The model wasn't trained with enough injury data")
        print("   - The injury features have low importance")
        print("   - Need to retrain with more injury examples")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

