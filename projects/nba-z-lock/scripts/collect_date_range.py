"""
Quick script to collect games for a specific date range.
Collects games from Dec 13 to Dec 30, 2025.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import config

# Choose API client
if config.API_PROVIDER == 'nba_api':
    try:
        from api_client_nba import NBAAPIClient
        client = NBAAPIClient()
        print("Using NBA_API client")
    except ImportError:
        from api_client import APIClient
        client = APIClient()
        print("Using Ball Don't Lie API client")
else:
    from api_client import APIClient
    client = APIClient()

def main():
    # Allow command line arguments for dates, or use defaults
    import argparse
    parser = argparse.ArgumentParser(description='Collect NBA games for a date range')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)', default='2025-12-31')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)', default=None)
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        # Default to today if not specified
        end_date = datetime.now()
    
    print("=" * 60)
    print(f"Collecting games from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    all_new_games = []
    current_date = start_date
    
    # Check if client supports get_games_by_date
    if hasattr(client, 'get_games_by_date'):
        print("\nCollecting games day by day...")
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            try:
                print(f"Checking {date_str}...", end=" ", flush=True)
                games = client.get_games_by_date(date_str)
                if games:
                    print(f"Found {len(games)} games")
                    all_new_games.extend(games)
                else:
                    print("No games")
                time.sleep(0.6)  # Rate limiting
            except Exception as e:
                print(f"Error: {e}")
            current_date += timedelta(days=1)
    else:
        print("\nClient doesn't support get_games_by_date, using season-based collection...")
        # Fallback method
        try:
            current_year = 2025
            games = client.get_all_games(seasons=[2025])
            print(f"Collected {len(games)} games for 2025 season")
            
            # Filter to date range
            for game in games:
                game_date_str = game.get('date')
                if game_date_str:
                    try:
                        game_date = datetime.strptime(game_date_str, '%Y-%m-%d')
                        if start_date <= game_date <= end_date:
                            all_new_games.append(game)
                    except:
                        continue
        except Exception as e:
            print(f"Error: {e}")
            return
    
    print(f"\nCollected {len(all_new_games)} games total")
    
    if len(all_new_games) == 0:
        print("\nNo games found for this date range.")
        return
    
    # Load existing games
    games_file = Path(config.DATA_DIR) / 'historical_games.json'
    existing_games = []
    existing_game_ids = set()
    
    if games_file.exists():
        with open(games_file, 'r') as f:
            existing_games = json.load(f)
            existing_game_ids = {g.get('id') for g in existing_games if g.get('id')}
        print(f"\nExisting games: {len(existing_games)}")
    else:
        print("\nNo existing games file")
    
    # Add new games (avoid duplicates)
    added = 0
    for game in all_new_games:
        game_id = game.get('id')
        if game_id and game_id not in existing_game_ids:
            existing_games.append(game)
            existing_game_ids.add(game_id)
            added += 1
    
    print(f"Added {added} new games")
    print(f"Total games now: {len(existing_games)}")
    
    # Save
    with open(games_file, 'w') as f:
        json.dump(existing_games, f, indent=2)
    
    print(f"\nSaved to {games_file}")
    print("\nDone! Run: python models/train_incremental.py")

if __name__ == '__main__':
    main()

