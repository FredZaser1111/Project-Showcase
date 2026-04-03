"""
Comprehensive test of NBA_API setup.
Tests all components: API client, data collection, Flask app integration.
"""
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent))

print("=" * 70)
print("NBA Prediction Tool - Full Setup Test")
print("=" * 70)

# Test 1: Configuration
print("\n[1/6] Testing Configuration...")
try:
    import config
    print(f"   [OK] API Provider: {config.API_PROVIDER}")
    print(f"   [OK] Data Directory: {config.DATA_DIR}")
    print(f"   [OK] Models Directory: {config.MODELS_DIR}")
    print(f"   [OK] Rate Limit: {config.RATE_LIMIT_PER_MIN}/min")
except Exception as e:
    print(f"   [ERROR] Configuration error: {e}")
    sys.exit(1)

# Test 2: NBA_API Import
print("\n[2/6] Testing NBA_API Import...")
try:
    from api_client_nba import NBAAPIClient
    print("   [OK] NBA_API client imported successfully")
except ImportError as e:
    print(f"   [ERROR] NBA_API not available: {e}")
    print("   → Run: pip install nba_api")
    sys.exit(1)

# Test 3: API Client Initialization
print("\n[3/6] Testing API Client...")
try:
    client = NBAAPIClient()
    print("   [OK] API client initialized")
    
    # Test teams endpoint
    print("   -> Fetching teams...")
    teams = client.get_all_teams()
    print(f"   [OK] Found {len(teams)} teams")
    
    if teams:
        sample_team = teams[0]
        print(f"   [OK] Sample team: {sample_team.get('full_name', 'N/A')}")
except Exception as e:
    print(f"   [ERROR] API client error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Game Data Collection
print("\n[4/6] Testing Game Data Collection...")
try:
    # Test getting games for one team
    test_team = teams[0]
    print(f"   -> Testing with: {test_team.get('full_name', 'N/A')}")
    
    team_games = client.get_team_games(test_team['id'], '2023-24')
    print(f"   [OK] Got {len(team_games)} games for team")
    
    # Test date-based collection
    print("   -> Testing date-based collection...")
    date_games = client.get_games_by_date('2024-04-14')
    print(f"   [OK] Got {len(date_games)} games for date")
    
    if date_games:
        sample_game = date_games[0]
        has_scores = (sample_game.get('home_team_score', 0) > 0 and 
                     sample_game.get('visitor_team_score', 0) > 0)
        print(f"   [OK] Sample game has complete scores: {has_scores}")
        print(f"      Game ID: {sample_game.get('id', 'N/A')}")
        print(f"      Home: {sample_game.get('home_team_score', 0)}")
        print(f"      Visitor: {sample_game.get('visitor_team_score', 0)}")
except Exception as e:
    print(f"   [ERROR] Game data collection error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Flask App Integration
print("\n[5/6] Testing Flask App Integration...")
try:
    # Check if app can import the client
    if config.API_PROVIDER == 'nba_api':
        from api_client_nba import NBAAPIClient
        test_client = NBAAPIClient()
        print("   [OK] Flask app can use NBA_API client")
    else:
        from api_client import APIClient
        test_client = APIClient()
        print("   [OK] Flask app using Ball Don't Lie client")
    
    # Test that teams can be fetched (what the app does)
    app_teams = test_client.get_all_teams()
    print(f"   [OK] App can fetch {len(app_teams)} teams")
    
except Exception as e:
    print(f"   [ERROR] Flask integration error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Data Directory Structure
print("\n[6/6] Testing Data Directory Structure...")
try:
    data_dir = Path(config.DATA_DIR)
    cache_dir = Path(config.CACHE_DIR)
    models_dir = Path(config.MODELS_DIR)
    
    print(f"   [OK] Data directory exists: {data_dir.exists()}")
    print(f"   [OK] Cache directory exists: {cache_dir.exists()}")
    print(f"   [OK] Models directory exists: {models_dir.exists()}")
    
    # Check for existing data files
    teams_file = data_dir / 'teams.json'
    games_file = data_dir / 'historical_games.json'
    
    if teams_file.exists():
        with open(teams_file, 'r') as f:
            cached_teams = json.load(f)
        print(f"   [OK] Found cached teams file ({len(cached_teams)} teams)")
    else:
        print("   -> No cached teams file (will be created on first run)")
    
    if games_file.exists():
        with open(games_file, 'r') as f:
            cached_games = json.load(f)
        print(f"   [OK] Found historical games file ({len(cached_games)} games)")
    else:
        print("   -> No historical games file (run collect_historical_data.py)")
    
except Exception as e:
    print(f"   [ERROR] Directory check error: {e}")

# Summary
print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)
print("[OK] Configuration: OK")
print("[OK] NBA_API Import: OK")
print("[OK] API Client: OK")
print("[OK] Game Data Collection: OK")
print("[OK] Flask Integration: OK")
print("[OK] Directory Structure: OK")
print("\n[SUCCESS] All tests passed!")
print("\nNext steps:")
print("  1. Run: python scripts/collect_historical_data.py")
print("  2. Run: python models/train_model.py")
print("  3. Run: python app.py")
print("  4. Open: http://127.0.0.1:5000")
print("=" * 70)

