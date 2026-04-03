"""
Collect recent games from a date range.
Quick script to collect games since last training.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import config

# Choose API client based on config
if config.API_PROVIDER == 'nba_api':
    try:
        from api_client_nba import NBAAPIClient
        client = NBAAPIClient()
    except ImportError:
        print("Warning: NBA_API not available, falling back to Ball Don't Lie API")
        from api_client import APIClient
        client = APIClient()
else:
    from api_client import APIClient
    client = APIClient()

def collect_games_since(since_date: datetime):
    """Collect games from since_date to today."""
    today = datetime.now()
    current_date = since_date
    
    all_games = []
    dates_to_check = []
    
    # Generate list of dates to check
    while current_date <= today:
        dates_to_check.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    print(f"Collecting games from {since_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")
    print(f"Checking {len(dates_to_check)} dates...")
    
    # Check if client has get_games_by_date method
    if hasattr(client, 'get_games_by_date'):
        print("\nUsing date-by-date collection (NBA_API)...")
        for date_str in dates_to_check:
            try:
                games = client.get_games_by_date(date_str)
                if games:
                    print(f"  {date_str}: {len(games)} games")
                    all_games.extend(games)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"  {date_str}: Error - {e}")
                continue
    else:
        # Fallback: get games for current season and filter
        print("\nUsing season-based collection (will filter by date)...")
        current_year = datetime.now().year
        if datetime.now().month >= 10:
            current_season = current_year
        else:
            current_season = current_year - 1
        
        try:
            games = client.get_all_games(seasons=[current_season])
            print(f"  Collected {len(games)} games for {current_season} season")
            
            # Filter to only games after since_date
            for game in games:
                game_date_str = game.get('date')
                if game_date_str:
                    try:
                        game_date = datetime.strptime(game_date_str, '%Y-%m-%d')
                        if game_date > since_date:
                            all_games.append(game)
                    except:
                        continue
        except Exception as e:
            print(f"Error collecting games: {e}")
    
    return all_games

def main():
    """Main function to collect recent games and merge with existing data."""
    print("=" * 60)
    print("Collect Recent Games")
    print("=" * 60)
    
    # Get last training date (default to Dec 13, 2025 if not found)
    results_file = Path(config.MODELS_DIR) / 'training_results.json'
    since_date = None
    
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
                if 'training_date' in results:
                    since_date = datetime.fromisoformat(results['training_date'])
                else:
                    # Use file modification time as proxy
                    since_date = datetime.fromtimestamp(results_file.stat().st_mtime)
        except:
            pass
    
    if since_date is None:
        # Default to December 13, 2025
        since_date = datetime(2025, 12, 13)
        print(f"No training date found, defaulting to: {since_date.strftime('%Y-%m-%d')}")
    else:
        print(f"Collecting games since: {since_date.strftime('%Y-%m-%d')}")
    
    # Collect new games
    new_games = collect_games_since(since_date)
    print(f"\nCollected {len(new_games)} new games")
    
    if len(new_games) == 0:
        print("\nNo new games found. They may already be in historical_games.json")
        return
    
    # Load existing games
    games_file = Path(config.DATA_DIR) / 'historical_games.json'
    existing_games = []
    existing_game_ids = set()
    
    if games_file.exists():
        with open(games_file, 'r') as f:
            existing_games = json.load(f)
            existing_game_ids = {g.get('id') for g in existing_games if g.get('id')}
        print(f"\nExisting games in file: {len(existing_games)}")
    else:
        print("\nNo existing games file found - creating new one")
    
    # Merge: add new games that aren't already there
    added_count = 0
    for game in new_games:
        game_id = game.get('id')
        if game_id and game_id not in existing_game_ids:
            existing_games.append(game)
            existing_game_ids.add(game_id)
            added_count += 1
    
    print(f"\nAdding {added_count} new games to historical_games.json")
    print(f"Total games after merge: {len(existing_games)}")
    
    # Save updated games file
    with open(games_file, 'w') as f:
        json.dump(existing_games, f, indent=2)
    
    print(f"\nSaved updated games to {games_file}")
    print("\nDone! You can now run: python models/train_incremental.py")

if __name__ == '__main__':
    main()

