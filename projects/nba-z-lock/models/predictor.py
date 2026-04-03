"""
Prediction engine for NBA game predictions.
Loads trained model and makes predictions on new matchups.
"""
import pickle
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from feature_engineering import FeatureEngineer
from api_client import APIClient

class GamePredictor:
    """Predict game outcomes using trained ML model."""
    
    def __init__(self, model_path: str = None, games_data: list = None):
        """
        Initialize predictor with trained model.
        
        Args:
            model_path: Path to saved model file
            games_data: Historical games data for feature engineering
        """
        models_dir = Path(config.MODELS_DIR)
        
        # Load model
        model_file = model_path or (models_dir / 'best_model.pkl')
        if not model_file.exists():
            raise FileNotFoundError(
                f"Model not found at {model_file}. Please train the model first."
            )
        
        with open(model_file, 'rb') as f:
            loaded_model = pickle.load(f)
        
        # Initialize scaler
        self.scaler = None
        
        # Handle case where model was saved as a dictionary (from stacking ensemble training)
        model_dict = None
        if isinstance(loaded_model, dict):
            model_dict = loaded_model
            # Check if it's a stacking ensemble structure
            if 'meta_learner' in loaded_model or 'is_stacking' in loaded_model:
                # If stacking was used but best model wasn't stacking, use meta_learner
                # If is_stacking is False, use meta_learner as the best model
                if loaded_model.get('is_stacking', False):
                    # Stacking ensemble is active - would need to handle differently
                    # For now, use meta_learner as fallback
                    self.model = loaded_model.get('meta_learner')
                    if self.model is None:
                        raise ValueError("Stacking ensemble model found but meta_learner is missing")
                else:
                    # Not using stacking, use meta_learner as the best model
                    self.model = loaded_model.get('meta_learner')
                    if self.model is None:
                        raise ValueError("Model dictionary found but meta_learner is missing")
                
                # Override scaler if present in dict
                if loaded_model.get('scaler') is not None:
                    self.scaler = loaded_model.get('scaler')
            else:
                raise ValueError(f"Unknown model dictionary format. Keys: {list(loaded_model.keys())}")
        else:
            # Model is a scikit-learn model object
            self.model = loaded_model
        
        # Load scaler if it exists (for Logistic Regression)
        # Only load from file if not already loaded from dict
        if self.scaler is None:
            scaler_file = models_dir / 'scaler.pkl'
            if scaler_file.exists():
                with open(scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
        
        # Load feature selector if it exists (for advanced training)
        selector_file = models_dir / 'feature_selector.pkl'
        self.selector = None
        if selector_file.exists():
            with open(selector_file, 'rb') as f:
                self.selector = pickle.load(f)
        
        # Load feature names
        # First check if they're in the model dict
        if model_dict and 'feature_names' in model_dict:
            self.feature_names = model_dict['feature_names']
        else:
            feature_names_file = models_dir / 'feature_names.json'
            if feature_names_file.exists():
                with open(feature_names_file, 'r') as f:
                    self.feature_names = json.load(f)
            else:
                # Default feature names (should match training)
                self.feature_names = [
                    'home_win_pct', 'home_wins', 'home_losses',
                    'visitor_win_pct', 'visitor_wins', 'visitor_losses',
                    'home_home_win_pct', 'visitor_away_win_pct',
                    'home_recent_win_pct', 'home_recent_avg_points_for',
                    'home_recent_avg_points_against',
                    'visitor_recent_win_pct', 'visitor_recent_avg_points_for',
                    'visitor_recent_avg_points_against',
                    'h2h_home_win_pct', 'h2h_games_played',
                    'home_rest_days', 'visitor_rest_days', 'rest_days_diff'
                ]
        
        # Initialize feature engineer with games data
        self.games_data = games_data or []
        if self.games_data:
            self.fe = FeatureEngineer(self.games_data)
        else:
            self.fe = None
    
    def _sanitize_features(self, features: Dict) -> Dict:
        """
        Sanitize features dictionary by replacing NaN and None values with 0.0.
        This prevents JSON serialization errors.
        """
        sanitized = {}
        for key, value in features.items():
            try:
                if value is None:
                    sanitized[key] = 0.0
                elif isinstance(value, (int, float)):
                    if np.isnan(value) or np.isinf(value):
                        sanitized[key] = 0.0
                    else:
                        sanitized[key] = float(value)
                else:
                    sanitized[key] = value
            except (ValueError, TypeError):
                sanitized[key] = 0.0
        return sanitized
    
    def probability_to_moneyline(self, probability: float) -> Dict[str, int]:
        """
        Convert win probability to money line odds.
        
        Args:
            probability: Win probability (0 to 1)
        
        Returns:
            Dict with 'favorite' and 'underdog' money line odds
        """
        if probability >= 0.5:
            # Favorite
            favorite_ml = int(-100 * probability / (1 - probability))
            if favorite_ml > -100:
                favorite_ml = -110  # Minimum favorite odds
            underdog_ml = int(100 * (1 - probability) / probability)
            if underdog_ml < 100:
                underdog_ml = 110  # Minimum underdog odds
        else:
            # Underdog
            underdog_ml = int(100 * (1 - probability) / probability)
            if underdog_ml < 100:
                underdog_ml = 110
            favorite_ml = int(-100 * probability / (1 - probability))
            if favorite_ml > -100:
                favorite_ml = -110
        
        return {
            'favorite': favorite_ml,
            'underdog': underdog_ml
        }
    
    def predict(self, home_team_id: int, visitor_team_id: int,
                game_date: datetime = None, games_data: list = None,
                injury_data: Optional[Dict] = None) -> Dict:
        """
        Predict game outcome.
        
        Args:
            home_team_id: Home team ID
            visitor_team_id: Visitor team ID
            game_date: Date of the game (defaults to today)
            games_data: Historical games data (if not provided in init)
            injury_data: Optional manual injury data dict with 'home' and 'visitor' keys
        
        Returns:
            Prediction dictionary with probabilities, money line, etc.
        """
        if games_data:
            print(f"  [PREDICTOR] Initializing FeatureEngineer with {len(games_data)} games...")
            try:
                self.fe = FeatureEngineer(games_data)
                print(f"  [PREDICTOR] FeatureEngineer initialized successfully")
                print(f"  [PREDICTOR] games_df shape: {self.fe.games_df.shape if hasattr(self.fe, 'games_df') else 'N/A'}")
            except Exception as fe_error:
                print(f"  [PREDICTOR] ERROR initializing FeatureEngineer: {fe_error}")
                import traceback
                print(traceback.format_exc())
                raise
        elif not self.fe:
            raise ValueError("No games data provided for feature engineering")
        
        if game_date is None:
            game_date = datetime.now()
        
        # Extract features (with optional manual injury data)
        print(f"  Extracting features for prediction...")
        print(f"  Injury data passed to feature engineering: {injury_data}")
        features = self.fe.extract_features_for_prediction(
            home_team_id, visitor_team_id, game_date, injury_data=injury_data
        )
        print(f"  Extracted {len(features)} features")
        
        # Only use features that the model was trained with
        # Handle missing features by using 0 as default
        print(f"  Model expects {len(self.feature_names)} features")
        feature_values = []
        missing_features = []
        for name in self.feature_names:
            if name in features:
                feature_values.append(features[name])
            else:
                # Feature not in extracted features - use default value
                missing_features.append(name)
                feature_values.append(0.0)
        
        if missing_features:
            print(f"  Warning: {len(missing_features)} features missing: {missing_features[:5]}...")
        
        # Convert to array in correct order and sanitize NaN values
        # Replace any NaN or None values with 0.0 before creating array
        sanitized_values = []
        for val in feature_values:
            if val is None:
                sanitized_values.append(0.0)
            elif isinstance(val, (int, float)):
                if np.isnan(val) or np.isinf(val):
                    sanitized_values.append(0.0)
                else:
                    sanitized_values.append(float(val))
            else:
                try:
                    float_val = float(val)
                    if np.isnan(float_val) or np.isinf(float_val):
                        sanitized_values.append(0.0)
                    else:
                        sanitized_values.append(float_val)
                except (ValueError, TypeError):
                    sanitized_values.append(0.0)
        
        feature_array = np.array([sanitized_values])
        print(f"  Feature array shape: {feature_array.shape}")
        
        # Double-check for any remaining NaN values
        if np.any(np.isnan(feature_array)) or np.any(np.isinf(feature_array)):
            print(f"  WARNING: Found NaN/Inf in feature array, replacing with 0.0")
            feature_array = np.nan_to_num(feature_array, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Scale if needed (scaler expects the same number of features as training)
        if self.scaler:
            print(f"  Scaler found, checking compatibility...")
            # Check if scaler expects the same number of features
            if hasattr(self.scaler, 'n_features_in_') and self.scaler.n_features_in_ != len(feature_values):
                print(f"Warning: Scaler expects {self.scaler.n_features_in_} features, but got {len(feature_values)}. Skipping scaling.")
            elif hasattr(self.scaler, 'mean_') and len(self.scaler.mean_) != len(feature_values):
                print(f"Warning: Scaler was trained with {len(self.scaler.mean_)} features, but got {len(feature_values)}. Skipping scaling.")
            else:
                try:
                    feature_array = self.scaler.transform(feature_array)
                except ValueError as e:
                    print(f"Warning: Scaler error: {e}. Skipping scaling.")
                    # Continue without scaling
        
        # Apply feature selection if needed
        if self.selector:
            print(f"  Applying feature selector...")
            expected_features = None
            if hasattr(self.selector, 'n_features_in_'):
                expected_features = self.selector.n_features_in_
            elif hasattr(self.selector, 'n_features_'):
                expected_features = self.selector.n_features_
            
            if expected_features:
                print(f"  Selector expects {expected_features} features")
            print(f"  We have {feature_array.shape[1]} features")
            
            # Check if feature count matches
            if expected_features and expected_features != feature_array.shape[1]:
                print(f"  WARNING: Feature count mismatch! Selector expects {expected_features}, got {feature_array.shape[1]}")
                print(f"  Skipping feature selection to avoid error")
                # Don't apply selector - continue with all features
            else:
                try:
                    feature_array = self.selector.transform(feature_array)
                    print(f"  After selection, shape: {feature_array.shape}")
                except (ValueError, AttributeError) as e:
                    print(f"  WARNING: Feature selection failed: {e}")
                    print(f"  Error type: {type(e).__name__}")
                    print(f"  Continuing without feature selection...")
                    # Continue with original feature array
        
        # Predict
        print(f"  Running model prediction...")
        print(f"  Final feature array shape: {feature_array.shape}")
        home_win_prob = self.model.predict_proba(feature_array)[0][1]
        print(f"  Prediction complete!")
        visitor_win_prob = 1 - home_win_prob
        
        # Get money line odds
        moneyline = self.probability_to_moneyline(home_win_prob)
        
        # Determine favorite
        if home_win_prob >= 0.5:
            favorite_team = 'home'
            favorite_ml = moneyline['favorite']
            underdog_ml = moneyline['underdog']
        else:
            favorite_team = 'visitor'
            favorite_ml = moneyline['underdog']
            underdog_ml = moneyline['favorite']
        
        # Confidence score (how far from 0.5)
        confidence = abs(home_win_prob - 0.5) * 2  # 0 to 1 scale
        
        # Sanitize features to remove NaN values before returning
        sanitized_features = self._sanitize_features(features)
        
        return {
            'home_win_probability': float(home_win_prob),
            'visitor_win_probability': float(visitor_win_prob),
            'predicted_winner': 'home' if home_win_prob >= 0.5 else 'visitor',
            'favorite_team': favorite_team,
            'moneyline': {
                'home': moneyline['favorite'] if favorite_team == 'home' else moneyline['underdog'],
                'visitor': moneyline['underdog'] if favorite_team == 'home' else moneyline['favorite'],
            },
            'confidence': float(confidence),
            'features': sanitized_features,
        }

