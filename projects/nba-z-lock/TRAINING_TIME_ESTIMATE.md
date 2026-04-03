# Model Training Time Estimates

## Training Process Overview

The training script trains **3 models** and selects the best one:
1. **Logistic Regression** - Fast (~seconds)
2. **Random Forest** (100 trees) - Moderate (~minutes)
3. **Gradient Boosting** (100 estimators) - Moderate (~minutes)

Plus:
- **5-fold Cross-Validation** on the best model
- **Feature Engineering** (if needed)

## Time Estimates by Data Size

### Small Dataset (1 season, ~1,200 games)
- **Feature Engineering**: 1-3 minutes
- **Model Training**: 2-5 minutes
  - Logistic Regression: ~10 seconds
  - Random Forest: ~1-2 minutes
  - Gradient Boosting: ~1-2 minutes
- **Cross-Validation**: 1-2 minutes
- **Total**: **5-10 minutes**

### Medium Dataset (2-3 seasons, ~2,500-3,500 games)
- **Feature Engineering**: 3-5 minutes
- **Model Training**: 5-10 minutes
  - Logistic Regression: ~15 seconds
  - Random Forest: ~3-5 minutes
  - Gradient Boosting: ~2-4 minutes
- **Cross-Validation**: 2-4 minutes
- **Total**: **10-20 minutes**

### Large Dataset (5+ seasons, ~5,000+ games)
- **Feature Engineering**: 5-10 minutes
- **Model Training**: 10-20 minutes
  - Logistic Regression: ~30 seconds
  - Random Forest: ~5-10 minutes
  - Gradient Boosting: ~5-10 minutes
- **Cross-Validation**: 5-10 minutes
- **Total**: **20-40 minutes**

## Factors Affecting Training Time

### ⚡ Speed Factors
- **CPU Cores**: Random Forest uses `n_jobs=-1` (all cores)
- **RAM**: More RAM = faster processing
- **SSD vs HDD**: SSD is faster for data loading
- **Data Already Processed**: If `training_data.csv` exists, skips feature engineering

### 🐌 Slowdown Factors
- **Large Historical Dataset**: More games = longer feature engineering
- **Complex Features**: More features = longer training
- **Older Hardware**: Slower CPU/RAM
- **First Run**: Feature engineering takes longer on first run

## Typical Scenario

For **NBA Z-LOCK** with **2-3 seasons** of data:
- **Most Common**: **10-15 minutes**
- **Fast Computer**: **5-10 minutes**
- **Slower Computer**: **15-25 minutes**

## What Happens During Training

1. **Data Loading** (30 seconds - 2 minutes)
   - Loads historical games
   - Creates feature engineer

2. **Feature Engineering** (1-10 minutes)
   - Calculates team records
   - Recent form analysis
   - Head-to-head stats
   - Rest days calculation
   - Home court advantage

3. **Model Training** (2-20 minutes)
   - Trains 3 models
   - Evaluates each
   - Selects best

4. **Cross-Validation** (1-10 minutes)
   - 5-fold CV on best model
   - More reliable accuracy estimate

5. **Saving Models** (5-10 seconds)
   - Saves best model
   - Saves scaler (if needed)
   - Saves feature names
   - Saves results

## Tips to Speed Up Training

1. **Use Pre-processed Data**: If `training_data.csv` exists, training is faster
2. **Collect Less Data**: Start with 1-2 seasons instead of 5+
3. **Run During Off-Peak**: Other programs slow down training
4. **Close Unnecessary Apps**: Free up RAM/CPU

## Progress Indicators

The training script shows:
- Number of training examples
- Feature names
- Training progress for each model
- Accuracy and AUC scores
- Cross-validation results

You'll see real-time progress, so you know it's working!

## After Training

Once training completes:
- Model saved to `models/best_model.pkl`
- Results saved to `models/training_results.json`
- Ready to make predictions immediately!

---

**Bottom Line**: Expect **10-15 minutes** for typical training, but it can range from **5-40 minutes** depending on your data size and computer speed.

