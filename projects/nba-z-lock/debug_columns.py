"""Debug column names in the API responses."""
from nba_api.stats.endpoints import commonteamroster, teamplayerdashboard

team_id = 1610612747
season = "2024-25"

print("Getting roster...")
roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
roster_df = roster.get_data_frames()[0]
print(f"Roster columns: {list(roster_df.columns)}")
print(f"Roster shape: {roster_df.shape}")
if len(roster_df) > 0:
    print(f"First row:\n{roster_df.iloc[0]}")

print("\n\nGetting dashboard...")
dashboard = teamplayerdashboard.TeamPlayerDashboard(
    team_id=team_id,
    season=season,
    season_type_all_star="Regular Season"
)
stats_df = dashboard.get_data_frames()[0]
print(f"Stats columns: {list(stats_df.columns)}")
print(f"Stats shape: {stats_df.shape}")
if len(stats_df) > 0:
    print(f"First row:\n{stats_df.iloc[0]}")

