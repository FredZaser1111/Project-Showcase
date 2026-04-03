"""
Advanced ML model training with:
- Feature selection
- Hyperparameter tuning (GridSearchCV)
- Ensemble methods (Voting Classifier)
- Advanced preprocessing
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
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import config
from feature_engineering import FeatureEngineer

# Try to import XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

def load_training_data(data_path: str = None) -> pd.DataFrame:
    """Load training data."""
    if data_path and Path(data_path).exists():
        return pd.read_csv(data_path)
    
    cache_dir = Path(config.DATA_DIR)
    games_file = cache_dir / 'historical_games.json'
    
    if games_file.exists():
        with open(games_file, 'r') as f:
            games_data = json.load(f)
        
        print(f"\nLoading {len(games_data)} games for training...")
        print("Note: Player stats for historical games will use cached/estimated values")
        print("      to speed up training and avoid API timeouts.\n")
        
        fe = FeatureEngineer(games_data)
        df = fe.create_training_dataset()
        
        output_path = cache_dir / 'training_data.csv'
        df.to_csv(output_path, index=False)
        print(f"Training dataset saved to {output_path}")
        return df
    
    raise FileNotFoundError("No training data found.")

def prepare_features(df: pd.DataFrame):
    """Prepare features with feature selection."""
    target_col = 'home_team_won'
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found")
    
    y = df[target_col].values
    X = df.drop(columns=[target_col])
    X = X.select_dtypes(include=[np.number])
    X = X.fillna(X.median())
    
    feature_names = X.columns.tolist()
    X = X.values
    
    return X, y, feature_names

def feature_selection(X_train, y_train, X_test, feature_names, k='all'):
    """
    Select best features using statistical tests.
    """
    print(f"\nPerforming feature selection...")
    print(f"  Original features: {len(feature_names)}")
    
    # Use mutual information for feature selection
    selector = SelectKBest(score_func=mutual_info_classif, k=k)
    X_train_selected = selector.fit_transform(X_train, y_train)
    X_test_selected = selector.transform(X_test)
    
    # Get selected feature names
    selected_mask = selector.get_support()
    selected_features = [feature_names[i] for i in range(len(feature_names)) if selected_mask[i]]
    feature_scores = selector.scores_
    
    print(f"  Selected features: {len(selected_features)}")
    print(f"  Feature importance scores:")
    for i, (name, score) in enumerate(zip(feature_names, feature_scores)):
        if selected_mask[i]:
            print(f"    {name}: {score:.4f}")
    
    return X_train_selected, X_test_selected, selected_features, selector

def hyperparameter_tuning(X_train, y_train, model_type='logistic'):
    """
    Perform hyperparameter tuning using GridSearchCV.
    """
    print(f"\nHyperparameter tuning for {model_type}...")
    
    if model_type == 'logistic':
        param_grid = {
            'C': [0.1, 0.5, 1.0, 2.0, 5.0],
            'solver': ['lbfgs', 'liblinear'],
            'max_iter': [1000, 2000]
        }
        base_model = LogisticRegression(random_state=42)
    elif model_type == 'random_forest':
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10]
        }
        base_model = RandomForestClassifier(random_state=42, n_jobs=-1)
    elif model_type == 'gradient_boosting':
        param_grid = {
            'n_estimators': [100, 200],
            'learning_rate': [0.05, 0.1, 0.15],
            'max_depth': [3, 5, 7]
        }
        base_model = GradientBoostingClassifier(random_state=42)
    else:
        return None
    
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    grid_search = GridSearchCV(
        base_model, param_grid, cv=skf, scoring='accuracy',
        n_jobs=-1, verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"  Best parameters: {grid_search.best_params_}")
    print(f"  Best CV score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def train_ensemble_models(X_train, y_train, X_test, y_test, feature_names):
    """
    Train ensemble of models with optimized hyperparameters.
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Feature selection
    X_train_selected, X_test_selected, selected_features, selector = feature_selection(
        X_train_scaled, y_train, X_test_scaled, feature_names, k='all'
    )
    
    # Train optimized models
    print("\n" + "=" * 60)
    print("Training Optimized Models")
    print("=" * 60)
    
    models = {}
    
    # Optimized Logistic Regression
    print("\n1. Optimizing Logistic Regression...")
    lr_optimized = hyperparameter_tuning(X_train_selected, y_train, 'logistic')
    if lr_optimized:
        lr_optimized.fit(X_train_selected, y_train)
        y_pred = lr_optimized.predict(X_test_selected)
        y_pred_proba = lr_optimized.predict_proba(X_test_selected)[:, 1]
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        models['Logistic Regression'] = {
            'model': lr_optimized,
            'accuracy': accuracy,
            'auc': auc,
            'scaler': scaler,
            'selector': selector
        }
        print(f"  Test Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
    
    # Optimized Random Forest
    print("\n2. Optimizing Random Forest...")
    rf_optimized = hyperparameter_tuning(X_train, y_train, 'random_forest')
    if rf_optimized:
        rf_optimized.fit(X_train, y_train)
        y_pred = rf_optimized.predict(X_test)
        y_pred_proba = rf_optimized.predict_proba(X_test)[:, 1]
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        models['Random Forest'] = {
            'model': rf_optimized,
            'accuracy': accuracy,
            'auc': auc,
            'scaler': None,
            'selector': None
        }
        print(f"  Test Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
    
    # Optimized Gradient Boosting
    print("\n3. Optimizing Gradient Boosting...")
    gb_optimized = hyperparameter_tuning(X_train, y_train, 'gradient_boosting')
    if gb_optimized:
        gb_optimized.fit(X_train, y_train)
        y_pred = gb_optimized.predict(X_test)
        y_pred_proba = gb_optimized.predict_proba(X_test)[:, 1]
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        models['Gradient Boosting'] = {
            'model': gb_optimized,
            'accuracy': accuracy,
            'auc': auc,
            'scaler': None,
            'selector': None
        }
        print(f"  Test Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
    
    # Create Ensemble (Voting Classifier) - use only models that work on same data
    print("\n4. Creating Ensemble Model...")
    # For ensemble, use only models that work on raw features (not LR with scaling)
    ensemble_models = []
    for name, model_data in models.items():
        if name != 'Logistic Regression':  # Skip LR for ensemble (needs scaling)
            ensemble_models.append((name.lower().replace(' ', '_'), model_data['model']))
    
    if len(ensemble_models) >= 2:
        voting_clf = VotingClassifier(
            estimators=ensemble_models,
            voting='soft'  # Use probabilities
        )
        voting_clf.fit(X_train, y_train)
        y_pred = voting_clf.predict(X_test)
        y_pred_proba = voting_clf.predict_proba(X_test)[:, 1]
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        models['Ensemble (Voting)'] = {
            'model': voting_clf,
            'accuracy': accuracy,
            'auc': auc,
            'scaler': None,
            'selector': None
        }
        print(f"  Test Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
    else:
        print("  Not enough models for ensemble (need at least 2)")
    
    # Find best model
    best_name = max(models.keys(), key=lambda k: models[k]['accuracy'])
    best_model = models[best_name]
    
    return best_model, best_name, models, selected_features

def main():
    """Main advanced training function."""
    print("=" * 60)
    print("NBA Z-LOCK - Advanced Model Training")
    print("=" * 60)
    print("Features:")
    print("  - Feature Selection")
    print("  - Hyperparameter Tuning (GridSearchCV)")
    print("  - Ensemble Methods")
    print("=" * 60)
    
    # Load data
    try:
        df = load_training_data('data/training_data.csv')
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        return
    
    print(f"\nLoaded {len(df)} training examples")
    print(f"Features: {len(df.columns) - 1}")
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} examples")
    print(f"Test set: {len(X_test)} examples")
    
    # Train advanced models
    best_model_data, best_name, all_models, selected_features = train_ensemble_models(
        X_train, y_train, X_test, y_test, feature_names
    )
    
    print(f"\n{'=' * 60}")
    print("Model Comparison:")
    print("=" * 60)
    for name, model_data in all_models.items():
        marker = " <-- BEST" if name == best_name else ""
        print(f"{name}:")
        print(f"  Accuracy: {model_data['accuracy']:.4f}")
        print(f"  AUC: {model_data['auc']:.4f}{marker}")
    
    print(f"\n{'=' * 60}")
    print(f"Best Model: {best_name}")
    print(f"Test Accuracy: {best_model_data['accuracy']:.4f}")
    print(f"Test AUC: {best_model_data['auc']:.4f}")
    print(f"{'=' * 60}")
    
    # Cross-validation on best model
    print(f"\nPerforming cross-validation on {best_name}...")
    if best_name == 'Logistic Regression':
        scaler = best_model_data['scaler']
        selector = best_model_data['selector']
        X_train_scaled = scaler.transform(X_train)
        X_train_selected = selector.transform(X_train_scaled)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            best_model_data['model'], X_train_selected, y_train, 
            cv=skf, scoring='accuracy'
        )
    else:
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            best_model_data['model'], X_train, y_train, 
            cv=skf, scoring='accuracy'
        )
    
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    print(f"CV Accuracy: {cv_mean:.4f} (+/- {cv_std * 2:.4f})")
    
    # Save model
    models_dir = Path(config.MODELS_DIR)
    model_path = models_dir / 'best_model.pkl'
    scaler_path = models_dir / 'scaler.pkl'
    selector_path = models_dir / 'feature_selector.pkl'
    feature_names_path = models_dir / 'feature_names.json'
    
    with open(model_path, 'wb') as f:
        pickle.dump(best_model_data['model'], f)
    
    if best_model_data['scaler']:
        with open(scaler_path, 'wb') as f:
            pickle.dump(best_model_data['scaler'], f)
    
    if best_model_data['selector']:
        with open(selector_path, 'wb') as f:
            pickle.dump(best_model_data['selector'], f)
    
    with open(feature_names_path, 'w') as f:
        json.dump(selected_features if best_name == 'Logistic Regression' else feature_names, f)
    
    print(f"\nSaved model to {model_path}")
    if best_model_data['scaler']:
        print(f"Saved scaler to {scaler_path}")
    if best_model_data['selector']:
        print(f"Saved feature selector to {selector_path}")
    print(f"Saved feature names to {feature_names_path}")
    
    # Save results
    results_summary = {
        'best_model': best_name,
        'test_accuracy': float(best_model_data['accuracy']),
        'test_auc': float(best_model_data['auc']),
        'cv_accuracy_mean': float(cv_mean),
        'cv_accuracy_std': float(cv_std),
        'feature_names': selected_features if best_name == 'Logistic Regression' else feature_names,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'advanced_training': True,
        'all_models': {name: {
            'accuracy': float(data['accuracy']),
            'auc': float(data['auc'])
        } for name, data in all_models.items()}
    }
    
    results_path = models_dir / 'training_results.json'
    with open(results_path, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"Saved training results to {results_path}")
    print("\nAdvanced training complete!")

if __name__ == '__main__':
    main()

