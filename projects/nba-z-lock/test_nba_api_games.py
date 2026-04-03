"""
Test script to verify NBA_API game data collection.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api_client_nba import NBAAPIClient

def test_game_collection():
    """Test collecting games from NBA_API."""
    print("Testing NBA_API game collection...")
    
    client = NBAAPIClient()
    
    # Get teams
    print("\n1. Fetching teams...")
    teams = client.get_all_teams()
    print(f"   Found {len(teams)} teams")
    
    # Test getting games for one team
    print("\n2. Testing team game collection...")
    test_team = teams[0]  # First team
    print(f"   Testing with: {test_team['full_name']}")
    
    games = client.get_team_games(test_team['id'], '2023-24')
    print(f"   Got {len(games)} games")
    
    if games:
        sample = games[0]
        print(f"\n   Sample game structure:")
        print(f"   - Game ID: {sample.get('id')}")
        print(f"   - Date: {sample.get('date')}")
        print(f"   - Home Team ID: {sample.get('home_team_id')}")
        print(f"   - Visitor Team ID: {sample.get('visitor_team_id')}")
        print(f"   - Home Score: {sample.get('home_team_score')}")
        print(f"   - Visitor Score: {sample.get('visitor_team_score')}")
        print(f"   - All keys: {list(sample.keys())}")
    
    # Test getting games by date
    print("\n3. Testing date-based game collection...")
    test_date = '2024-04-14'
    date_games = client.get_games_by_date(test_date)
    print(f"   Got {len(date_games)} games for {test_date}")
    
    if date_games:
        sample = date_games[0]
        print(f"\n   Sample game from date query:")
        print(f"   - Game ID: {sample.get('id')}")
        print(f"   - Home Score: {sample.get('home_team_score')}")
        print(f"   - Visitor Score: {sample.get('visitor_team_score')}")
    
    print("\n[OK] Test complete!")

if __name__ == '__main__':
    test_game_collection()

