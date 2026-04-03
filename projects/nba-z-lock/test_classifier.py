"""Test player classifier to debug the issue."""
from player_classifier import PlayerClassifier
import traceback

classifier = PlayerClassifier()

# Test with Lakers
team_id = 1610612747
season = "2024-25"

print(f"Testing classifier for team {team_id}, season {season}...")

try:
    # Get players with stats
    players_df = classifier.get_team_players_with_stats(team_id, season)
    print(f"\nPlayers DataFrame shape: {players_df.shape}")
    
    if len(players_df) > 0:
        print(f"Columns: {list(players_df.columns)}")
        print(f"\nFirst few players:")
        print(players_df[['PLAYER', 'GP', 'PPG', 'MPG', 'USG_PCT']].head())
        
        # Check active players
        active = players_df[players_df['GP'] >= 5]
        print(f"\nActive players (GP >= 5): {len(active)}")
        
        if len(active) == 0:
            print("\nWARNING: No players with 5+ games. Trying with 1+ games...")
            active = players_df[players_df['GP'] >= 1]
            print(f"Active players (GP >= 1): {len(active)}")
    else:
        print("ERROR: No players returned!")
    
    # Test classification
    print("\n\nTesting classification...")
    classifications = classifier.classify_players(team_id, season)
    print(f"Star players: {len(classifications['star'])}")
    print(f"Key players: {len(classifications['key'])}")
    print(f"Role players: {len(classifications['role'])}")
    
    if classifications['star']:
        print(f"\nStar: {classifications['star'][0]['name']}")
    if classifications['key']:
        print(f"Key: {[p['name'] for p in classifications['key']]}")
    
    # Test roster method
    print("\n\nTesting get_classification_for_roster...")
    roster = classifier.get_classification_for_roster(team_id, season)
    print(f"Total players in roster: {len(roster)}")
    if len(roster) > 0:
        print(f"First 5: {[p['name'] for p in roster[:5]]}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()

