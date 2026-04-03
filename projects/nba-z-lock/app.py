"""
Flask web application for NBA game predictions.
"""
from flask import Flask, render_template, jsonify, request
import json
import time
from pathlib import Path
from datetime import datetime
import sys
import os
import numpy as np

import config
from models.predictor import GamePredictor

# Choose API client based on config
if config.API_PROVIDER == 'nba_api':
    try:
        from api_client_nba import NBAAPIClient
        api_client = NBAAPIClient()
    except ImportError:
        print("Warning: NBA_API not available, falling back to Ball Don't Lie API")
        from api_client import APIClient
        api_client = APIClient()
else:
    from api_client import APIClient
    api_client = APIClient()

app = Flask(__name__)

# Initialize predictor (lazy loading)
predictor = None

def get_predictor():
    """Get or initialize the predictor."""
    global predictor
    if predictor is None:
        # Load historical games data
        games_file = Path(config.DATA_DIR) / 'historical_games.json'
        games_data = []
        if games_file.exists():
            with open(games_file, 'r') as f:
                games_data = json.load(f)
        
        try:
            print(f"[GET_PREDICTOR] Initializing GamePredictor with {len(games_data)} games...")
            predictor = GamePredictor(games_data=games_data)
            print(f"[GET_PREDICTOR] GamePredictor initialized successfully")
        except FileNotFoundError as e:
            # Model not trained yet
            print(f"[GET_PREDICTOR] Model file not found: {e}")
            predictor = None
        except Exception as e:
            print(f"[GET_PREDICTOR] ERROR initializing GamePredictor: {e}")
            import traceback
            print(traceback.format_exc())
            predictor = None
    
    return predictor

@app.route('/')
def index():
    """Home page with team selector."""
    # Add cache-busting timestamp to ensure fresh static files
    cache_bust = int(datetime.now().timestamp())
    return render_template('index.html', cache_bust=cache_bust)

@app.route('/api/teams')
def get_teams():
    """Get list of all NBA teams."""
    try:
        # Try to load from cache first
        teams_file = Path(config.DATA_DIR) / 'teams.json'
        if teams_file.exists():
            with open(teams_file, 'r') as f:
                teams = json.load(f)
        else:
            # Fetch from API
            teams = api_client.get_all_teams()
            # Cache it
            with open(teams_file, 'w') as f:
                json.dump(teams, f, indent=2)
        
        return jsonify({
            'success': True,
            'teams': teams
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict game outcome."""
    start_time = time.time()
    timeout_seconds = 25  # Server-side timeout
    
    try:
        print("\n" + "=" * 60)
        print("PREDICTION REQUEST RECEIVED")
        print("=" * 60)
        data = request.get_json()
        home_team_id = int(data.get('home_team_id'))
        visitor_team_id = int(data.get('visitor_team_id'))
        game_date = data.get('game_date')  # Optional, format: YYYY-MM-DD
        injury_data = data.get('injury_data')  # Optional manual injury data
        
        print(f"Home Team ID: {home_team_id}")
        print(f"Visitor Team ID: {visitor_team_id}")
        print(f"Game Date: {game_date}")
        print(f"Injury Data Received: {injury_data}")
        
        # Get predictor
        print(f"[PREDICT] Getting predictor...")
        try:
            pred = get_predictor()
            if pred is None:
                return jsonify({
                    'success': False,
                    'error': 'Model not trained yet. Please train the model first.'
                }), 400
            print(f"[PREDICT] Predictor obtained successfully")
            print(f"[PREDICT] Predictor has fe: {hasattr(pred, 'fe') and pred.fe is not None}")
            print(f"[PREDICT] Predictor has games_data: {hasattr(pred, 'games_data') and len(pred.games_data) if pred.games_data else 0} games")
        except Exception as pred_error:
            print(f"[PREDICT] ERROR getting predictor: {pred_error}")
            import traceback
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Failed to get predictor: {str(pred_error)}',
                'traceback': traceback.format_exc() if config.FLASK_DEBUG else None
            }), 500
        
        # Parse game date if provided
        game_datetime = None
        if game_date:
            try:
                game_datetime = datetime.strptime(game_date, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Convert player names to injury data format if needed
        print(f"\nProcessing injury data...")
        print(f"Injury data type: {type(injury_data)}")
        print(f"Injury data content: {injury_data}")
        
        if injury_data and isinstance(injury_data, dict) and 'injured_players' in injury_data:
            print("Converting player probabilities to fractional availability...")
            # Convert player probabilities to fractional key/star player availability
            from player_classifier import PlayerClassifier
            classifier = PlayerClassifier()
            
            now = datetime.now()
            if now.month >= 10:
                season = f"{now.year}-{str(now.year + 1)[2:]}"
            else:
                season = f"{now.year - 1}-{str(now.year)[2:]}"
            
            # Initialize converted injury data
            converted_injury_data = {}
            
            def calculate_team_availability(team_id, player_probabilities_dict):
                """
                Calculate fractional availability based on player probabilities.
                Returns: { 'key_players_available': float, 'star_player_available': float }
                """
                try:
                    # Get roster with classifications
                    players = classifier.get_classification_for_roster(team_id, season)
                    
                    if not players:
                        # Fallback: assume all available if we can't get roster
                        return {'key_players_available': 3.0, 'star_player_available': 1.0}
                    
                    # Count star and key players
                    star_players = [p for p in players if p['type'] == 'star']
                    key_players = [p for p in players if p['type'] == 'key']
                    
                    # Calculate star player availability (weighted average)
                    star_available = 1.0  # Default: full availability
                    if star_players:
                        star_probs = []
                        for star in star_players:
                            player_name = star['name']
                            # If player is in the probability dict, use that value, otherwise assume 1.0 (available)
                            prob = player_probabilities_dict.get(player_name, 1.0)
                            # Ensure prob is a valid number (handle None, NaN, etc.)
                            try:
                                prob = float(prob) if prob is not None else 1.0
                                if np.isnan(prob) or np.isinf(prob):
                                    prob = 1.0
                                star_probs.append(prob)
                            except (ValueError, TypeError):
                                star_probs.append(1.0)  # Default to available if invalid
                        # Use the star player with lowest probability (most conservative)
                        star_available = min(star_probs) if star_probs else 1.0
                    
                    # Calculate key players availability (sum of probabilities, max 3.0)
                    key_available = min(3.0, len(key_players))  # Default: all key players available
                    if key_players:
                        key_probs_sum = 0.0
                        for key_player in key_players:
                            player_name = key_player['name']
                            # If player is in the probability dict, use that value, otherwise assume 1.0 (available)
                            prob = player_probabilities_dict.get(player_name, 1.0)
                            # Ensure prob is a valid number (handle None, NaN, etc.)
                            try:
                                prob = float(prob) if prob is not None else 1.0
                                if np.isnan(prob) or np.isinf(prob):
                                    prob = 1.0
                                key_probs_sum += prob
                            except (ValueError, TypeError):
                                key_probs_sum += 1.0  # Default to available if invalid
                        # Cap at 3.0 (typical number of key players)
                        key_available = min(3.0, key_probs_sum)
                    
                    return {
                        'key_players_available': round(key_available, 3),
                        'star_player_available': round(star_available, 3)
                    }
                except Exception as e:
                    print(f"[INJURY] Error calculating availability: {e}")
                    import traceback
                    print(traceback.format_exc())
                    # Fallback: assume all available
                    return {'key_players_available': 3.0, 'star_player_available': 1.0}
            
            # Process home team
            home_player_probs = injury_data['injured_players'].get('home', {})
            if isinstance(home_player_probs, dict) and len(home_player_probs) > 0:
                print(f"[INJURY] Processing {len(home_player_probs)} home players with probabilities...")
                converted_injury_data['home'] = calculate_team_availability(home_team_id, home_player_probs)
                print(f"[INJURY] Home team availability: {converted_injury_data['home']}")
            else:
                # No injuries for home team
                converted_injury_data['home'] = {
                    'key_players_available': 3.0,
                    'star_player_available': 1.0
                }
            
            # Process visitor team
            visitor_player_probs = injury_data['injured_players'].get('visitor', {})
            if isinstance(visitor_player_probs, dict) and len(visitor_player_probs) > 0:
                print(f"[INJURY] Processing {len(visitor_player_probs)} visitor players with probabilities...")
                converted_injury_data['visitor'] = calculate_team_availability(visitor_team_id, visitor_player_probs)
                print(f"[INJURY] Visitor team availability: {converted_injury_data['visitor']}")
            else:
                # No injuries for visitor team
                converted_injury_data['visitor'] = {
                    'key_players_available': 3.0,
                    'star_player_available': 1.0
                }
            
            # Use converted injury data
            injury_data = converted_injury_data
            print(f"Converted injury data (fractional): {injury_data}")
        else:
            # No injury data provided, set to None
            injury_data = None
            print("No injury data to process")
        
        print(f"\nMaking prediction with injury_data: {injury_data}")
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Prediction took too long ({elapsed:.1f}s), aborting")
        
        # Make prediction with optional injury data
        print(f"\n[PREDICT] Calling pred.predict()...")
        print(f"[PREDICT] Home: {home_team_id}, Visitor: {visitor_team_id}, Date: {game_datetime}")
        print(f"[PREDICT] Injury data: {injury_data}")
        try:
            prediction = pred.predict(
                home_team_id=home_team_id,
                visitor_team_id=visitor_team_id,
                game_date=game_datetime,
                injury_data=injury_data
            )
            print(f"[PREDICT] Prediction successful!")
        except Exception as pred_error:
            print(f"[PREDICT] ERROR in pred.predict(): {pred_error}")
            import traceback
            print(traceback.format_exc())
            raise  # Re-raise to be caught by outer exception handler
        
        elapsed = time.time() - start_time
        print(f"Prediction successful! (took {elapsed:.2f}s)")
        print(f"Home Win Probability: {prediction['home_win_probability']:.2%}")
        print(f"Visitor Win Probability: {prediction['visitor_win_probability']:.2%}")
        
        # Get team names
        teams_file = Path(config.DATA_DIR) / 'teams.json'
        teams = {}
        if teams_file.exists():
            with open(teams_file, 'r') as f:
                teams_list = json.load(f)
                teams = {t['id']: t for t in teams_list}
        
        home_team = teams.get(home_team_id, {'full_name': f'Team {home_team_id}'})
        visitor_team = teams.get(visitor_team_id, {'full_name': f'Team {visitor_team_id}'})
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'home_team': home_team,
            'visitor_team': visitor_team
        })
    except TimeoutError as e:
        elapsed = time.time() - start_time
        print(f"\n[TIMEOUT] Prediction timed out after {elapsed:.2f} seconds: {e}")
        return jsonify({
            'success': False,
            'error': f'Prediction timed out after {elapsed:.1f} seconds. Please try again or reduce the number of features.',
            'timeout': True
        }), 504
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"ERROR in predict endpoint (after {elapsed:.2f}s)")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"\nFull traceback:")
        print(error_trace)
        print(f"{'='*60}\n")
        # Always include traceback in response for debugging (even if FLASK_DEBUG is False)
        # This helps us see the error
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace,  # Always include for now
            'error_type': type(e).__name__,
            'elapsed_seconds': round(elapsed, 2)
        }), 500

@app.route('/api/roster/<int:team_id>')
def get_team_roster(team_id):
    """Get team roster with player names and improved classification."""
    try:
        from player_classifier import PlayerClassifier
        import traceback
        
        # Get current season
        now = datetime.now()
        if now.month >= 10:
            season = f"{now.year}-{str(now.year + 1)[2:]}"
        else:
            season = f"{now.year - 1}-{str(now.year)[2:]}"
        
        # Use improved player classifier
        print(f"\n[ROSTER] Fetching roster for team {team_id}, season {season}")
        classifier = PlayerClassifier()
        players = classifier.get_classification_for_roster(team_id, season)
        
        print(f"[ROSTER] Retrieved {len(players)} players")
        
        # If still empty after fallback, try one more time with basic roster
        if len(players) == 0:
            print(f"[ROSTER] WARNING: No players returned, trying direct roster fetch...")
            try:
                from nba_api.stats.endpoints import commonteamroster
                roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
                roster_df = roster.get_data_frames()[0]
                
                print(f"[ROSTER] Direct roster fetch returned {len(roster_df)} players")
                
                # Return all players as role players if classification fails
                for _, row in roster_df.iterrows():
                    players.append({
                        'player_id': int(row['PLAYER_ID']),
                        'name': row['PLAYER'],
                        'position': row.get('POSITION', ''),
                        'type': 'role'  # Default to role if we can't classify
                    })
                print(f"[ROSTER] Successfully added {len(players)} players from direct fetch")
            except Exception as fallback_error:
                print(f"[ROSTER] Fallback also failed: {fallback_error}")
                import traceback
                print(traceback.format_exc())
        
        # Format for frontend
        formatted_players = []
        star_player_id = None
        
        for player in players:
            if player['type'] == 'star' and star_player_id is None:
                star_player_id = player['player_id']
            
            formatted_players.append({
                'id': player['player_id'],
                'name': player['name'],
                'position': player.get('position', ''),
                'type': player['type']
            })
        
        return jsonify({
            'success': True,
            'players': formatted_players,
            'star_player': star_player_id,
            'key_players': [p['id'] for p in formatted_players if p['type'] == 'key']
        })
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_team_roster: {e}")
        print(error_trace)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats/<int:team_id>')
def get_team_stats(team_id):
    """Get team statistics."""
    try:
        # For now, return basic info
        # In a full implementation, you'd fetch detailed stats
        teams_file = Path(config.DATA_DIR) / 'teams.json'
        if teams_file.exists():
            with open(teams_file, 'r') as f:
                teams = json.load(f)
                team = next((t for t in teams if t['id'] == team_id), None)
                if team:
                    return jsonify({
                        'success': True,
                        'team': team
                    })
        
        return jsonify({
            'success': False,
            'error': 'Team not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/model/status')
def model_status():
    """Get model training status."""
    model_file = Path(config.MODELS_DIR) / 'best_model.pkl'
    results_file = Path(config.MODELS_DIR) / 'training_results.json'
    
    status = {
        'trained': model_file.exists(),
        'model_path': str(model_file) if model_file.exists() else None,
    }
    
    if results_file.exists():
        with open(results_file, 'r') as f:
            results = json.load(f)
            status['training_results'] = results
    
    return jsonify(status)

if __name__ == '__main__':
    print("=" * 60)
    print("NBA Z-LOCK")
    print("=" * 60)
    print(f"Starting Flask server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"API Tier: {config.API_TIER}")
    print(f"Rate Limit: {config.RATE_LIMIT_PER_MIN} req/min")
    print("=" * 60)
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

