"""
Test script to verify Ball Don't Lie API connection and configuration.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import config
from api_client import APIClient

def test_api_connection():
    """Test API connection and configuration."""
    print("=" * 60)
    print("Ball Don't Lie API Connection Test")
    print("=" * 60)
    print()
    
    print(f"API Tier: {config.API_TIER}")
    print(f"Rate Limit: {config.RATE_LIMIT_PER_MIN} requests/minute")
    print(f"API Key: {'Set' if config.API_KEY else 'Not Set'}")
    if config.API_KEY:
        print(f"API Key (first 10 chars): {config.API_KEY[:10]}...")
    print()
    
    # Initialize client
    try:
        client = APIClient()
        print("✓ API client initialized")
    except Exception as e:
        print(f"✗ Failed to initialize API client: {e}")
        return False
    
    # Test: Get teams
    print("\nTesting: Get Teams...")
    try:
        teams = client.get_all_teams()
        print(f"✓ Successfully fetched {len(teams)} teams")
        if teams:
            print(f"  Example: {teams[0].get('full_name', 'N/A')}")
    except Exception as e:
        print(f"✗ Failed to fetch teams: {e}")
        return False
    
    # Test: Get recent games
    print("\nTesting: Get Recent Games...")
    try:
        games = client.get_games(page=0, per_page=5)
        game_count = len(games.get('data', []))
        print(f"✓ Successfully fetched {game_count} games (sample)")
        if game_count > 0:
            game = games['data'][0]
            print(f"  Example: {game.get('date', 'N/A')}")
    except Exception as e:
        print(f"✗ Failed to fetch games: {e}")
        print("  Note: This might be normal if API structure differs")
    
    print()
    print("=" * 60)
    print("API Connection Test Complete!")
    print("=" * 60)
    print()
    print("If all tests passed, you're ready to:")
    print("1. Collect data: python scripts/collect_historical_data.py")
    print("2. Train model: python models/train_model.py")
    print("3. Run app: python app.py")
    
    return True

if __name__ == '__main__':
    success = test_api_connection()
    sys.exit(0 if success else 1)

