"""
Helper script to identify star and key players for a team.
Uses NBA_API to fetch roster and stats, then suggests classifications.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from nba_api.stats.endpoints import commonteamroster, teamplayerdashboard
    from nba_api.stats.static import teams
    from nba_api.stats.endpoints import playergamelog
    import pandas as pd
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False
    print("Error: nba_api not installed. Install with: pip install nba_api")

def get_team_id(team_name: str) -> int:
    """Get team ID from team name."""
    nba_teams = teams.get_teams()
    for team in nba_teams:
        if team_name.lower() in team['full_name'].lower() or \
           team_name.lower() in team['nickname'].lower() or \
           team_name.lower() in team['abbreviation'].lower():
            return team['id']
    return None

def get_team_players(team_id: int, season: str = None):
    """Get team roster with basic stats."""
    if not NBA_API_AVAILABLE:
        return None
    
    try:
        # Get roster
        roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
        roster_df = roster.get_data_frames()[0]
        
        # Get team player dashboard for stats
        dashboard = teamplayerdashboard.TeamPlayerDashboard(
            team_id=team_id,
            season=season or "2024-25",
            season_type_all_star="Regular Season"
        )
        stats_df = dashboard.get_data_frames()[0]
        
        # Merge roster with stats
        merged = pd.merge(
            roster_df[['PLAYER_ID', 'PLAYER', 'POSITION', 'AGE']],
            stats_df[['PLAYER_ID', 'GP', 'MIN', 'PTS', 'USG_PCT']],
            on='PLAYER_ID',
            how='left'
        )
        
        # Fill NaN values
        merged = merged.fillna(0)
        
        # Sort by points (descending)
        merged = merged.sort_values('PTS', ascending=False)
        
        return merged
    except Exception as e:
        print(f"Error fetching team data: {e}")
        return None

def classify_players(players_df):
    """Classify players into star, key, and role categories."""
    if players_df is None or len(players_df) == 0:
        return None
    
    classifications = {
        'star': None,
        'key': [],
        'role': []
    }
    
    # Filter active players (played at least 5 games)
    active = players_df[players_df['GP'] >= 5].copy()
    
    if len(active) == 0:
        return classifications
    
    # Star player: Highest PPG, usually 20+ PPG, highest usage
    star_candidates = active[active['PTS'] >= 15].copy()
    if len(star_candidates) > 0:
        star = star_candidates.iloc[0]
        classifications['star'] = {
            'name': star['PLAYER'],
            'position': star['POSITION'],
            'ppg': round(star['PTS'], 1),
            'mpg': round(star['MIN'] / star['GP'] if star['GP'] > 0 else 0, 1),
            'usage': round(star['USG_PCT'] * 100, 1) if pd.notna(star['USG_PCT']) else 0
        }
    
    # Key players: Next 2-3 players by PPG/MPG (excluding star)
    remaining = active[active['PLAYER'] != classifications['star']['name']].copy() if classifications['star'] else active.copy()
    
    # Sort by combination of PPG and MPG
    remaining['score'] = remaining['PTS'] * 0.6 + (remaining['MIN'] / remaining['GP'] if remaining['GP'].max() > 0 else 0) * 0.4
    remaining = remaining.sort_values('score', ascending=False)
    
    # Top 2-3 are key players
    key_players = remaining.head(3)
    for _, player in key_players.iterrows():
        if player['MIN'] / player['GP'] >= 15:  # At least 15 MPG
            classifications['key'].append({
                'name': player['PLAYER'],
                'position': player['POSITION'],
                'ppg': round(player['PTS'], 1),
                'mpg': round(player['MIN'] / player['GP'] if player['GP'] > 0 else 0, 1),
                'usage': round(player['USG_PCT'] * 100, 1) if pd.notna(player['USG_PCT']) else 0
            })
    
    # Role players: Everyone else
    role_players = remaining.iloc[3:]
    for _, player in role_players.iterrows():
        classifications['role'].append({
            'name': player['PLAYER'],
            'position': player['POSITION'],
            'ppg': round(player['PTS'], 1),
            'mpg': round(player['MIN'] / player['GP'] if player['GP'] > 0 else 0, 1)
        })
    
    return classifications

def print_classifications(team_name: str, classifications):
    """Print player classifications in a readable format."""
    print("\n" + "=" * 60)
    print(f"PLAYER CLASSIFICATION: {team_name.upper()}")
    print("=" * 60)
    
    if not classifications:
        print("No data available.")
        return
    
    # Star Player
    if classifications['star']:
        star = classifications['star']
        print(f"\n🌟 STAR PLAYER:")
        print(f"   {star['name']} ({star['position']})")
        print(f"   {star['ppg']} PPG | {star['mpg']} MPG | {star['usage']}% Usage")
    else:
        print("\n🌟 STAR PLAYER: Not identified (may need more data)")
    
    # Key Players
    if classifications['key']:
        print(f"\n🔑 KEY PLAYERS ({len(classifications['key'])}):")
        for i, player in enumerate(classifications['key'], 1):
            print(f"   {i}. {player['name']} ({player['position']})")
            print(f"      {player['ppg']} PPG | {player['mpg']} MPG | {player['usage']}% Usage")
    else:
        print("\n🔑 KEY PLAYERS: None identified")
    
    # Role Players (show top 5)
    if classifications['role']:
        print(f"\n👥 ROLE PLAYERS (showing top 5 of {len(classifications['role'])}):")
        for i, player in enumerate(classifications['role'][:5], 1):
            print(f"   {i}. {player['name']} ({player['position']}) - {player['ppg']} PPG, {player['mpg']} MPG")
    
    # Summary for UI
    print("\n" + "-" * 60)
    print("FOR MANUAL INJURY INPUT:")
    print("-" * 60)
    if classifications['star']:
        print(f"   Star Player: {classifications['star']['name']}")
    print(f"   Key Players Count: {len(classifications['key'])}")
    print(f"   (Set 'Key Players Available' to 0-{len(classifications['key'])})")
    print("\n" + "=" * 60)

def main():
    """Main function."""
    if not NBA_API_AVAILABLE:
        print("NBA_API not available. Please install: pip install nba_api")
        return
    
    if len(sys.argv) < 2:
        print("Usage: python identify_team_players.py <team_name> [season]")
        print("\nExample:")
        print("  python identify_team_players.py Lakers")
        print("  python identify_team_players.py Warriors 2024-25")
        print("\nTeam name can be:")
        print("  - Full name: 'Los Angeles Lakers'")
        print("  - Nickname: 'Lakers'")
        print("  - Abbreviation: 'LAL'")
        return
    
    team_name = sys.argv[1]
    season = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Get team ID
    team_id = get_team_id(team_name)
    if not team_id:
        print(f"Error: Team '{team_name}' not found.")
        print("Try: Lakers, Warriors, Celtics, Nuggets, etc.")
        return
    
    # Get team info
    nba_teams = teams.get_teams()
    team_info = next((t for t in nba_teams if t['id'] == team_id), None)
    team_full_name = team_info['full_name'] if team_info else team_name
    
    print(f"\nFetching data for {team_full_name}...")
    if season:
        print(f"Season: {season}")
    else:
        print("Season: Current (2024-25)")
    
    # Get players
    players_df = get_team_players(team_id, season)
    if players_df is None:
        print("Error: Could not fetch team data.")
        return
    
    # Classify players
    classifications = classify_players(players_df)
    
    # Print results
    print_classifications(team_full_name, classifications)

if __name__ == '__main__':
    main()

