"""
Generate SAMPLE historical NBA game data for local development.

The real data comes from stats.nba.com via nba_api, which is not reachable from
some environments (e.g. cloud CI/dev VMs). This script produces data in the
exact same schema as api_client_nba.get_all_games / collect_historical_data.py
so the model can be trained and the app exercised end-to-end offline.

Output:
  data/teams.json             (real static team list from nba_api)
  data/historical_games.json  (synthetic games with realistic scores)
"""
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.append(str(Path(__file__).parent.parent))
import config
from nba_api.stats.static import teams as static_teams

random.seed(42)

DATA_DIR = Path(config.DATA_DIR)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_teams():
    teams_list = []
    for t in static_teams.get_teams():
        teams_list.append({
            'id': t['id'],
            'abbreviation': t.get('abbreviation', ''),
            'city': t.get('city', ''),
            'conference': t.get('conference', ''),
            'division': t.get('division', ''),
            'full_name': t.get('full_name', ''),
            'name': t.get('nickname', ''),
        })
    return teams_list


def simulate_season(teams_list, season_start_year, strengths):
    """Round-robin-ish schedule; each pair plays twice (home/away)."""
    games = []
    season_start = datetime(season_start_year, 10, 20)
    gid = season_start_year * 100000
    ids = [t['id'] for t in teams_list]
    day_offset = 0
    for i, home in enumerate(ids):
        for j, away in enumerate(ids):
            if home == away:
                continue
            # Skill-based expected scoring with noise
            hs = strengths[home]
            as_ = strengths[away]
            home_score = int(random.gauss(108 + (hs - as_) * 8 + 3, 9))   # +3 home court
            away_score = int(random.gauss(108 + (as_ - hs) * 8, 9))
            home_score = max(85, min(145, home_score))
            away_score = max(85, min(145, away_score))
            if home_score == away_score:
                home_score += 1
            date = season_start + timedelta(days=day_offset % 170)
            day_offset += 1
            gid += 1
            games.append({
                'id': f"{gid}",
                'date': date.strftime('%Y-%m-%d'),
                'home_team': {'id': home},
                'visitor_team': {'id': away},
                'home_team_id': home,
                'visitor_team_id': away,
                'home_team_score': home_score,
                'visitor_team_score': away_score,
            })
    return games


def main():
    teams_list = build_teams()
    (DATA_DIR / 'teams.json').write_text(json.dumps(teams_list, indent=2))
    print(f"Wrote {len(teams_list)} teams -> data/teams.json")

    # Stable per-team latent strength in [0,1]
    strengths = {t['id']: random.uniform(0.30, 0.70) for t in teams_list}

    current_year = datetime.now().year
    all_games = []
    # Generate the last 4 completed seasons
    for yr in range(current_year - 4, current_year):
        all_games.extend(simulate_season(teams_list, yr, strengths))

    (DATA_DIR / 'historical_games.json').write_text(json.dumps(all_games, indent=2))
    print(f"Wrote {len(all_games)} games -> data/historical_games.json")


if __name__ == '__main__':
    main()
