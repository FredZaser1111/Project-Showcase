"""
Train ML models for NBA game prediction.
Supports multiple algorithms: Logistic Regression, Random Forest, Gradient Boosting.
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import config
from feature_engineering import FeatureEngineer
from api_client import APIClient

def load_training_data(data_path: str = None) -> pd.DataFrame:
    """
    Load training data from file or create from API.
    
    Args:
        data_path: Path to training data CSV/JSON file
    
    Returns:
        DataFrame with features and target
    """
    if data_path and Path(data_path).exists():
        print(f"Loading training data from {data_path}")
        return pd.read_csv(data_path)
    
    # If no file, try to load from cached games data
    cache_dir = Path(config.DATA_DIR)
    games_file = cache_dir / 'historical_games.json'
    
    if games_file.exists():
        print(f"Loading games from {games_file}")
        with open(games_file, 'r') as f:
            games_data = json.load(f)
        
        # Create feature engineer and extract features
        print("Extracting features from historical games...")
        fe = FeatureEngineer(games_data)
        df = fe.create_training_dataset()
        
        # Save for future use
        output_path = cache_dir / 'training_data.csv'
        df.to_csv(output_path, index=False)
        print(f"Saved training data to {output_path}")
        
        return df
    
    raise FileNotFoundError(
        "No training data found. Please run collect_historical_data.py first "
        "or provide a path to training data."
    )

def calculate_time_weights(dates: pd.Series, decay_rate: float = 0.002) -> np.ndarray:
    """
    Calculate time-based sample weights using exponential decay.
    
    More recent games get higher weights (closer to 1.0), older games get lower weights.
    Uses exponential decay: weight = exp(-decay_rate * days_ago)
    
    Args:
        dates: Series of game dates (strings or datetime objects)
        decay_rate: Decay rate (higher = faster decay). Default 0.002 means:
                   - 1 year ago: ~0.48 weight
                   - 2 years ago: ~0.23 weight
                   - 3 years ago: ~0.11 weight
    
    Returns:
        Array of weights (normalized so most recent game = 1.0)
    """
    # Convert dates to datetime if they're strings
    dates_dt = pd.to_datetime(dates)
    
    # Find the most recent date (baseline)
    most_recent = dates_dt.max()
    
    # Calculate days ago for each date
    days_ago = (most_recent - dates_dt).dt.days
    
    # Calculate exponential decay weights
    weights = np.exp(-decay_rate * days_ago)
    
    # Normalize so most recent = 1.0
    weights = weights / weights.max()
    
    return weights.values

def prepare_features(df: pd.DataFrame, use_time_weights: bool = True):
    """
    Prepare features for training.
    
    Args:
        df: DataFrame with features and target
        use_time_weights: Whether to calculate time-based sample weights
    
    Returns:
        X (features), y (target), feature_names, sample_weights (or None)
    """
    # Remove outcome column if present
    target_col = 'home_team_won'
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in data")
    
    # Extract game dates before dropping columns (for time weighting)
    sample_weights = None
    if use_time_weights and 'game_date' in df.columns:
        dates = df['game_date']
        sample_weights = calculate_time_weights(dates)
        print(f"\nTime-based weighting enabled:")
        print(f"  Most recent game weight: {sample_weights.max():.4f}")
        print(f"  Oldest game weight: {sample_weights.min():.4f}")
        print(f"  Average weight: {sample_weights.mean():.4f}")
    
    y = df[target_col].values
    X = df.drop(columns=[target_col])
    
    # Remove game_date from features (it's not a feature for the model)
    if 'game_date' in X.columns:
        X = X.drop(columns=['game_date'])
    
    # Handle any remaining non-numeric columns
    X = X.select_dtypes(include=[np.number])
    
    # Fill NaN values with median
    X = X.fillna(X.median())
    
    feature_names = X.columns.tolist()
    X = X.values
    
    return X, y, feature_names, sample_weights

def train_models(X_train, y_train, X_test, y_test, feature_names, sample_weights=None):
    """
    Train multiple models and return the best one.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        feature_names: List of feature names
        sample_weights: Optional sample weights for training (time-based)
    
    Returns:
        Best model, model name, results dictionary
    """
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    }
    
    # Scale features for Logistic Regression
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    results = {}
    best_model = None
    best_score = 0
    best_name = None
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        if sample_weights is not None:
            print(f"  Using time-based sample weights (avg: {sample_weights.mean():.4f})")
        
        # Use scaled data for Logistic Regression
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train, sample_weight=sample_weights)
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train, sample_weight=sample_weights)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        
        results[name] = {
            'accuracy': accuracy,
            'auc': auc,
            'model': model,
            'scaler': scaler if name == 'Logistic Regression' else None,
        }
        
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  AUC: {auc:.4f}")
        
        if accuracy > best_score:
            best_score = accuracy
            best_model = model
            best_name = name
            if name == 'Logistic Regression':
                results['_best_scaler'] = scaler
    
    return best_model, best_name, results

def cross_validate_model(model, X, y, cv=5):
    """Perform cross-validation on a model."""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
    return scores.mean(), scores.std()

def main():
    """Main training function."""
    print("=" * 60)
    print("NBA Game Prediction Model Training")
    print("=" * 60)
    
    # Load data
    try:
        df = load_training_data()
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nTo collect data, run:")
        print("  python scripts/collect_historical_data.py")
        return
    
    print(f"\nLoaded {len(df)} training examples")
    print(f"Features: {len(df.columns) - 1}")  # -1 for target
    
    # Prepare features (with time-based weighting)
    X, y, feature_names, sample_weights = prepare_features(df, use_time_weights=True)
    print(f"\nFeature names: {feature_names}")
    
    # Split data
    # If we have sample weights, we need to split them too
    if sample_weights is not None:
        # train_test_split can split multiple arrays at once
        split_result = train_test_split(
            X, y, sample_weights, test_size=0.2, random_state=42, stratify=y
        )
        X_train, X_test, y_train, y_test, weights_train, weights_test = split_result
        # For training, use weights_train; for testing, we don't use weights (just evaluate)
        train_weights = weights_train
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        train_weights = None
    
    print(f"\nTraining set: {len(X_train)} examples")
    print(f"Test set: {len(X_test)} examples")
    
    # Train models (with time-based sample weights)
    best_model, best_name, results = train_models(X_train, y_train, X_test, y_test, feature_names, sample_weights=train_weights)
    
    print(f"\n{'=' * 60}")
    print(f"Best Model: {best_name}")
    print(f"Test Accuracy: {results[best_name]['accuracy']:.4f}")
    print(f"Test AUC: {results[best_name]['auc']:.4f}")
    print(f"{'=' * 60}")
    
    # Cross-validation on best model
    print(f"\nPerforming cross-validation on {best_name}...")
    if best_name == 'Logistic Regression':
        cv_mean, cv_std = cross_validate_model(best_model, X_train, y_train)
    else:
        cv_mean, cv_std = cross_validate_model(best_model, X_train, y_train)
    print(f"CV Accuracy: {cv_mean:.4f} (+/- {cv_std * 2:.4f})")
    
    # Save best model
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
    
    # Save training results
    from datetime import datetime
    results_summary = {
        'best_model': best_name,
        'test_accuracy': float(results[best_name]['accuracy']),
        'test_auc': float(results[best_name]['auc']),
        'cv_accuracy_mean': float(cv_mean),
        'cv_accuracy_std': float(cv_std),
        'feature_names': feature_names,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'training_date': datetime.now().isoformat(),  # Track when model was trained
    }
    
    results_path = models_dir / 'training_results.json'
    with open(results_path, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"Saved training results to {results_path}")
    print("\nTraining complete!")

if __name__ == '__main__':
    main()

