"""
NBA_API client adapter - uses python-nba-api library.
Replaces Ball Don't Lie API with free NBA.com data.
"""
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import deque

try:
    from nba_api.stats.endpoints import commonteamroster, teamgamelog
    from nba_api.stats.static import teams
    # Scoreboard may not be available in all versions
    try:
        from nba_api.stats.endpoints import scoreboardv2 as scoreboard
    except ImportError:
        try:
            from nba_api.stats.endpoints import scoreboard
        except ImportError:
            scoreboard = None
    NBA_API_AVAILABLE = True
except ImportError as e:
    NBA_API_AVAILABLE = False
    print(f"Warning: nba_api not installed. Run: pip install nba_api. Error: {e}")

import config

class RateLimiter:
    """Rate limiter for NBA_API (respects NBA.com rate limits)."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.request_times = deque()
    
    def wait_if_needed(self):
        """Wait if we've exceeded the rate limit."""
        now = time.time()
        
        # Remove requests older than 1 minute
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()
        
        # If we're at the limit, wait
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0]) + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)
                now = time.time()
                while self.request_times and now - self.request_times[0] > 60:
                    self.request_times.popleft()
        
        self.request_times.append(time.time())

class NBAAPIClient:
    """Client for NBA_API (python-nba-api library)."""
    
    def __init__(self, rate_limit: int = 60):
        if not NBA_API_AVAILABLE:
            raise ImportError("nba_api library not installed. Run: pip install nba_api")
        
        self.rate_limiter = RateLimiter(rate_limit)
        self.cache_dir = Path(config.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=24)
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Generate cache file path."""
        cache_key = cache_key.replace('/', '_').replace('?', '_')
        return self.cache_dir / f"nba_api_{cache_key}.json"
    
    def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load data from cache if not expired."""
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cached_data.get('cached_at', ''))
            if datetime.now() - cache_time > self.cache_ttl:
                return None
            
            return cached_data.get('data')
        except Exception:
            return None
    
    def _save_to_cache(self, cache_path: Path, data: Dict):
        """Save data to cache."""
        try:
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception:
            pass
    
    def get_all_teams(self) -> List[Dict]:
        """
        Get all NBA teams.
        Returns list in format compatible with existing code.
        """
        cache_path = self._get_cache_path('teams')
        cached = self._load_from_cache(cache_path)
        if cached:
            return cached
        
        self.rate_limiter.wait_if_needed()
        
        try:
            # Get teams from NBA_API
            nba_teams = teams.get_teams()
            
            # Convert to format compatible with existing code
            teams_list = []
            for team in nba_teams:
                # NBA_API structure: id, full_name, abbreviation, nickname, city, state, year_founded
                team_name = team.get('nickname', team.get('name', ''))
                city = team.get('city', '')
                full_name = team.get('full_name', f"{city} {team_name}".strip())
                
                teams_list.append({
                    'id': team['id'],
                    'abbreviation': team.get('abbreviation', ''),
                    'city': city,
                    'conference': team.get('conference', ''),
                    'division': team.get('division', ''),
                    'full_name': full_name,
                    'name': team_name
                })
            
            self._save_to_cache(cache_path, teams_list)
            return teams_list
        except Exception as e:
            raise Exception(f"Failed to fetch teams from NBA_API: {str(e)}")
    
    def get_team_games(self, team_id: int, season: str = None) -> List[Dict]:
        """
        Get games for a specific team.
        Returns games in format compatible with feature engineering.
        
        Args:
            team_id: NBA team ID
            season: Season string (e.g., '2023-24')
        
        Returns:
            List of game dictionaries with home_team, visitor_team, scores
        """
        if season is None:
            # Default to current season
            current_year = datetime.now().year
            if datetime.now().month >= 10:
                season = f"{current_year}-{str(current_year + 1)[2:]}"
            else:
                season = f"{current_year - 1}-{str(current_year)[2:]}"
        
        cache_path = self._get_cache_path(f'team_{team_id}_games_{season}')
        cached = self._load_from_cache(cache_path)
        if cached:
            return cached
        
        self.rate_limiter.wait_if_needed()
        
        try:
            # Get team game log
            game_log = teamgamelog.TeamGameLog(
                team_id=team_id,
                season=season
            )
            df = game_log.get_data_frames()[0]
            
            # Convert to list of dicts in format expected by feature engineering
            games = []
            for _, row in df.iterrows():
                matchup = row.get('MATCHUP', '')
                is_home = 'vs.' in matchup or 'VS.' in matchup
                is_away = '@' in matchup
                
                # Parse opponent from matchup (e.g., "ATL @ IND" or "ATL vs. IND")
                if is_away:
                    opponent_abbr = matchup.split('@')[1].strip()
                else:
                    opponent_abbr = matchup.split('vs.')[1].strip() if 'vs.' in matchup else matchup.split('VS.')[1].strip()
                
                # Find opponent team ID
                from nba_api.stats.static import teams
                all_teams = teams.get_teams()
                opponent_team = next((t for t in all_teams if t['abbreviation'] == opponent_abbr), None)
                opponent_id = opponent_team['id'] if opponent_team else None
                
                # Parse date (format: "APR 14, 2024")
                try:
                    date_str = row.get('GAME_DATE', '')
                    game_date = datetime.strptime(date_str, '%b %d, %Y')
                    date_iso = game_date.strftime('%Y-%m-%d')
                except:
                    date_iso = date_str
                
                # Create game dict in expected format
                if is_home:
                    game_dict = {
                        'id': row.get('Game_ID', ''),
                        'date': date_iso,
                        'home_team': {'id': team_id},
                        'visitor_team': {'id': opponent_id} if opponent_id else None,
                        'home_team_id': team_id,
                        'visitor_team_id': opponent_id,
                        'home_team_score': row.get('PTS', 0),
                        'visitor_team_score': 0  # Will need to get from opponent's log
                    }
                else:
                    game_dict = {
                        'id': row.get('Game_ID', ''),
                        'date': date_iso,
                        'home_team': {'id': opponent_id} if opponent_id else None,
                        'visitor_team': {'id': team_id},
                        'home_team_id': opponent_id,
                        'visitor_team_id': team_id,
                        'home_team_score': 0,  # Will need to get from opponent's log
                        'visitor_team_score': row.get('PTS', 0)
                    }
                
                if opponent_id:  # Only add if we found opponent
                    games.append(game_dict)
            
            self._save_to_cache(cache_path, games)
            return games
        except Exception as e:
            raise Exception(f"Failed to fetch team games: {str(e)}")
    
    def get_games_by_date(self, game_date: str) -> List[Dict]:
        """
        Get games for a specific date using scoreboard.
        
        Args:
            game_date: Date in YYYY-MM-DD format
        
        Returns:
            List of game dictionaries in format compatible with feature engineering
        """
        cache_path = self._get_cache_path(f'games_{game_date}')
        cached = self._load_from_cache(cache_path)
        if cached:
            return cached
        
        self.rate_limiter.wait_if_needed()
        
        try:
            # Parse date
            date_obj = datetime.strptime(game_date, '%Y-%m-%d')
            date_str = date_obj.strftime('%m/%d/%Y')
            
            # Get scoreboard for that date
            if scoreboard is None:
                from nba_api.stats.endpoints import scoreboardv2
                scoreboard_data = scoreboardv2.ScoreboardV2(game_date=date_str)
            else:
                # Check if it's ScoreboardV2 or Scoreboard
                if hasattr(scoreboard, 'ScoreboardV2'):
                    scoreboard_data = scoreboard.ScoreboardV2(game_date=date_str)
                elif hasattr(scoreboard, 'Scoreboard'):
                    scoreboard_data = scoreboard.Scoreboard(game_date=date_str)
                else:
                    # Try direct import
                    from nba_api.stats.endpoints import scoreboardv2
                    scoreboard_data = scoreboardv2.ScoreboardV2(game_date=date_str)
            
            dfs = scoreboard_data.get_data_frames()
            if not dfs or len(dfs) == 0:
                return []
            
            # First dataframe has game headers, second has line scores
            game_header_df = dfs[0]
            line_score_df = dfs[1] if len(dfs) > 1 else None
            
            games = []
            for _, game_row in game_header_df.iterrows():
                game_id = game_row.get('GAME_ID', '')
                home_team_id = game_row.get('HOME_TEAM_ID', 0)
                visitor_team_id = game_row.get('VISITOR_TEAM_ID', 0)
                
                # Get scores from line score if available
                home_score = 0
                visitor_score = 0
                
                if line_score_df is not None:
                    # Find scores for this game
                    game_scores = line_score_df[line_score_df['GAME_ID'] == game_id]
                    if len(game_scores) > 0:
                        # Line score has PTS column, need to match to home/visitor
                        for _, score_row in game_scores.iterrows():
                            team_id = score_row.get('TEAM_ID', 0)
                            pts = score_row.get('PTS', 0)
                            if team_id == home_team_id:
                                home_score = pts
                            elif team_id == visitor_team_id:
                                visitor_score = pts
                
                # Convert date
                date_est = game_row.get('GAME_DATE_EST', game_date)
                try:
                    if isinstance(date_est, str):
                        date_parsed = datetime.strptime(date_est.split('T')[0], '%Y-%m-%d')
                    else:
                        date_parsed = date_obj
                    date_iso = date_parsed.strftime('%Y-%m-%d')
                except:
                    date_iso = game_date
                
                games.append({
                    'id': game_id,
                    'date': date_iso,
                    'home_team': {'id': home_team_id},
                    'visitor_team': {'id': visitor_team_id},
                    'home_team_id': home_team_id,
                    'visitor_team_id': visitor_team_id,
                    'home_team_score': home_score,
                    'visitor_team_score': visitor_score
                })
            
            self._save_to_cache(cache_path, games)
            return games
        except Exception as e:
            raise Exception(f"Failed to fetch games for date {game_date}: {str(e)}")
    
    def get_all_games(self, seasons: List[int] = None) -> List[Dict]:
        """
        Get all games for specified seasons.
        Uses team game logs and matches them up to get complete game data.
        
        Args:
            seasons: List of season years (e.g., [2023, 2024])
        
        Returns:
            List of all game dictionaries with complete scores
        """
        all_games = []
        
        if seasons is None:
            # Default to last 3 seasons
            current_year = datetime.now().year
            seasons = [current_year - 2, current_year - 1, current_year]
        
        # Get all teams first
        teams_list = self.get_all_teams()
        
        # Dictionary to store games by game_id for matching scores
        games_by_id = {}
        
        for season_year in seasons:
            # Convert to NBA season format (e.g., 2023 -> "2023-24")
            season_str = f"{season_year}-{str(season_year + 1)[2:]}"
            
            print(f"Collecting games for {season_str} season...")
            
            for team in teams_list:
                try:
                    self.rate_limiter.wait_if_needed()
                    team_games = self.get_team_games(team['id'], season_str)
                    
                    # Process games and match up scores
                    for game in team_games:
                        game_id = game.get('id')
                        if not game_id:
                            continue
                        
                        if game_id not in games_by_id:
                            games_by_id[game_id] = game.copy()
                        else:
                            # Match up scores from both teams' game logs
                            existing_game = games_by_id[game_id]
                            
                            # If we have a score for this team, update the appropriate field
                            team_score = game.get('home_team_score', 0) or game.get('visitor_team_score', 0)
                            
                            if game.get('home_team_id') == existing_game.get('home_team_id'):
                                # Same home team, update home score
                                if team_score > 0:
                                    existing_game['home_team_score'] = team_score
                            elif game.get('visitor_team_id') == existing_game.get('visitor_team_id'):
                                # Same visitor team, update visitor score
                                if team_score > 0:
                                    existing_game['visitor_team_score'] = team_score
                            else:
                                # Different perspective - need to swap
                                if game.get('home_team_id') == existing_game.get('visitor_team_id'):
                                    # This team was visitor in existing, home in new
                                    if team_score > 0:
                                        existing_game['visitor_team_score'] = team_score
                                elif game.get('visitor_team_id') == existing_game.get('home_team_id'):
                                    # This team was home in existing, visitor in new
                                    if team_score > 0:
                                        existing_game['home_team_score'] = team_score
                    
                    time.sleep(0.1)  # Small delay to respect rate limits
                except Exception as e:
                    print(f"Error fetching games for {team['full_name']} {season_str}: {e}")
                    continue
        
        # Convert to list and filter out incomplete games
        unique_games = []
        for game_id, game in games_by_id.items():
            # Only include games with both scores
            if game.get('home_team_score', 0) > 0 and game.get('visitor_team_score', 0) > 0:
                unique_games.append(game)
        
        print(f"Collected {len(unique_games)} complete games")
        return unique_games

# Alias for compatibility
APIClient = NBAAPIClient

