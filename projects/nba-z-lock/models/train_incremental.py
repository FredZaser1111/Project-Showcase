"""
Incremental training script - trains on new games since last training.
Loads existing training data and adds new games, then retrains the model.
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

import config
from feature_engineering import FeatureEngineer
from train_model import train_models, prepare_features, cross_validate_model

def get_last_training_date():
    """Get the date when the model was last trained."""
    results_file = Path(config.MODELS_DIR) / 'training_results.json'
    if results_file.exists():
        with open(results_file, 'r') as f:
            results = json.load(f)
            # Check if we have a training_date field
            if 'training_date' in results:
                return datetime.fromisoformat(results['training_date'])
            # Otherwise, use file modification time as proxy
            return datetime.fromtimestamp(results_file.stat().st_mtime)
    return None

def get_new_games_since(since_date: datetime):
    """Get games from historical_games.json that are newer than since_date."""
    games_file = Path(config.DATA_DIR) / 'historical_games.json'
    if not games_file.exists():
        return []
    
    with open(games_file, 'r') as f:
        all_games = json.load(f)
    
    if since_date is None:
        # No previous training, return all games
        return all_games
    
    new_games = []
    for game in all_games:
        # Try to parse game date - could be in various formats
        game_date_str = game.get('date') or game.get('game_date') or game.get('date_time')
        if not game_date_str:
            continue
        
        try:
            # Try different date formats
            if isinstance(game_date_str, str):
                # Try ISO format first
                try:
                    game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                except:
                    # Try other formats
                    try:
                        game_date = datetime.strptime(game_date_str, '%Y-%m-%d')
                    except:
                        try:
                            game_date = datetime.strptime(game_date_str, '%Y-%m-%d %H:%M:%S')
                        except:
                            # Skip if we can't parse
                            continue
            else:
                continue
            
            # Only include games after the last training date
            if game_date > since_date:
                new_games.append(game)
        except Exception as e:
            # Skip games we can't parse
            print(f"Warning: Could not parse date for game {game.get('id', 'unknown')}: {e}")
            continue
    
    return new_games

def load_existing_training_data():
    """Load existing training data CSV if it exists."""
    training_data_file = Path(config.DATA_DIR) / 'training_data.csv'
    if training_data_file.exists():
        print(f"Loading existing training data from {training_data_file}")
        return pd.read_csv(training_data_file)
    return None

def create_training_data_from_games(games_data):
    """Create training dataset from games data."""
    print(f"Extracting features from {len(games_data)} games...")
    fe = FeatureEngineer(games_data)
    df = fe.create_training_dataset()
    return df

def main():
    """Main incremental training function."""
    print("=" * 60)
    print("NBA Game Prediction - Incremental Training")
    print("=" * 60)
    
    # Get last training date
    last_training_date = get_last_training_date()
    if last_training_date:
        print(f"\nLast training date: {last_training_date.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("\nNo previous training found - will train on all available data")
    
    # Get new games
    print("\nIdentifying new games...")
    new_games = get_new_games_since(last_training_date)
    print(f"Found {len(new_games)} new games since last training")
    
    if len(new_games) == 0:
        print("\nNo new games found. Nothing to train on!")
        print("To do a full retrain, run: python models/train_model.py")
        return
    
    # Load existing training data
    existing_df = load_existing_training_data()
    
    # Create training data from new games
    new_df = create_training_data_from_games(new_games)
    
    # Combine datasets
    if existing_df is not None:
        print(f"\nCombining datasets:")
        print(f"  Existing samples: {len(existing_df)}")
        print(f"  New samples: {len(new_df)}")
        
        # Combine and remove duplicates (based on feature similarity or game ID if available)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Remove exact duplicates
        combined_df = combined_df.drop_duplicates()
        print(f"  Combined (after dedup): {len(combined_df)}")
    else:
        print("\nNo existing training data found - using only new games")
        combined_df = new_df
    
    # Save updated training data
    training_data_file = Path(config.DATA_DIR) / 'training_data.csv'
    combined_df.to_csv(training_data_file, index=False)
    print(f"\nSaved updated training data to {training_data_file}")
    
    # Prepare features (with time-based weighting)
    print("\nPreparing features...")
    X, y, feature_names, sample_weights = prepare_features(combined_df, use_time_weights=True)
    print(f"Feature names: {feature_names[:5]}... ({len(feature_names)} total)")
    
    # Split data (including sample weights if available)
    if sample_weights is not None:
        # train_test_split can split multiple arrays at once
        split_result = train_test_split(
            X, y, sample_weights, test_size=0.2, random_state=42, stratify=y
        )
        X_train, X_test, y_train, y_test, weights_train, weights_test = split_result
        train_weights = weights_train
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        train_weights = None
    
    print(f"\nTraining set: {len(X_train)} examples")
    print(f"Test set: {len(X_test)} examples")
    
    # Train models (with time-based sample weights)
    print("\nTraining models...")
    best_model, best_name, results = train_models(X_train, y_train, X_test, y_test, feature_names, sample_weights=train_weights)
    
    print(f"\n{'=' * 60}")
    print(f"Best Model: {best_name}")
    print(f"Test Accuracy: {results[best_name]['accuracy']:.4f}")
    print(f"Test AUC: {results[best_name]['auc']:.4f}")
    print(f"{'=' * 60}")
    
    # Cross-validation
    print(f"\nPerforming cross-validation on {best_name}...")
    cv_mean, cv_std = cross_validate_model(best_model, X_train, y_train)
    print(f"CV Accuracy: {cv_mean:.4f} (+/- {cv_std * 2:.4f})")
    
    # Save model
    models_dir = Path(config.MODELS_DIR)
    model_path = models_dir / 'best_model.pkl'
    scaler_path = models_dir / 'scaler.pkl'
    feature_names_path = models_dir / 'feature_names.json'
    
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)
    
    if best_name == 'Logistic Regression' and results.get('_best_scaler'):
        with open(scaler_path, 'wb') as f:
            pickle.dump(results['_best_scaler'], f)
    
    with open(feature_names_path, 'w') as f:
        json.dump(feature_names, f)
    
    print(f"\nSaved model to {model_path}")
    if best_name == 'Logistic Regression':
        print(f"Saved scaler to {scaler_path}")
    print(f"Saved feature names to {feature_names_path}")
    
    # Update training results with new date
    results_summary = {
        'best_model': best_name,
        'test_accuracy': float(results[best_name]['accuracy']),
        'test_auc': float(results[best_name]['auc']),
        'cv_accuracy_mean': float(cv_mean),
        'cv_accuracy_std': float(cv_std),
        'feature_names': feature_names,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'training_date': datetime.now().isoformat(),
        'new_games_added': len(new_games),
        'total_games': len(combined_df),
    }
    
    results_path = models_dir / 'training_results.json'
    with open(results_path, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"Saved training results to {results_path}")
    print(f"\nTraining date updated to: {datetime.now().isoformat()}")
    print(f"New games added: {len(new_games)}")
    print("\nIncremental training complete! ✅")

if __name__ == '__main__':
    main()

