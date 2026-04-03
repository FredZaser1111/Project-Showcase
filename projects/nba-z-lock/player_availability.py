"""
Player availability tracking using historical game logs.
Approximates injuries/rest by checking if key players played in recent games.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json
import time

try:
    from nba_api.stats.endpoints import commonteamroster, playergamelog, teamgamelog
    from nba_api.stats.static import teams
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False

import config

class PlayerAvailabilityTracker:
    """Track player availability using historical game logs."""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path(config.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.team_key_players_cache = {}
        self.player_availability_cache = {}
    
    def get_team_key_players(self, team_id: int, season: str = None) -> List[Dict]:
        """
        Identify key players for a team using improved classification.
        Now uses PlayerClassifier for accurate star/key player identification.
        
        Returns:
            List of player dicts with PLAYER_ID, PLAYER, etc.
        """
        cache_key = f'key_players_{team_id}_{season}'
        if cache_key in self.team_key_players_cache:
            return self.team_key_players_cache[cache_key]
        
        cache_file = self.cache_dir / f'key_players_{team_id}_{season}.json'
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                players = json.load(f)
                self.team_key_players_cache[cache_key] = players
                return players
        
        # Use improved PlayerClassifier
        try:
            from player_classifier import PlayerClassifier
            classifier = PlayerClassifier()
            classifications = classifier.classify_players(team_id, season)
            
            # Combine star and key players
            key_players = []
            
            # Add star player
            for star in classifications.get('star', []):
                key_players.append({
                    'player_id': star['player_id'],
                    'player_name': star['name'],
                    'position': star.get('position', ''),
                })
            
            # Add key players
            for key in classifications.get('key', []):
                key_players.append({
                    'player_id': key['player_id'],
                    'player_name': key['name'],
                    'position': key.get('position', ''),
                })
            
            # Cache it
            with open(cache_file, 'w') as f:
                json.dump(key_players, f, indent=2)
            
            self.team_key_players_cache[cache_key] = key_players
            return key_players
        
        except Exception as e:
            print(f"Error getting key players for team {team_id}: {e}")
            # Fallback to old method if classifier fails
            return []
    
    def check_player_played(self, player_id: int, game_id: str, season: str = None) -> bool:
        """
        Check if a player played in a specific game.
        Uses player game log - if MIN > 0, they played.
        """
        cache_key = f'player_{player_id}_game_{game_id}'
        if cache_key in self.player_availability_cache:
            return self.player_availability_cache[cache_key]
        
        if not NBA_API_AVAILABLE:
            return True  # Default to available if we can't check
        
        try:
            # Get player game log
            game_log = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=season or self._get_current_season()
            )
            gl_df = game_log.get_data_frames()[0]
            
            # Find the game
            game_row = gl_df[gl_df['Game_ID'] == game_id]
            if len(game_row) == 0:
                # Game not found - assume player didn't play (might be injury/rest)
                return False
            
            # Check if player played (MIN > 0)
            minutes = game_row.iloc[0].get('MIN', 0)
            played = minutes > 0
            
            self.player_availability_cache[cache_key] = played
            return played
        
        except Exception as e:
            # On error, assume available (conservative)
            return True
    
    def get_key_players_availability(self, team_id: int, game_date: datetime, 
                                    games_data: List[Dict], season: str = None) -> Dict:
        """
        Get availability of key players for a team before a game date.
        Uses performance-based approximation for speed (checks recent scoring drop).
        
        Returns:
            Dict with availability metrics
        """
        key_players = self.get_team_key_players(team_id, season)
        
        if len(key_players) == 0:
            return {
                'key_players_count': 0,
                'key_players_available': 3,  # Default to all available
                'key_players_available_pct': 1.0,
                'star_player_available': 1,
            }
        
        # Find team's recent games before this date
        team_games = [
            g for g in games_data
            if (g.get('home_team_id') == team_id or g.get('visitor_team_id') == team_id) and
            pd.to_datetime(g.get('date', '1900-01-01')) < game_date
        ]
        
        if len(team_games) == 0:
            return {
                'key_players_count': len(key_players),
                'key_players_available': len(key_players),
                'key_players_available_pct': 1.0,
                'star_player_available': 1,
            }
        
        # Sort by date descending
        team_games = sorted(team_games, key=lambda x: pd.to_datetime(x.get('date', '1900-01-01')), reverse=True)
        
        # Performance-based approximation:
        # If team's recent scoring dropped significantly, key players might be out
        # This is faster than checking individual player logs
        
        if len(team_games) >= 5:
            # Compare last 3 games vs previous 3 games
            recent_3 = team_games[:3]
            previous_3 = team_games[3:6]
            
            recent_avg = np.mean([
                g.get('home_team_score', 0) if g.get('home_team_id') == team_id 
                else g.get('visitor_team_score', 0) 
                for g in recent_3
            ])
            
            previous_avg = np.mean([
                g.get('home_team_score', 0) if g.get('home_team_id') == team_id 
                else g.get('visitor_team_score', 0) 
                for g in previous_3
            ])
            
            # If scoring dropped by >15 points, likely key players out
            scoring_drop = previous_avg - recent_avg
            
            if scoring_drop > 15:
                # Significant drop - estimate 1-2 key players out
                available_count = max(1, len(key_players) - 2)
                star_player_available = 0 if scoring_drop > 20 else 1
            elif scoring_drop > 8:
                # Moderate drop - estimate 1 key player out
                available_count = max(2, len(key_players) - 1)
                star_player_available = 1
            else:
                # Normal scoring - assume all available
                available_count = len(key_players)
                star_player_available = 1
        else:
            # Not enough games - assume all available
            available_count = len(key_players)
            star_player_available = 1
        
        return {
            'key_players_count': len(key_players),
            'key_players_available': available_count,
            'key_players_available_pct': available_count / len(key_players) if len(key_players) > 0 else 1.0,
            'star_player_available': star_player_available,
        }
    
    def _get_current_season(self) -> str:
        """Get current season string."""
        current_year = datetime.now().year
        if datetime.now().month >= 10:
            return f"{current_year}-{str(current_year + 1)[2:]}"
        else:
            return f"{current_year - 1}-{str(current_year)[2:]}"

