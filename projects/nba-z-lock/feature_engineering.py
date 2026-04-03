"""
Feature engineering for NBA game predictions.
Extracts features from game data, team stats, and historical matchups.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

# Import player availability tracker
try:
    from player_availability import PlayerAvailabilityTracker
    PLAYER_TRACKING_AVAILABLE = True
except ImportError:
    PLAYER_TRACKING_AVAILABLE = False

# Import player classifier for Phase 3 features
try:
    from player_classifier import PlayerClassifier
    PLAYER_CLASSIFIER_AVAILABLE = True
except ImportError:
    PLAYER_CLASSIFIER_AVAILABLE = False

class FeatureEngineer:
    """Extract and engineer features for ML model."""
    
    def __init__(self, games_data: List[Dict], teams_data: List[Dict] = None):
        """
        Initialize with historical game data.
        
        Args:
            games_data: List of game dictionaries from API
            teams_data: List of team dictionaries (optional)
        """
        # Handle empty games_data gracefully
        if not games_data or len(games_data) == 0:
            print("[FE] WARNING: Empty games_data provided, creating empty DataFrame with required columns")
            # Create empty DataFrame with required columns to avoid KeyErrors
            self.games_df = pd.DataFrame(columns=[
                'id', 'date', 'home_team', 'visitor_team', 
                'home_team_id', 'visitor_team_id',
                'home_team_score', 'visitor_team_score'
            ])
        else:
            try:
                self.games_df = pd.DataFrame(games_data)
                # Ensure required columns exist (add with default values if missing)
                required_cols = {
                    'home_team_score': 0,
                    'visitor_team_score': 0,
                    'home_team_id': None,
                    'visitor_team_id': None
                }
                for col, default_val in required_cols.items():
                    if col not in self.games_df.columns:
                        print(f"[FE] WARNING: Missing column '{col}', adding with default value {default_val}")
                        self.games_df[col] = default_val
            except Exception as e:
                print(f"[FE] ERROR: Failed to create DataFrame from games_data: {e}")
                import traceback
                traceback.print_exc()
                # Create empty DataFrame with required columns
                self.games_df = pd.DataFrame(columns=[
                    'id', 'date', 'home_team', 'visitor_team', 
                    'home_team_id', 'visitor_team_id',
                    'home_team_score', 'visitor_team_score'
                ])
        
        self.teams_data = teams_data or []
        self.team_stats_cache = {}
        self.team_record_cache = {}  # Cache for team records
        self.advanced_metrics_cache = {}  # Cache for advanced metrics
        self.recent_form_cache = {}  # Cache for recent form
        
        # Initialize player availability tracker
        if PLAYER_TRACKING_AVAILABLE:
            self.player_tracker = PlayerAvailabilityTracker()
        else:
            self.player_tracker = None
        
        # Initialize player classifier for Phase 3 features
        if PLAYER_CLASSIFIER_AVAILABLE:
            self.player_classifier = PlayerClassifier()
        else:
            self.player_classifier = None
        
        # Convert date strings to datetime if present (only if DataFrame is not empty)
        if len(self.games_df) > 0:
            if 'date' in self.games_df.columns:
                try:
                    self.games_df['date'] = pd.to_datetime(self.games_df['date'])
                except Exception as e:
                    print(f"[FE] WARNING: Could not convert date column: {e}")
            
            # Extract nested team IDs for easier access
            if 'home_team' in self.games_df.columns:
                try:
                    self.games_df['home_team_id'] = self.games_df['home_team'].apply(
                        lambda x: x.get('id') if isinstance(x, dict) else None
                    )
                except Exception as e:
                    print(f"[FE] WARNING: Could not extract home_team_id: {e}")
            
            if 'visitor_team' in self.games_df.columns:
                try:
                    self.games_df['visitor_team_id'] = self.games_df['visitor_team'].apply(
                        lambda x: x.get('id') if isinstance(x, dict) else None
                    )
                except Exception as e:
                    print(f"[FE] WARNING: Could not extract visitor_team_id: {e}")
            
            # OPTIMIZATION: Set indexes for faster filtering
            # Index on date for faster date-based filtering
            if 'date' in self.games_df.columns and len(self.games_df) > 0:
                try:
                    self.games_df = self.games_df.sort_values('date')
                    # Don't set as index (keeps DataFrame flexible), but sorted helps
                except Exception as e:
                    print(f"[FE] WARNING: Could not sort by date: {e}")
            
            # OPTIMIZATION: Ensure team_id columns are numeric for faster comparisons
            if 'home_team_id' in self.games_df.columns:
                try:
                    self.games_df['home_team_id'] = pd.to_numeric(self.games_df['home_team_id'], errors='coerce')
                except Exception as e:
                    print(f"[FE] WARNING: Could not convert home_team_id to numeric: {e}")
            if 'visitor_team_id' in self.games_df.columns:
                try:
                    self.games_df['visitor_team_id'] = pd.to_numeric(self.games_df['visitor_team_id'], errors='coerce')
                except Exception as e:
                    print(f"[FE] WARNING: Could not convert visitor_team_id to numeric: {e}")
    
    def calculate_advanced_metrics(self, team_id: int, before_date: datetime = None,
                                  num_games: int = 82) -> Dict:
        """
        Calculate advanced team metrics: Net Rating, eFG%, TS%, Pace, etc.
        
        Returns:
            Dict with advanced metrics
        """
        # Cache key for this calculation
        cache_key = f"adv_{team_id}_{before_date}_{num_games}"
        if cache_key in self.advanced_metrics_cache:
            return self.advanced_metrics_cache[cache_key]
        
        # OPTIMIZATION: Combine filters efficiently (no copy until needed)
        if len(self.games_df) == 0:
            result = {
                'net_rating': 0.0,
                'offensive_rating': 100.0,
                'defensive_rating': 100.0,
                'pace': 100.0,
                'efg_pct': 0.5,
                'ts_pct': 0.5,
            }
            self.advanced_metrics_cache[cache_key] = result
            return result
        
        team_mask = (self.games_df['home_team_id'] == team_id) | (self.games_df['visitor_team_id'] == team_id)
        if before_date and 'date' in self.games_df.columns:
            date_mask = self.games_df['date'] < before_date
            mask = team_mask & date_mask
        else:
            mask = team_mask
        
        team_games = self.games_df[mask].copy()  # Only copy when we have filtered data
        
        if len(team_games) == 0:
            result = {
                'net_rating': 0.0,
                'offensive_rating': 100.0,
                'defensive_rating': 100.0,
                'pace': 100.0,
                'efg_pct': 0.5,
                'ts_pct': 0.5,
            }
            self.advanced_metrics_cache[cache_key] = result
            return result
        
        team_games = team_games.sort_values('date', ascending=False).head(num_games)
        
        if len(team_games) == 0:
            result = {
                'net_rating': 0.0,
                'offensive_rating': 100.0,
                'defensive_rating': 100.0,
                'pace': 100.0,
                'efg_pct': 0.5,
                'ts_pct': 0.5,
            }
            self.advanced_metrics_cache[cache_key] = result
            return result
        
        # Vectorized operations (much faster than iterrows)
        is_home = team_games['home_team_id'] == team_id
        team_scores = np.where(is_home, team_games['home_team_score'], team_games['visitor_team_score'])
        opp_scores = np.where(is_home, team_games['visitor_team_score'], team_games['home_team_score'])
        
        points_for = team_scores
        points_against = opp_scores
        # Estimate possessions (simplified: average of both teams' scores)
        total_possessions = float(np.sum((team_scores + opp_scores) / 2))
        
        avg_points_for = float(np.mean(points_for)) if len(points_for) > 0 else 100
        avg_points_against = float(np.mean(points_against)) if len(points_against) > 0 else 100
        avg_possessions = total_possessions / len(team_games) if len(team_games) > 0 else 100
        
        # Offensive Rating (points per 100 possessions)
        offensive_rating = (avg_points_for / avg_possessions) * 100 if avg_possessions > 0 else 100
        
        # Defensive Rating (opponent points per 100 possessions)
        defensive_rating = (avg_points_against / avg_possessions) * 100 if avg_possessions > 0 else 100
        
        # Net Rating (Offensive - Defensive)
        net_rating = offensive_rating - defensive_rating
        
        # Pace (possessions per game)
        pace = avg_possessions
        
        # Simplified eFG% and TS% (we don't have FGA, 3PA, FTA from basic game data)
        # Using point-based approximations
        # eFG% approximation: higher scoring = better shooting (simplified)
        efg_pct = min(0.6, max(0.4, (avg_points_for / 110)))  # Normalized to 0.4-0.6 range
        
        # TS% approximation
        ts_pct = min(0.6, max(0.4, (avg_points_for / 105)))  # Normalized
        
        result = {
            'net_rating': net_rating,
            'offensive_rating': offensive_rating,
            'defensive_rating': defensive_rating,
            'pace': pace,
            'efg_pct': efg_pct,
            'ts_pct': ts_pct,
        }
        # Cache the result
        self.advanced_metrics_cache[cache_key] = result
        return result
    
    def calculate_team_record(self, team_id: int, before_date: datetime = None,
                            home_only: bool = False, away_only: bool = False) -> Dict:
        """
        Calculate team's win/loss record up to a certain date.
        
        Returns:
            Dict with 'wins', 'losses', 'win_pct', 'home_wins', 'home_losses', etc.
        """
        # Cache key for this calculation
        cache_key = f"{team_id}_{before_date}_{home_only}_{away_only}"
        if cache_key in self.team_record_cache:
            return self.team_record_cache[cache_key]
        
        # Handle empty DataFrame
        if len(self.games_df) == 0:
            result = {
                'wins': 0,
                'losses': 0,
                'win_pct': 0.5,
            }
            self.team_record_cache[cache_key] = result
            return result
        
        # OPTIMIZATION: Combine filters in one step (much faster than sequential filtering)
        # Build filter mask efficiently
        if before_date and 'date' in self.games_df.columns:
            date_mask = self.games_df['date'] < before_date
        else:
            # No date filter - all games
            date_mask = pd.Series([True] * len(self.games_df), index=self.games_df.index)
        
        # Filter by home/away if specified
        if home_only:
            # Combine date and team filters in one step
            team_mask = (self.games_df['home_team_id'] == team_id)
            mask = date_mask & team_mask
            team_games = self.games_df[mask]
            # Vectorized comparison (faster)
            if len(team_games) > 0 and 'home_team_score' in team_games.columns and 'visitor_team_score' in team_games.columns:
                wins = int(np.sum(team_games['home_team_score'] > team_games['visitor_team_score']))
                losses = int(np.sum(team_games['home_team_score'] < team_games['visitor_team_score']))
            else:
                wins = 0
                losses = 0
        elif away_only:
            # Combine date and team filters in one step
            team_mask = (self.games_df['visitor_team_id'] == team_id)
            mask = date_mask & team_mask
            team_games = self.games_df[mask]
            # Vectorized comparison (faster)
            if len(team_games) > 0 and 'home_team_score' in team_games.columns and 'visitor_team_score' in team_games.columns:
                wins = int(np.sum(team_games['visitor_team_score'] > team_games['home_team_score']))
                losses = int(np.sum(team_games['visitor_team_score'] < team_games['home_team_score']))
            else:
                wins = 0
                losses = 0
        else:
            # All games - combine filters efficiently
            home_team_mask = (self.games_df['home_team_id'] == team_id)
            away_team_mask = (self.games_df['visitor_team_id'] == team_id)
            home_mask = date_mask & home_team_mask
            away_mask = date_mask & away_team_mask
            home_games = self.games_df[home_mask]
            away_games = self.games_df[away_mask]
            
            # Vectorized comparisons (much faster)
            if len(home_games) > 0 and 'home_team_score' in home_games.columns and 'visitor_team_score' in home_games.columns:
                home_wins = int(np.sum(home_games['home_team_score'] > home_games['visitor_team_score']))
                home_losses = int(np.sum(home_games['home_team_score'] < home_games['visitor_team_score']))
            else:
                home_wins = 0
                home_losses = 0
            
            if len(away_games) > 0 and 'home_team_score' in away_games.columns and 'visitor_team_score' in away_games.columns:
                away_wins = int(np.sum(away_games['visitor_team_score'] > away_games['home_team_score']))
                away_losses = int(np.sum(away_games['visitor_team_score'] < away_games['home_team_score']))
            else:
                away_wins = 0
                away_losses = 0
            
            wins = home_wins + away_wins
            losses = home_losses + away_losses
            
            result = {
                'wins': wins,
                'losses': losses,
                'win_pct': wins / (wins + losses) if (wins + losses) > 0 else 0.5,
                'home_wins': home_wins,
                'home_losses': home_losses,
                'home_win_pct': home_wins / (home_wins + home_losses) if (home_wins + home_losses) > 0 else 0.5,
                'away_wins': away_wins,
                'away_losses': away_losses,
                'away_win_pct': away_wins / (away_wins + away_losses) if (away_wins + away_losses) > 0 else 0.5,
            }
            # Cache the result
            self.team_record_cache[cache_key] = result
            return result
        
        total = wins + losses
        result = {
            'wins': wins,
            'losses': losses,
            'win_pct': wins / total if total > 0 else 0.5,
        }
        # Cache the result
        self.team_record_cache[cache_key] = result
        return result
    
    def get_recent_form(self, team_id: int, before_date: datetime, num_games: int = 10) -> Dict:
        """
        Get team's recent form (last N games).
        
        Returns:
            Dict with wins, losses, win_pct, avg_points_for, avg_points_against
        """
        # Cache key for this calculation
        cache_key = f"form_{team_id}_{before_date}_{num_games}"
        if cache_key in self.recent_form_cache:
            return self.recent_form_cache[cache_key]
        
        # OPTIMIZATION: Combine filters efficiently
        if len(self.games_df) == 0:
            result = {
                'wins': 0,
                'losses': 0,
                'win_pct': 0.5,
                'avg_points_for': 100,
                'avg_points_against': 100,
            }
            self.recent_form_cache[cache_key] = result
            return result
        
        team_mask = (self.games_df['home_team_id'] == team_id) | (self.games_df['visitor_team_id'] == team_id)
        if 'date' in self.games_df.columns:
            date_mask = self.games_df['date'] < before_date
            mask = team_mask & date_mask
        else:
            mask = team_mask
        
        # Get team's games before the date, sorted by date descending
        team_games = self.games_df[mask].copy()
        
        if len(team_games) == 0:
            return {
                'wins': 0,
                'losses': 0,
                'win_pct': 0.5,
                'avg_points_for': 100,
                'avg_points_against': 100,
            }
        
        # Sort by date descending and take last N games
        team_games = team_games.sort_values('date', ascending=False).head(num_games)
        
        if len(team_games) == 0:
            result = {
                'wins': 0,
                'losses': 0,
                'win_pct': 0.5,
                'avg_points_for': 100,
                'avg_points_against': 100,
            }
            self.recent_form_cache[cache_key] = result
            return result
        
        # Vectorized operations (much faster than iterrows)
        is_home = team_games['home_team_id'] == team_id
        team_scores = np.where(is_home, team_games['home_team_score'], team_games['visitor_team_score'])
        opp_scores = np.where(is_home, team_games['visitor_team_score'], team_games['home_team_score'])
        
        wins = int(np.sum(team_scores > opp_scores))
        losses = len(team_games) - wins
        
        result = {
            'wins': wins,
            'losses': losses,
            'win_pct': float(wins / len(team_games)) if len(team_games) > 0 else 0.5,
            'avg_points_for': float(np.mean(team_scores)) if len(team_scores) > 0 else 100,
            'avg_points_against': float(np.mean(opp_scores)) if len(opp_scores) > 0 else 100,
        }
        # Cache the result
        self.recent_form_cache[cache_key] = result
        return result
    
    def get_head_to_head(self, team1_id: int, team2_id: int, 
                        before_date: datetime = None) -> Dict:
        """
        Get head-to-head record between two teams.
        
        Returns:
            Dict with team1_wins, team2_wins, team1_win_pct
        """
        # OPTIMIZATION: Combine all filters in one step
        h2h_mask = (
            ((self.games_df['home_team_id'] == team1_id) & 
             (self.games_df['visitor_team_id'] == team2_id)) |
            ((self.games_df['home_team_id'] == team2_id) & 
             (self.games_df['visitor_team_id'] == team1_id))
        )
        
        if before_date:
            date_mask = self.games_df['date'] < before_date
            mask = h2h_mask & date_mask
        else:
            mask = h2h_mask
        
        h2h_games = self.games_df[mask].copy()
        
        if len(h2h_games) == 0:
            return {
                'team1_wins': 0,
                'team2_wins': 0,
                'team1_win_pct': 0.5,
            }
        
        team1_wins = 0
        for _, game in h2h_games.iterrows():
            is_home = game.get('home_team_id') == team1_id
            if is_home:
                if game['home_team_score'] > game['visitor_team_score']:
                    team1_wins += 1
            else:
                if game['visitor_team_score'] > game['home_team_score']:
                    team1_wins += 1
        
        team2_wins = len(h2h_games) - team1_wins
        
        return {
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'team1_win_pct': team1_wins / len(h2h_games) if len(h2h_games) > 0 else 0.5,
        }
    
    def calculate_rest_days(self, team_id: int, game_date: datetime) -> int:
        """Calculate days of rest for a team before a game."""
        # OPTIMIZATION: Combine filters efficiently
        if len(self.games_df) == 0:
            return 2  # Default if no games data
        
        team_mask = (self.games_df['home_team_id'] == team_id) | (self.games_df['visitor_team_id'] == team_id)
        if 'date' in self.games_df.columns:
            date_mask = self.games_df['date'] < game_date
            mask = team_mask & date_mask
            
            # Find team's last game before this date (no need to copy, just get max)
            if mask.any():
                try:
                    last_game_date = self.games_df.loc[mask, 'date'].max()
                    rest_days = (game_date - last_game_date).days
                    return max(0, min(rest_days, 7))  # Cap at 7 days
                except:
                    return 2
        else:
            # No date column, just check team games
            if team_mask.any():
                return 2  # Default rest days
        
        return 2  # Default to 2 days rest if no previous games
    
    def calculate_home_streak(self, team_id: int, game_date: datetime) -> int:
        """Calculate consecutive home games for a team."""
        # OPTIMIZATION: Combine filters efficiently
        if len(self.games_df) == 0:
            return 0
        
        team_mask = (self.games_df['home_team_id'] == team_id) | (self.games_df['visitor_team_id'] == team_id)
        if 'date' in self.games_df.columns:
            date_mask = self.games_df['date'] < game_date
            mask = team_mask & date_mask
        else:
            mask = team_mask
        
        # Get team games (already sorted by date in __init__)
        team_games = self.games_df[mask].sort_values('date', ascending=False).head(10) if mask.any() else pd.DataFrame()
        
        if len(team_games) == 0:
            return 0
        
        # Count consecutive home games from most recent (limit to 10 for speed)
        streak = 0
        for _, game in team_games.iterrows():
            if game['home_team_id'] == team_id:
                streak += 1
            else:
                break
        
        return min(streak, 10)  # Cap at 10
    
    def calculate_away_streak(self, team_id: int, game_date: datetime) -> int:
        """Calculate consecutive away games for a team."""
        # OPTIMIZATION: Combine filters efficiently
        if len(self.games_df) == 0:
            return 0
        
        team_mask = (self.games_df['home_team_id'] == team_id) | (self.games_df['visitor_team_id'] == team_id)
        if 'date' in self.games_df.columns:
            date_mask = self.games_df['date'] < game_date
            mask = team_mask & date_mask
        else:
            mask = team_mask
        
        # Get team games (already sorted by date in __init__)
        team_games = self.games_df[mask].sort_values('date', ascending=False).head(10) if mask.any() else pd.DataFrame()
        
        if len(team_games) == 0:
            return 0
        
        # Count consecutive away games from most recent (limit to 10 for speed)
        streak = 0
        for _, game in team_games.iterrows():
            if game['visitor_team_id'] == team_id:
                streak += 1
            else:
                break
        
        return min(streak, 10)  # Cap at 10
    
    def get_player_stats(self, team_id: int, game_date: datetime = None, use_cache: bool = True) -> Dict:
        """
        Get player-level statistics for a team (Phase 3 feature).
        Returns star player stats and top 3 players aggregate stats.
        
        Args:
            team_id: Team ID
            game_date: Date of the game (for season determination)
            use_cache: Whether to use cached player stats (faster for training)
        
        Returns:
            Dict with star player stats and top 3 aggregate stats
        """
        if not self.player_classifier:
            # Return defaults if classifier not available
            return {
                'star_ppg': 0.0,
                'star_usage': 0.0,
                'star_mpg': 0.0,
                'top3_ppg_avg': 0.0,
                'top3_mpg_avg': 0.0,
                'top3_impact_avg': 0.0
            }
        
        try:
            # Get season from game date
            if game_date:
                season_year = game_date.year
                if game_date.month >= 10:
                    season = f"{season_year}-{str(season_year + 1)[2:]}"
                else:
                    season = f"{season_year - 1}-{str(season_year)[2:]}"
            else:
                from datetime import datetime as dt
                now = dt.now()
                if now.month >= 10:
                    season = f"{now.year}-{str(now.year + 1)[2:]}"
                else:
                    season = f"{now.year - 1}-{str(now.year)[2:]}"
            
            # For predictions, ALWAYS use cache/estimates to ensure fast response
            # API calls are too slow for real-time predictions (30+ seconds)
            if use_cache:
                print(f"    [FE] FAST MODE: Using cached/estimated stats (skipping API calls)...")
                cached_stats = self._get_cached_or_estimated_player_stats(team_id, season)
                print(f"    [FE] Using cached stats (star_ppg={cached_stats.get('star_ppg', 0):.1f})")
                return cached_stats
            
            # Only fetch from API if use_cache=False (for training only)
            # For historical games (older than 1 year), use season averages or skip
            from datetime import datetime as dt
            if game_date and (dt.now() - game_date).days > 365:
                return self._get_cached_or_estimated_player_stats(team_id, season)
            
            # Get player classifications (with timeout protection) - ONLY for training
            try:
                print(f"    [FE] Fetching player classifications from API (SLOW - training only)...")
                classifications = self.player_classifier.classify_players(team_id, season)
                print(f"    [FE] Successfully fetched player classifications")
            except Exception as e:
                print(f"    [FE] Warning: Could not fetch player stats for team {team_id}, using estimates: {e}")
                return self._get_cached_or_estimated_player_stats(team_id, season)
            
            # Star player stats
            star_ppg = 0.0
            star_usage = 0.0
            star_mpg = 0.0
            
            if classifications.get('star') and len(classifications['star']) > 0:
                star = classifications['star'][0]
                star_ppg = star.get('ppg', 0.0)
                star_usage = star.get('usage', 0.0) / 100.0  # Convert from percentage
                star_mpg = star.get('mpg', 0.0)
            
            # Top 3 players aggregate (star + key players)
            top3_players = []
            if classifications.get('star'):
                top3_players.extend(classifications['star'])
            if classifications.get('key'):
                top3_players.extend(classifications['key'][:3 - len(top3_players)])
            
            top3_ppg_avg = 0.0
            top3_mpg_avg = 0.0
            top3_impact_avg = 0.0
            
            if len(top3_players) > 0:
                top3_ppg_avg = np.mean([p.get('ppg', 0.0) for p in top3_players])
                top3_mpg_avg = np.mean([p.get('mpg', 0.0) for p in top3_players])
                top3_impact_avg = np.mean([p.get('impact_score', 0.0) for p in top3_players])
            
            return {
                'star_ppg': star_ppg,
                'star_usage': star_usage,
                'star_mpg': star_mpg,
                'top3_ppg_avg': top3_ppg_avg,
                'top3_mpg_avg': top3_mpg_avg,
                'top3_impact_avg': top3_impact_avg
            }
            
        except Exception as e:
            # Return defaults on error
            print(f"Error getting player stats for team {team_id}: {e}")
            return self._get_cached_or_estimated_player_stats(team_id, season if 'season' in locals() else None)
    
    def _get_cached_or_estimated_player_stats(self, team_id: int, season: str = None) -> Dict:
        """
        Get cached player stats or return reasonable estimates.
        This speeds up training by avoiding API calls for every historical game.
        IMPORTANT: This method NEVER makes API calls - only uses cache or returns estimates.
        """
        # Try to get from cache first (NO API CALLS - cache only)
        if self.player_classifier:
            try:
                cache_key = f'{team_id}_{season}' if season else f'{team_id}'
                # Only check cache - NEVER call classify_players or any API methods
                if cache_key in self.player_classifier.classification_cache:
                    classifications = self.player_classifier.classification_cache[cache_key]
                    
                    # Extract stats from cached classification
                    star_ppg = 0.0
                    star_usage = 0.0
                    star_mpg = 0.0
                    
                    if classifications.get('star') and len(classifications['star']) > 0:
                        star = classifications['star'][0]
                        star_ppg = star.get('ppg', 0.0)
                        star_usage = star.get('usage', 0.0) / 100.0
                        star_mpg = star.get('mpg', 0.0)
                    
                    top3_players = []
                    if classifications.get('star'):
                        top3_players.extend(classifications['star'])
                    if classifications.get('key'):
                        top3_players.extend(classifications['key'][:3 - len(top3_players)])
                    
                    top3_ppg_avg = np.mean([p.get('ppg', 0.0) for p in top3_players]) if top3_players else 0.0
                    top3_mpg_avg = np.mean([p.get('mpg', 0.0) for p in top3_players]) if top3_players else 0.0
                    top3_impact_avg = np.mean([p.get('impact_score', 0.0) for p in top3_players]) if top3_players else 0.0
                    
                    print(f"    [FE] Using cached player stats from classification_cache")
                    return {
                        'star_ppg': star_ppg,
                        'star_usage': star_usage,
                        'star_mpg': star_mpg,
                        'top3_ppg_avg': top3_ppg_avg,
                        'top3_mpg_avg': top3_mpg_avg,
                        'top3_impact_avg': top3_impact_avg
                    }
            except Exception as e:
                print(f"    [FE] Cache check failed: {e}, using estimates")
        
        # Return reasonable estimates if cache miss (NO API CALLS)
        # These are typical NBA averages - fast and safe
        print(f"    [FE] Cache miss for team {team_id}, using estimated stats (NO API CALLS)")
        return {
            'star_ppg': 22.0,  # Typical star player PPG
            'star_usage': 0.28,  # Typical star usage rate
            'star_mpg': 35.0,  # Typical star minutes
            'top3_ppg_avg': 18.0,  # Average of top 3 players
            'top3_mpg_avg': 32.0,  # Average minutes
            'top3_impact_avg': 20.0  # Average impact score
        }
    
    def extract_features_for_game(self, game: Dict) -> Dict:
        """
        Extract all features for a single game.
        
        Args:
            game: Game dictionary from API
        
        Returns:
            Feature dictionary for ML model
        """
        game_date = pd.to_datetime(game['date'])
        home_team_id = game.get('home_team_id') or (game.get('home_team', {}).get('id') if isinstance(game.get('home_team'), dict) else None)
        visitor_team_id = game.get('visitor_team_id') or (game.get('visitor_team', {}).get('id') if isinstance(game.get('visitor_team'), dict) else None)
        
        if not home_team_id or not visitor_team_id:
            raise ValueError("Could not extract team IDs from game data")
        
        # Team records
        home_record = self.calculate_team_record(home_team_id, before_date=game_date)
        visitor_record = self.calculate_team_record(visitor_team_id, before_date=game_date)
        
        # Home/away specific records
        home_home_record = self.calculate_team_record(home_team_id, before_date=game_date, home_only=True)
        visitor_away_record = self.calculate_team_record(visitor_team_id, before_date=game_date, away_only=True)
        
        # Recent form
        home_recent = self.get_recent_form(home_team_id, before_date=game_date, num_games=10)
        visitor_recent = self.get_recent_form(visitor_team_id, before_date=game_date, num_games=10)
        
        # Head-to-head
        h2h = self.get_head_to_head(home_team_id, visitor_team_id, before_date=game_date)
        
        # Rest days
        home_rest = self.calculate_rest_days(home_team_id, game_date)
        visitor_rest = self.calculate_rest_days(visitor_team_id, game_date)
        
        # Advanced metrics
        home_advanced = self.calculate_advanced_metrics(home_team_id, before_date=game_date)
        visitor_advanced = self.calculate_advanced_metrics(visitor_team_id, before_date=game_date)
        
        # Enhanced situational features
        # Check for back-to-back games
        home_is_back_to_back = 1 if home_rest == 0 else 0
        visitor_is_back_to_back = 1 if visitor_rest == 0 else 0
        
        # Home/away streak (consecutive home/away games)
        home_home_streak = self.calculate_home_streak(home_team_id, game_date)
        visitor_away_streak = self.calculate_away_streak(visitor_team_id, game_date)
        
        # Player availability (Phase 1 - injury approximation)
        home_player_availability = {}
        visitor_player_availability = {}
        
        if self.player_tracker:
            try:
                # Get season from game date
                season_year = game_date.year
                if game_date.month >= 10:
                    season = f"{season_year}-{str(season_year + 1)[2:]}"
                else:
                    season = f"{season_year - 1}-{str(season_year)[2:]}"
                
                home_player_availability = self.player_tracker.get_key_players_availability(
                    home_team_id, game_date, self.games_df.to_dict('records'), season
                )
                visitor_player_availability = self.player_tracker.get_key_players_availability(
                    visitor_team_id, game_date, self.games_df.to_dict('records'), season
                )
            except Exception as e:
                # If player tracking fails, use defaults
                home_player_availability = {'key_players_available': 3, 'star_player_available': 1}
                visitor_player_availability = {'key_players_available': 3, 'star_player_available': 1}
        else:
            # Defaults if player tracking not available
            home_player_availability = {'key_players_available': 3, 'star_player_available': 1}
            visitor_player_availability = {'key_players_available': 3, 'star_player_available': 1}
        
        # Build feature vector
        features = {
            # Home team overall record
            'home_win_pct': home_record.get('win_pct', 0.5),
            'home_wins': home_record.get('wins', 0),
            'home_losses': home_record.get('losses', 0),
            
            # Visitor team overall record
            'visitor_win_pct': visitor_record.get('win_pct', 0.5),
            'visitor_wins': visitor_record.get('wins', 0),
            'visitor_losses': visitor_record.get('losses', 0),
            
            # Home team at home
            'home_home_win_pct': home_home_record.get('home_win_pct', 0.5),
            
            # Visitor team away
            'visitor_away_win_pct': visitor_away_record.get('away_win_pct', 0.5),
            
            # Win percentage difference (QUICK WIN - highly predictive)
            'win_pct_diff': self._safe_float(home_record.get('win_pct', 0.5) - visitor_record.get('win_pct', 0.5)),
            
            # Recent form (last 10 games)
            'home_recent_win_pct': home_recent['win_pct'],
            'home_recent_avg_points_for': home_recent['avg_points_for'],
            'home_recent_avg_points_against': home_recent['avg_points_against'],
            'home_recent_point_diff': self._safe_float(home_recent['avg_points_for'] - home_recent['avg_points_against']),
            
            'visitor_recent_win_pct': visitor_recent['win_pct'],
            'visitor_recent_avg_points_for': visitor_recent['avg_points_for'],
            'visitor_recent_avg_points_against': visitor_recent['avg_points_against'],
            'visitor_recent_point_diff': self._safe_float(visitor_recent['avg_points_for'] - visitor_recent['avg_points_against']),
            
            # Recent form differences (QUICK WIN - highly predictive)
            'recent_win_pct_diff': self._safe_float(home_recent['win_pct'] - visitor_recent['win_pct']),
            'recent_point_diff_diff': self._safe_float((home_recent['avg_points_for'] - home_recent['avg_points_against']) - 
                                     (visitor_recent['avg_points_for'] - visitor_recent['avg_points_against'])),
            
            # Head-to-head
            'h2h_home_win_pct': h2h['team1_win_pct'],
            'h2h_games_played': h2h['team1_wins'] + h2h['team2_wins'],
            
            # Rest days
            'home_rest_days': home_rest,
            'visitor_rest_days': visitor_rest,
            'rest_days_diff': home_rest - visitor_rest,
            
            # Advanced metrics (Phase 1 improvement)
            'home_net_rating': home_advanced['net_rating'],
            'home_offensive_rating': home_advanced['offensive_rating'],
            'home_defensive_rating': home_advanced['defensive_rating'],
            'home_pace': home_advanced['pace'],
            'home_efg_pct': home_advanced['efg_pct'],
            'home_ts_pct': home_advanced['ts_pct'],
            
            'visitor_net_rating': visitor_advanced['net_rating'],
            'visitor_offensive_rating': visitor_advanced['offensive_rating'],
            'visitor_defensive_rating': visitor_advanced['defensive_rating'],
            'visitor_pace': visitor_advanced['pace'],
            'visitor_efg_pct': visitor_advanced['efg_pct'],
            'visitor_ts_pct': visitor_advanced['ts_pct'],
            
            # Advanced metric differences
            'net_rating_diff': home_advanced['net_rating'] - visitor_advanced['net_rating'],
            'offensive_rating_diff': home_advanced['offensive_rating'] - visitor_advanced['offensive_rating'],
            'defensive_rating_diff': home_advanced['defensive_rating'] - visitor_advanced['defensive_rating'],
            'pace_diff': home_advanced['pace'] - visitor_advanced['pace'],
            
            # Enhanced situational features (Phase 1 improvement)
            'home_is_back_to_back': home_is_back_to_back,
            'visitor_is_back_to_back': visitor_is_back_to_back,
            'home_home_streak': home_home_streak,
            'visitor_away_streak': visitor_away_streak,
            
            # Player availability (Phase 1 - injury approximation)
            'home_key_players_available': self._safe_float(home_player_availability.get('key_players_available', 3)),
            'home_star_player_available': self._safe_float(home_player_availability.get('star_player_available', 1)),
            'visitor_key_players_available': self._safe_float(visitor_player_availability.get('key_players_available', 3)),
            'visitor_star_player_available': self._safe_float(visitor_player_availability.get('star_player_available', 1)),
            'key_players_available_diff': self._safe_float(home_player_availability.get('key_players_available', 3) - 
                                          visitor_player_availability.get('key_players_available', 3)),
            
            # Player-level statistics (Phase 3 - HIGHEST IMPACT)
            **self._get_player_features(home_team_id, visitor_team_id, game_date),
            
            # Win margin (for training - actual outcome)
            'home_team_won': 1 if game.get('home_team_score', 0) > game.get('visitor_team_score', 0) else 0,
            
            # Game date (for time-based weighting in training)
            'game_date': game_date.isoformat() if isinstance(game_date, pd.Timestamp) else game_date.strftime('%Y-%m-%d') if hasattr(game_date, 'strftime') else str(game_date),
        }
        
        return features
    
    def create_training_dataset(self) -> pd.DataFrame:
        """
        Create training dataset from all historical games.
        
        Returns:
            DataFrame with features and target variable
        """
        features_list = []
        
        for _, game in self.games_df.iterrows():
            try:
                features = self.extract_features_for_game(game.to_dict())
                features_list.append(features)
            except Exception as e:
                # Skip games that cause errors
                continue
        
        df = pd.DataFrame(features_list)
        return df
    
    def extract_features_for_prediction(self, home_team_id: int, visitor_team_id: int,
                                      game_date: datetime = None, injury_data: Optional[Dict] = None) -> Dict:
        """
        Extract features for a future game prediction.
        
        Args:
            home_team_id: Home team ID
            visitor_team_id: Visitor team ID
            game_date: Date of the game (defaults to today)
        
        Returns:
            Feature dictionary (without outcome)
        """
        if game_date is None:
            game_date = datetime.now()
        else:
            game_date = pd.to_datetime(game_date)
        
        # Team records
        home_record = self.calculate_team_record(home_team_id, before_date=game_date)
        visitor_record = self.calculate_team_record(visitor_team_id, before_date=game_date)
        
        # Home/away specific records
        home_home_record = self.calculate_team_record(home_team_id, before_date=game_date, home_only=True)
        visitor_away_record = self.calculate_team_record(visitor_team_id, before_date=game_date, away_only=True)
        
        # Recent form
        home_recent = self.get_recent_form(home_team_id, before_date=game_date, num_games=10)
        visitor_recent = self.get_recent_form(visitor_team_id, before_date=game_date, num_games=10)
        
        # Head-to-head
        h2h = self.get_head_to_head(home_team_id, visitor_team_id, before_date=game_date)
        
        # Rest days
        home_rest = self.calculate_rest_days(home_team_id, game_date)
        visitor_rest = self.calculate_rest_days(visitor_team_id, game_date)
        
        # Advanced metrics
        home_advanced = self.calculate_advanced_metrics(home_team_id, before_date=game_date)
        visitor_advanced = self.calculate_advanced_metrics(visitor_team_id, before_date=game_date)
        
        # Enhanced situational features
        home_is_back_to_back = 1 if home_rest == 0 else 0
        visitor_is_back_to_back = 1 if visitor_rest == 0 else 0
        home_home_streak = self.calculate_home_streak(home_team_id, game_date)
        visitor_away_streak = self.calculate_away_streak(visitor_team_id, game_date)
        
        # Player-level statistics (Phase 3 - HIGHEST IMPACT)
        # Use cached/estimated stats for predictions to avoid slow API calls
        print(f"    [FE] Getting player features (using cache/estimates for speed)...")
        player_features = self._get_player_features(home_team_id, visitor_team_id, game_date, use_cache=True)
        
        # Player availability (Phase 1 - injury approximation)
        # Use manual injury data if provided, otherwise use automatic approximation
        print(f"    [FE] Processing injury data in feature engineering...")
        print(f"    [FE] Injury data received: {injury_data}")
        print(f"    [FE] Injury data type: {type(injury_data)}")
        
        if injury_data:
            print(f"    [FE] Using manual injury data from UI")
            # Manual injury data from UI
            home_injury = injury_data.get('home', {})
            visitor_injury = injury_data.get('visitor', {})
            print(f"    [FE] Home injury data: {home_injury}")
            print(f"    [FE] Visitor injury data: {visitor_injury}")
            
            home_player_availability = {
                'key_players_available': home_injury.get('key_players_available', 3),
                'star_player_available': home_injury.get('star_player_available', 1)
            }
            visitor_player_availability = {
                'key_players_available': visitor_injury.get('key_players_available', 3),
                'star_player_available': visitor_injury.get('star_player_available', 1)
            }
            print(f"    [FE] Home player availability: {home_player_availability}")
            print(f"    [FE] Visitor player availability: {visitor_player_availability}")
        elif self.player_tracker:
            print(f"    [FE] Using automatic player availability approximation")
            # Automatic approximation using historical data
            try:
                season_year = game_date.year
                if game_date.month >= 10:
                    season = f"{season_year}-{str(season_year + 1)[2:]}"
                else:
                    season = f"{season_year - 1}-{str(season_year)[2:]}"
                
                home_player_availability = self.player_tracker.get_key_players_availability(
                    home_team_id, game_date, self.games_df.to_dict('records'), season
                )
                visitor_player_availability = self.player_tracker.get_key_players_availability(
                    visitor_team_id, game_date, self.games_df.to_dict('records'), season
                )
            except Exception as e:
                home_player_availability = {'key_players_available': 3, 'star_player_available': 1}
                visitor_player_availability = {'key_players_available': 3, 'star_player_available': 1}
        else:
            print(f"    [FE] Using default player availability (all players available)")
            # Default (all players available)
            home_player_availability = {'key_players_available': 3, 'star_player_available': 1}
            visitor_player_availability = {'key_players_available': 3, 'star_player_available': 1}
        
        # Build feature vector (without outcome)
        features = {
            'home_win_pct': home_record.get('win_pct', 0.5),
            'home_wins': home_record.get('wins', 0),
            'home_losses': home_record.get('losses', 0),
            'visitor_win_pct': visitor_record.get('win_pct', 0.5),
            'visitor_wins': visitor_record.get('wins', 0),
            'visitor_losses': visitor_record.get('losses', 0),
            'home_home_win_pct': home_home_record.get('home_win_pct', 0.5),
            'visitor_away_win_pct': visitor_away_record.get('away_win_pct', 0.5),
            # Win percentage difference (QUICK WIN - highly predictive)
            'win_pct_diff': self._safe_float(home_record.get('win_pct', 0.5) - visitor_record.get('win_pct', 0.5)),
            'home_recent_win_pct': home_recent['win_pct'],
            'home_recent_avg_points_for': home_recent['avg_points_for'],
            'home_recent_avg_points_against': home_recent['avg_points_against'],
            'home_recent_point_diff': self._safe_float(home_recent['avg_points_for'] - home_recent['avg_points_against']),
            'visitor_recent_win_pct': visitor_recent['win_pct'],
            'visitor_recent_avg_points_for': visitor_recent['avg_points_for'],
            'visitor_recent_avg_points_against': visitor_recent['avg_points_against'],
            'visitor_recent_point_diff': self._safe_float(visitor_recent['avg_points_for'] - visitor_recent['avg_points_against']),
            # Recent form differences (QUICK WIN - highly predictive)
            'recent_win_pct_diff': self._safe_float(home_recent['win_pct'] - visitor_recent['win_pct']),
            'recent_point_diff_diff': self._safe_float((home_recent['avg_points_for'] - home_recent['avg_points_against']) - 
                                     (visitor_recent['avg_points_for'] - visitor_recent['avg_points_against'])),
            'h2h_home_win_pct': h2h['team1_win_pct'],
            'h2h_games_played': h2h['team1_wins'] + h2h['team2_wins'],
            'home_rest_days': home_rest,
            'visitor_rest_days': visitor_rest,
            'rest_days_diff': home_rest - visitor_rest,
            
            # Advanced metrics (Phase 1 improvement)
            'home_net_rating': home_advanced['net_rating'],
            'home_offensive_rating': home_advanced['offensive_rating'],
            'home_defensive_rating': home_advanced['defensive_rating'],
            'home_pace': home_advanced['pace'],
            'home_efg_pct': home_advanced['efg_pct'],
            'home_ts_pct': home_advanced['ts_pct'],
            
            'visitor_net_rating': visitor_advanced['net_rating'],
            'visitor_offensive_rating': visitor_advanced['offensive_rating'],
            'visitor_defensive_rating': visitor_advanced['defensive_rating'],
            'visitor_pace': visitor_advanced['pace'],
            'visitor_efg_pct': visitor_advanced['efg_pct'],
            'visitor_ts_pct': visitor_advanced['ts_pct'],
            
            # Advanced metric differences
            'net_rating_diff': home_advanced['net_rating'] - visitor_advanced['net_rating'],
            'offensive_rating_diff': home_advanced['offensive_rating'] - visitor_advanced['offensive_rating'],
            'defensive_rating_diff': home_advanced['defensive_rating'] - visitor_advanced['defensive_rating'],
            'pace_diff': home_advanced['pace'] - visitor_advanced['pace'],
            
            # Enhanced situational features (Phase 1 improvement)
            'home_is_back_to_back': home_is_back_to_back,
            'visitor_is_back_to_back': visitor_is_back_to_back,
            'home_home_streak': home_home_streak,
            'visitor_away_streak': visitor_away_streak,
            
            # Player availability (Phase 1 - injury approximation)
            'home_key_players_available': self._safe_float(home_player_availability.get('key_players_available', 3)),
            'home_star_player_available': self._safe_float(home_player_availability.get('star_player_available', 1)),
            'visitor_key_players_available': self._safe_float(visitor_player_availability.get('key_players_available', 3)),
            'visitor_star_player_available': self._safe_float(visitor_player_availability.get('star_player_available', 1)),
            'key_players_available_diff': self._safe_float(home_player_availability.get('key_players_available', 3) - 
                                          visitor_player_availability.get('key_players_available', 3)),
            
            # Player-level statistics (Phase 3 - HIGHEST IMPACT)
            **player_features,
        }
        
        return features
    
    def _safe_float(self, value):
        """Convert value to float, handling NaN and None."""
        try:
            if value is None:
                return 0.0
            float_val = float(value)
            if np.isnan(float_val) or np.isinf(float_val):
                return 0.0
            return float_val
        except (ValueError, TypeError):
            return 0.0
    
    def _get_player_features(self, home_team_id: int, visitor_team_id: int, game_date: datetime, use_cache: bool = True) -> Dict:
        """
        Helper method to get player-level features for both teams.
        Returns dict of features to merge into main feature dict.
        
        Args:
            home_team_id: Home team ID
            visitor_team_id: Visitor team ID
            game_date: Date of the game
            use_cache: Whether to use cached/estimated stats (faster, avoids API calls)
        """
        print(f"    [FE] Getting player stats for home team {home_team_id} (use_cache={use_cache})...")
        home_player_stats = self.get_player_stats(home_team_id, game_date, use_cache=use_cache)
        print(f"    [FE] Getting player stats for visitor team {visitor_team_id} (use_cache={use_cache})...")
        visitor_player_stats = self.get_player_stats(visitor_team_id, game_date, use_cache=use_cache)
        
        return {
            # Star player statistics
            'home_star_ppg': home_player_stats['star_ppg'],
            'home_star_usage': home_player_stats['star_usage'],
            'home_star_mpg': home_player_stats['star_mpg'],
            'visitor_star_ppg': visitor_player_stats['star_ppg'],
            'visitor_star_usage': visitor_player_stats['star_usage'],
            'visitor_star_mpg': visitor_player_stats['star_mpg'],
            
            # Star player differences
            'star_ppg_diff': home_player_stats['star_ppg'] - visitor_player_stats['star_ppg'],
            'star_usage_diff': home_player_stats['star_usage'] - visitor_player_stats['star_usage'],
            'star_mpg_diff': home_player_stats['star_mpg'] - visitor_player_stats['star_mpg'],
            
            # Top 3 players aggregate
            'home_top3_ppg_avg': home_player_stats['top3_ppg_avg'],
            'home_top3_mpg_avg': home_player_stats['top3_mpg_avg'],
            'home_top3_impact_avg': home_player_stats['top3_impact_avg'],
            'visitor_top3_ppg_avg': visitor_player_stats['top3_ppg_avg'],
            'visitor_top3_mpg_avg': visitor_player_stats['top3_mpg_avg'],
            'visitor_top3_impact_avg': visitor_player_stats['top3_impact_avg'],
            
            # Top 3 differences
            'top3_ppg_diff': home_player_stats['top3_ppg_avg'] - visitor_player_stats['top3_ppg_avg'],
            'top3_mpg_diff': home_player_stats['top3_mpg_avg'] - visitor_player_stats['top3_mpg_avg'],
            'top3_impact_diff': home_player_stats['top3_impact_avg'] - visitor_player_stats['top3_impact_avg'],
        }

