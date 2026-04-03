"""
Test prediction directly to capture the exact error.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from models.predictor import GamePredictor
from datetime import datetime
import json

print("=" * 70)
print("TESTING PREDICTION DIRECTLY (TO CAPTURE ERROR)")
print("=" * 70)

# Load games data
games_file = Path('data/historical_games.json')
if games_file.exists():
    with open(games_file, 'r') as f:
        games_data = json.load(f)
    print(f"\nLoaded {len(games_data)} games from file")
else:
    print("\nERROR: Games file not found!")
    sys.exit(1)

# Try to initialize predictor
print("\n1. Initializing GamePredictor...")
try:
    pred = GamePredictor(games_data=games_data)
    print("   [OK] Predictor initialized")
except Exception as e:
    print(f"   [ERROR] Failed to initialize: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try to make a prediction
print("\n2. Making prediction...")
try:
    result = pred.predict(
        home_team_id=1610612747,  # Lakers
        visitor_team_id=1610612738,  # Celtics
        game_date=datetime.now(),
        injury_data=None
    )
    print(f"   [OK] Prediction successful!")
    print(f"   Home Win: {result['home_win_probability']:.2%}")
except Exception as e:
    print(f"   [ERROR] Prediction failed: {e}")
    print(f"\n{'='*70}")
    print("FULL ERROR TRACEBACK:")
    print(f"{'='*70}")
    import traceback
    traceback.print_exc()
    print(f"{'='*70}")

