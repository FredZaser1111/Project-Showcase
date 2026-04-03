"""
Test prediction with detailed timing to find bottlenecks.
"""
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from models.predictor import GamePredictor
from datetime import datetime

def test_prediction_with_timing():
    """Test prediction with detailed timing."""
    print("=" * 70)
    print("TESTING PREDICTION WITH DETAILED TIMING")
    print("=" * 70)
    
    # Load predictor
    print("\n1. Loading predictor...")
    start = time.time()
    try:
        pred = GamePredictor()
        elapsed = time.time() - start
        print(f"   [OK] Loaded in {elapsed:.2f}s")
    except Exception as e:
        print(f"   [ERROR] Failed: {e}")
        return
    
    # Test prediction without injuries
    print("\n2. Testing prediction WITHOUT injuries...")
    start = time.time()
    try:
        result = pred.predict(
            home_team_id=1610612747,  # Lakers
            visitor_team_id=1610612738,  # Celtics
            game_date=datetime.now(),
            injury_data=None
        )
        elapsed = time.time() - start
        print(f"   ✓ Completed in {elapsed:.2f}s")
        print(f"   Home Win: {result['home_win_probability']:.2%}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"   ✗ Failed after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test prediction with injuries
    print("\n3. Testing prediction WITH injuries...")
    start = time.time()
    try:
        injury_data = {
            'home': {
                'key_players_available': 2,
                'star_player_available': 0
            },
            'visitor': {
                'key_players_available': 3,
                'star_player_available': 1
            }
        }
        result = pred.predict(
            home_team_id=1610612747,  # Lakers
            visitor_team_id=1610612738,  # Celtics
            game_date=datetime.now(),
            injury_data=injury_data
        )
        elapsed = time.time() - start
        print(f"   ✓ Completed in {elapsed:.2f}s")
        print(f"   Home Win: {result['home_win_probability']:.2%}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"   ✗ Failed after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_prediction_with_timing()

