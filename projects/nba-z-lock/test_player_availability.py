"""Test player availability tracking."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from player_availability import PlayerAvailabilityTracker
from nba_api.stats.static import teams

print("Testing Player Availability Tracker...")
tracker = PlayerAvailabilityTracker()
test_team = teams.get_teams()[0]

print(f"\nTesting with: {test_team['full_name']}")
players = tracker.get_team_key_players(test_team['id'], '2023-24')
print(f"Key players found: {len(players)}")
for p in players:
    print(f"  - {p['player_name']} (ID: {p['player_id']})")

print("\n[OK] Player availability tracker working!")

