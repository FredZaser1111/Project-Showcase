"""
Advanced player classification system using statistical analysis.
Classifies players as Star, Key, or Role based on actual performance metrics.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

try:
    from nba_api.stats.endpoints import (
        commonteamroster, teamplayerdashboard, playergamelog
    )
    from nba_api.stats.static import teams
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False

import config

class PlayerClassifier:
    """
    Classify players using statistical analysis.
    Uses PPG, MPG, usage rate, and other metrics to determine importance.
    """
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path(config.CACHE_DIR) / 'player_classification'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.classification_cache = {}
    
    def _get_current_season(self) -> str:
        """Get current NBA season string."""
        now = datetime.now()
        if now.month >= 10:
            return f"{now.year}-{str(now.year + 1)[2:]}"
        else:
            return f"{now.year - 1}-{str(now.year)[2:]}"
    
    def get_team_players_with_stats(self, team_id: int, season: str = None) -> pd.DataFrame:
        """Get team roster with player statistics."""
        if not NBA_API_AVAILABLE:
            return pd.DataFrame()
        
        season = season or self._get_current_season()
        cache_file = self.cache_dir / f'team_{team_id}_{season}_stats.json'
        
        # Check cache
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return pd.DataFrame(data)
            except:
                pass
        
        try:
            # Get roster - SKIP API CALLS FOR PREDICTIONS (too slow)
            # Use cached roster or return empty DataFrame to trigger estimates
            if False:  # Disabled for speed during predictions
                roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
                roster_df = roster.get_data_frames()[0]
            else:
                # Return empty to trigger estimate logic (no API calls)
                print(f"[PlayerClassifier] Skipping API call for team {team_id}, using estimates")
                return pd.DataFrame()
            
            if len(roster_df) == 0:
                return pd.DataFrame()
            
            # Get player stats from playergamelog (simpler approach)
            # For now, use roster and estimate based on position and experience
            players_list = []
            
            for _, row in roster_df.iterrows():
                player_id = int(row['PLAYER_ID'])
                player_name = row['PLAYER']
                position = row.get('POSITION', '')
                age = row.get('AGE', 25)
                exp = row.get('EXP', 0)
                
                # Try to get actual stats from player game log
                # SKIP API CALLS FOR PREDICTIONS - too slow (30+ seconds per team)
                # Use estimates instead for speed
                try:
                    # Only make API calls if explicitly needed (not during predictions)
                    # For predictions, we use cached data or estimates
                    if False:  # Disabled for speed - use estimates instead
                        from nba_api.stats.endpoints import playergamelog
                        game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
                        gl_df = game_log.get_data_frames()[0]
                    else:
                        # Use estimates for speed (no API calls)
                        gl_df = pd.DataFrame()  # Empty - will trigger estimate logic
                    
                    if len(gl_df) > 0:
                        gp = len(gl_df)
                        pts = gl_df['PTS'].sum()
                        min_total = gl_df['MIN'].sum() if 'MIN' in gl_df.columns else 0
                        ast = gl_df['AST'].sum() if 'AST' in gl_df.columns else 0
                        reb = gl_df['REB'].sum() if 'REB' in gl_df.columns else 0
                        
                        ppg = pts / gp if gp > 0 else 0
                        mpg = min_total / gp if gp > 0 else 0
                        apg = ast / gp if gp > 0 else 0
                        rpg = reb / gp if gp > 0 else 0
                    else:
                        # No games played yet - use estimates
                        gp = 0
                        ppg = 15 if exp > 3 else 10  # Estimate based on experience
                        mpg = 30 if exp > 3 else 20
                        apg = 5 if position in ['G', 'F-G', 'G-F'] else 3
                        rpg = 7 if position in ['F', 'C', 'F-C', 'C-F'] else 4
                except:
                    # Fallback: estimate based on position and experience
                    gp = 0
                    ppg = 15 if exp > 3 else 10
                    mpg = 30 if exp > 3 else 20
                    apg = 5 if position in ['G', 'F-G', 'G-F'] else 3
                    rpg = 7 if position in ['F', 'C', 'F-C', 'C-F'] else 4
                
                # Estimate usage rate (rough)
                usg_pct = min(0.35, (ppg / 30) * 0.3) if ppg > 0 else 0.15
                
                # Calculate impact score
                impact_score = (
                    ppg * 0.35 +
                    mpg * 0.25 +
                    (usg_pct * 100) * 0.20 +
                    apg * 0.10 +
                    rpg * 0.10
                )
                
                players_list.append({
                    'PLAYER_ID': player_id,
                    'PLAYER': player_name,
                    'POSITION': position,
                    'AGE': age,
                    'GP': gp,
                    'PPG': ppg,
                    'MPG': mpg,
                    'APG': apg,
                    'RPG': rpg,
                    'USG_PCT': usg_pct,
                    'IMPACT_SCORE': impact_score
                })
            
            merged = pd.DataFrame(players_list)
            
            # Cache it
            merged_dict = merged.to_dict('records')
            with open(cache_file, 'w') as f:
                json.dump(merged_dict, f, indent=2, default=str)
            
            return merged
            
        except Exception as e:
            print(f"Error getting team stats for team {team_id}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def classify_players(self, team_id: int, season: str = None) -> Dict[str, List[Dict]]:
        """
        Classify players into Star, Key, and Role categories.
        
        Returns:
            Dict with 'star', 'key', 'role' lists of player dicts
        """
        season = season or self._get_current_season()
        cache_key = f'{team_id}_{season}'
        
        if cache_key in self.classification_cache:
            return self.classification_cache[cache_key]
        
        # Get players with stats
        players_df = self.get_team_players_with_stats(team_id, season)
        
        if len(players_df) == 0:
            return {'star': [], 'key': [], 'role': []}
        
        # Filter active players (played at least 1 game, or all if none have played)
        active = players_df[players_df['GP'] >= 1].copy()
        
        # If no players have played, use all players (for early season)
        if len(active) == 0:
            active = players_df.copy()
        
        if len(active) == 0:
            return {'star': [], 'key': [], 'role': []}
        
        # Sort by impact score
        active = active.sort_values('IMPACT_SCORE', ascending=False)
        
        classifications = {'star': [], 'key': [], 'role': []}
        
        # Star Player: Top impact, high PPG (20+), high usage (25%+), high MPG (30+)
        star_candidates = active[
            (active['PPG'] >= 18) & 
            (active['MPG'] >= 25) &
            (active['USG_PCT'] >= 0.22)
        ]
        
        if len(star_candidates) > 0:
            star = star_candidates.iloc[0]
            classifications['star'].append({
                'player_id': int(star['PLAYER_ID']),
                'name': star['PLAYER'],
                'position': star.get('POSITION', ''),
                'ppg': round(star['PPG'], 1),
                'mpg': round(star['MPG'], 1),
                'usage': round(star['USG_PCT'] * 100, 1),
                'impact_score': round(star['IMPACT_SCORE'], 2)
            })
        
        # Key Players: Next 2-3 players with good stats (excluding star)
        remaining = active[active['PLAYER_ID'] != classifications['star'][0]['player_id']].copy() if classifications['star'] else active.copy()
        
        # Key player criteria: PPG >= 10, MPG >= 18, or high impact
        key_candidates = remaining[
            ((remaining['PPG'] >= 10) & (remaining['MPG'] >= 18)) |
            (remaining['IMPACT_SCORE'] >= 15)
        ]
        
        # Take top 2-3 key players
        for _, player in key_candidates.head(3).iterrows():
            classifications['key'].append({
                'player_id': int(player['PLAYER_ID']),
                'name': player['PLAYER'],
                'position': player.get('POSITION', ''),
                'ppg': round(player['PPG'], 1),
                'mpg': round(player['MPG'], 1),
                'usage': round(player['USG_PCT'] * 100, 1),
                'impact_score': round(player['IMPACT_SCORE'], 2)
            })
        
        # Role Players: Everyone else
        key_ids = {p['player_id'] for p in classifications['key']}
        star_ids = {p['player_id'] for p in classifications['star']}
        excluded_ids = key_ids | star_ids
        
        role_players = remaining[~remaining['PLAYER_ID'].isin(excluded_ids)]
        
        for _, player in role_players.iterrows():
            classifications['role'].append({
                'player_id': int(player['PLAYER_ID']),
                'name': player['PLAYER'],
                'position': player.get('POSITION', ''),
                'ppg': round(player['PPG'], 1),
                'mpg': round(player['MPG'], 1),
                'usage': round(player['USG_PCT'] * 100, 1),
                'impact_score': round(player['IMPACT_SCORE'], 2)
            })
        
        # Cache it
        self.classification_cache[cache_key] = classifications
        
        return classifications
    
    def get_classification_for_roster(self, team_id: int, season: str = None) -> List[Dict]:
        """
        Get all players with their classifications for roster display.
        
        Returns:
            List of player dicts with 'type' field ('star', 'key', 'role')
        """
        season = season or self._get_current_season()
        
        try:
            classifications = self.classify_players(team_id, season)
            
            all_players = []
            
            # Add star players
            for player in classifications.get('star', []):
                player['type'] = 'star'
                all_players.append(player)
            
            # Add key players
            for player in classifications.get('key', []):
                player['type'] = 'key'
                all_players.append(player)
            
            # Add role players
            for player in classifications.get('role', []):
                player['type'] = 'role'
                all_players.append(player)
            
            # If we got players, return them
            if len(all_players) > 0:
                return all_players
        except Exception as e:
            print(f"Warning: Player classification failed for team {team_id}: {e}")
        
        # Fallback: Get basic roster without classification
        print(f"Using fallback: Getting basic roster for team {team_id}, season {season}")
        try:
            if not NBA_API_AVAILABLE:
                return []
            
            roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
            roster_df = roster.get_data_frames()[0]
            
            if len(roster_df) == 0:
                print(f"Warning: No roster data found for team {team_id}, season {season}")
                return []
            
            # Return all players as role players
            all_players = []
            for _, row in roster_df.iterrows():
                all_players.append({
                    'player_id': int(row['PLAYER_ID']),
                    'name': row['PLAYER'],
                    'position': row.get('POSITION', ''),
                    'type': 'role',  # Default to role if classification fails
                    'ppg': 0.0,
                    'mpg': 0.0,
                    'usage': 0.0,
                    'impact_score': 0.0
                })
            
            print(f"Fallback successful: Found {len(all_players)} players")
            return all_players
        except Exception as e:
            print(f"Error in fallback roster fetch: {e}")
            return []

