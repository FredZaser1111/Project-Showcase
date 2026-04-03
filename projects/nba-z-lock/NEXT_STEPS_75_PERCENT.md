# Next Steps: Road to 75% Accuracy

## Current Status
- **Current Accuracy**: 61.5%
- **Target**: 75%
- **Gap**: +13.5 percentage points

## Priority Implementation Order (Most Efficient Path)

### Phase 2: Improved Player Classification ✅ (Just Completed)
**Status**: DONE - Using statistical analysis instead of simple roster order
**Impact**: Better injury input accuracy (indirect model improvement)

---

### Phase 3: Enhanced Player-Level Features (HIGHEST IMPACT)
**Estimated Impact**: +3-5% accuracy  
**Time**: 2-3 hours  
**Priority**: ⭐⭐⭐⭐⭐

#### What to Add:
1. **Star Player Statistics** (when available):
   - `home_star_ppg` - Star player's points per game
   - `visitor_star_ppg`
   - `home_star_usage_rate` - Usage percentage
   - `visitor_star_usage_rate`

2. **Top 3 Players Aggregate**:
   - `home_top3_ppg_avg` - Average PPG of top 3 players
   - `visitor_top3_ppg_avg`
   - `home_top3_mpg_avg` - Average minutes per game
   - `visitor_top3_mpg_avg`

3. **Player Efficiency**:
   - `home_top3_per_avg` - Player Efficiency Rating
   - `visitor_top3_per_avg`

**Files to Modify**:
- `feature_engineering.py` - Add new feature extraction methods
- `player_classifier.py` - Already created, use it to get player stats
- `models/train_advanced.py` - Retrain with new features

**Quick Start**:
```python
# In feature_engineering.py, add:
def get_star_player_stats(self, team_id, game_date):
    classifier = PlayerClassifier()
    classifications = classifier.classify_players(team_id)
    if classifications['star']:
        star = classifications['star'][0]
        return {
            'ppg': star['ppg'],
            'usage': star['usage'],
            'mpg': star['mpg']
        }
    return {'ppg': 0, 'usage': 0, 'mpg': 0}
```

---

### Phase 4: Advanced Team Metrics (Already Partially Done)
**Estimated Impact**: +1-2% accuracy  
**Time**: 1 hour  
**Priority**: ⭐⭐⭐⭐

#### What's Missing:
- **Turnover Rate** - TOV% (turnovers per 100 possessions)
- **Rebound Rate** - Offensive/Defensive rebound percentages
- **Free Throw Rate** - FTA per FGA
- **Assist Rate** - Percentage of baskets assisted

**Files to Modify**:
- `feature_engineering.py` - Enhance `calculate_advanced_metrics()`

---

### Phase 5: Situational Features Enhancement
**Estimated Impact**: +1-2% accuracy  
**Time**: 1-2 hours  
**Priority**: ⭐⭐⭐

#### What to Add:
1. **Travel Distance** (miles between team cities)
2. **Time Zone Changes** (e.g., West Coast team playing East Coast)
3. **Playoff Race Pressure**:
   - Games remaining in season
   - Playoff position (if in playoff race)
   - Games behind/ahead in standings

**Files to Create**:
- `utils/travel_distance.py` - Calculate distances between cities
- `utils/playoff_race.py` - Calculate playoff pressure metrics

---

### Phase 6: More Training Data
**Estimated Impact**: +1-2% accuracy  
**Time**: 2-3 hours (mostly waiting for data collection)  
**Priority**: ⭐⭐⭐⭐

#### Actions:
1. **Collect 15+ seasons** (currently 10):
   ```bash
   python scripts/collect_historical_data.py
   ```
   - Modify to collect 2009-10 through 2024-25
   - This gives ~12,000+ games instead of ~5,000

2. **Include Playoff Games** (optional):
   - Separate feature flag: `is_playoff_game`
   - Or train separate playoff model

3. **Data Quality Improvements**:
   - Remove games with missing key data
   - Weight recent seasons more heavily

---

### Phase 7: Model Architecture Improvements
**Estimated Impact**: +2-3% accuracy  
**Time**: 3-4 hours  
**Priority**: ⭐⭐⭐

#### Options:
1. **Ensemble Stacking**:
   - Train multiple models (XGBoost, LightGBM, CatBoost)
   - Stack them with a meta-learner

2. **Neural Network** (if you want to try):
   - Simple feedforward network
   - Can handle non-linear interactions better

3. **Hyperparameter Optimization**:
   - Use Optuna or Hyperopt for automated tuning
   - More thorough than GridSearchCV

**Files to Create**:
- `models/train_ensemble_stacked.py` - Stacked ensemble
- `models/train_neural_network.py` - Optional neural network

---

## Recommended Implementation Order

### Week 1: Quick Wins
1. ✅ **Phase 2**: Improved Player Classification (DONE)
2. **Phase 3**: Enhanced Player-Level Features (+3-5%)
3. **Phase 4**: Complete Advanced Metrics (+1-2%)

**Expected Result**: 65-68% accuracy

### Week 2: Data & Features
4. **Phase 5**: Situational Features (+1-2%)
5. **Phase 6**: More Training Data (+1-2%)

**Expected Result**: 67-70% accuracy

### Week 3: Model Improvements
6. **Phase 7**: Model Architecture (+2-3%)

**Expected Result**: 69-73% accuracy

---

## Efficiency Tips

### 1. **Incremental Testing**
After each phase:
```bash
# Retrain model
python models/train_advanced.py

# Check accuracy improvement
# Compare to baseline (61.5%)
```

### 2. **Feature Importance Analysis**
After adding features:
```python
# In train_advanced.py, add:
feature_importance = best_model.feature_importances_
# Print top 10 features
# Remove features that don't help
```

### 3. **Cross-Validation**
Always use 5-fold cross-validation to avoid overfitting:
```python
from sklearn.model_selection import cross_val_score
cv_scores = cross_val_score(model, X, y, cv=5)
print(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
```

### 4. **Data Caching**
Cache expensive API calls:
- Player stats
- Team metrics
- Travel distances

---

## Realistic Expectations

**Important**: 75% accuracy is extremely difficult. Here's what's realistic:

- **65-68%**: Very good (better than most sportsbooks)
- **68-70%**: Excellent (top-tier performance)
- **70-72%**: World-class (rarely achieved)
- **72-75%**: Exceptional (requires luck + perfect features)

**Focus on**: Getting to 68-70% first, which is already excellent performance.

---

## Quick Start: Phase 3 (Next Step)

1. **Open** `feature_engineering.py`
2. **Add** player stats methods (see code snippet above)
3. **Update** `extract_features_for_prediction()` to include player stats
4. **Retrain** model:
   ```bash
   python models/train_advanced.py
   ```
5. **Test** accuracy improvement

**Estimated Time**: 2-3 hours  
**Expected Gain**: +3-5% accuracy

---

## Monitoring Progress

Create a tracking file:
```python
# accuracy_tracking.json
{
    "baseline": 61.5,
    "phase_2": 61.5,  # Player classification (UI improvement)
    "phase_3": null,  # Player features
    "phase_4": null,  # Advanced metrics
    "phase_5": null,  # Situational features
    "phase_6": null,  # More data
    "phase_7": null   # Model improvements
}
```

Update after each phase to track progress!

