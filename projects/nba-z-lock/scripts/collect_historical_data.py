"""
Collect historical NBA game data.
Works with both Ball Don't Lie API and NBA_API.
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
        APIClient = NBAAPIClient
    except ImportError:
        print("Warning: NBA_API not available, falling back to Ball Don't Lie API")
        from api_client import APIClient
else:
    from api_client import APIClient

def get_season_dates(season: int) -> tuple:
    """
    Get start and end dates for an NBA season.
    
    Args:
        season: Year the season starts (e.g., 2023 for 2023-24 season)
    
    Returns:
        (start_date, end_date) as strings
    """
    # NBA season typically runs from October to June
    start_date = f"{season}-10-01"
    end_date = f"{season + 1}-06-30"
    return start_date, end_date

def collect_season_data(client: APIClient, season: int, output_file: Path):
    """Collect all games for a specific season."""
    print(f"\nCollecting data for {season}-{season+1} season...")
    
    start_date, end_date = get_season_dates(season)
    
    # Generate list of dates (NBA games are typically Tue-Sun)
    # We'll collect by month to be more efficient
    all_games = []
    
    # Try to get games for the season
    try:
        games = client.get_all_games(seasons=[season])
        all_games.extend(games)
        print(f"  Collected {len(games)} games for {season}-{season+1}")
    except Exception as e:
        print(f"  Error collecting {season}-{season+1}: {e}")
    
    return all_games

def main():
    """Main data collection function."""
    print("=" * 60)
    print("NBA Historical Data Collection")
    print("=" * 60)
    print(f"API Provider: {config.API_PROVIDER}")
    if config.API_PROVIDER == 'balldontlie':
        print(f"API Tier: {config.API_TIER}")
        print(f"Rate Limit: {config.RATE_LIMIT_PER_MIN} requests/minute")
    else:
        print("API: NBA_API (Free, no API key needed)")
    print("=" * 60)
    
    # Initialize API client
    client = APIClient()
    
    # Get all teams first (for reference)
    print("\nFetching team list...")
    try:
        teams = client.get_all_teams()
        print(f"Found {len(teams)} teams")
        
        # Save teams data
        teams_file = Path(config.DATA_DIR) / 'teams.json'
        with open(teams_file, 'w') as f:
            json.dump(teams, f, indent=2)
        print(f"Saved teams to {teams_file}")
    except Exception as e:
        print(f"Error fetching teams: {e}")
        teams = []
    
    # Collect historical games
    # Collect last 3 seasons by default
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Determine current season
    if current_month >= 10:
        current_season = current_year
    else:
        current_season = current_year - 1
    
    # Collect 10+ seasons for Phase 1 improvement (target: 65% accuracy)
    # Collect last 10 seasons for better training
    seasons_to_collect = list(range(current_season - 9, current_season + 1))
    
    print(f"\nCollecting data for seasons: {seasons_to_collect}")
    
    all_games = []
    
    for season in seasons_to_collect:
        games = collect_season_data(client, season, Path(config.DATA_DIR))
        all_games.extend(games)
        time.sleep(1)  # Brief pause between seasons
    
    # Remove duplicates (games might appear in multiple queries)
    seen_ids = set()
    unique_games = []
    for game in all_games:
        game_id = game.get('id')
        if game_id and game_id not in seen_ids:
            seen_ids.add(game_id)
            unique_games.append(game)
    
    print(f"\nTotal unique games collected: {len(unique_games)}")
    
    # Save to file
    output_file = Path(config.DATA_DIR) / 'historical_games.json'
    with open(output_file, 'w') as f:
        json.dump(unique_games, f, indent=2)
    
    print(f"Saved games to {output_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Collection Summary:")
    print(f"  Total games: {len(unique_games)}")
    print(f"  Teams: {len(teams)}")
    print(f"  Seasons: {seasons_to_collect}")
    print("=" * 60)
    
    print("\nData collection complete!")
    print("\nNext steps:")
    print("  1. Review the collected data")
    print("  2. Run: python models/train_model.py")

if __name__ == '__main__':
    main()

