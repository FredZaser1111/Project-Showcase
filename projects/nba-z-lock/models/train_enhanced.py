"""
Enhanced ML model training with more data and better hyperparameters.
Collects more seasons and uses improved model configurations.
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

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import config
from feature_engineering import FeatureEngineer

# Try to import XGBoost if available
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("Note: XGBoost not available. Install with: pip install xgboost")

def load_training_data(data_path: str = None) -> pd.DataFrame:
    """Load training data from file or create from API."""
    if data_path and Path(data_path).exists():
        print(f"Loading training data from {data_path}")
        return pd.read_csv(data_path)
    
    cache_dir = Path(config.DATA_DIR)
    games_file = cache_dir / 'historical_games.json'
    
    if games_file.exists():
        print(f"Loading games from {games_file}")
        with open(games_file, 'r') as f:
            games_data = json.load(f)
        
        print("Extracting features from historical games...")
        fe = FeatureEngineer(games_data)
        df = fe.create_training_dataset()
        
        output_path = cache_dir / 'training_data.csv'
        df.to_csv(output_path, index=False)
        print(f"Saved training data to {output_path}")
        
        return df
    
    raise FileNotFoundError(
        "No training data found. Please run collect_historical_data.py first."
    )

def prepare_features(df: pd.DataFrame):
    """Prepare features for training."""
    target_col = 'home_team_won'
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in data")
    
    y = df[target_col].values
    X = df.drop(columns=[target_col])
    X = X.select_dtypes(include=[np.number])
    X = X.fillna(X.median())
    
    feature_names = X.columns.tolist()
    X = X.values
    
    return X, y, feature_names

def train_enhanced_models(X_train, y_train, X_test, y_test, feature_names):
    """
    Train models with improved hyperparameters.
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'Logistic Regression': LogisticRegression(
            max_iter=2000, 
            random_state=42,
            C=1.0,
            solver='lbfgs'
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=200,  # Increased from 100
            max_depth=15,      # Added depth limit
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42, 
            n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=200,  # Increased from 100
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            random_state=42
        ),
    }
    
    # Add XGBoost if available
    if XGBOOST_AVAILABLE:
        models['XGBoost'] = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss'
        )
    
    results = {}
    best_model = None
    best_score = 0
    best_name = None
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        try:
            if name == 'Logistic Regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            
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
        except Exception as e:
            print(f"  Error training {name}: {e}")
            continue
    
    return best_model, best_name, results

def main():
    """Main enhanced training function."""
    print("=" * 60)
    print("NBA Z-LOCK - Enhanced Model Training")
    print("=" * 60)
    
    # Load data
    try:
        df = load_training_data()
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        return
    
    print(f"\nLoaded {len(df)} training examples")
    print(f"Features: {len(df.columns) - 1}")
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    print(f"\nFeature names: {feature_names}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} examples")
    print(f"Test set: {len(X_test)} examples")
    
    # Train enhanced models
    best_model, best_name, results = train_enhanced_models(
        X_train, y_train, X_test, y_test, feature_names
    )
    
    print(f"\n{'=' * 60}")
    print(f"Best Model: {best_name}")
    print(f"Test Accuracy: {results[best_name]['accuracy']:.4f}")
    print(f"Test AUC: {results[best_name]['auc']:.4f}")
    print(f"{'=' * 60}")
    
    # Cross-validation
    print(f"\nPerforming cross-validation on {best_name}...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    if best_name == 'Logistic Regression':
        from sklearn.model_selection import cross_val_score
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            best_model, X_train_scaled, y_train, cv=skf, scoring='accuracy'
        )
    else:
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            best_model, X_train, y_train, cv=skf, scoring='accuracy'
        )
    
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
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
    
    # Save results
    results_summary = {
        'best_model': best_name,
        'test_accuracy': float(results[best_name]['accuracy']),
        'test_auc': float(results[best_name]['auc']),
        'cv_accuracy_mean': float(cv_mean),
        'cv_accuracy_std': float(cv_std),
        'feature_names': feature_names,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'enhanced_training': True,
    }
    
    results_path = models_dir / 'training_results.json'
    with open(results_path, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"Saved training results to {results_path}")
    print("\nEnhanced training complete!")

if __name__ == '__main__':
    main()

