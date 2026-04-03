# Incremental Training Guide

## Overview

Incremental training allows you to **update the model with new games** without retraining on all historical data. This is faster and keeps your model current with the latest season performance.

## How It Works

1. **Tracks last training date** - Stores when the model was last trained
2. **Identifies new games** - Finds games in `historical_games.json` that are newer than the last training date
3. **Combines datasets** - Merges existing training data with new games
4. **Retrains model** - Trains on the combined dataset
5. **Updates tracking** - Records the new training date

## Usage

### Basic Incremental Training

```bash
python models/train_incremental.py
```

This will:
- Find games since the last training
- Add them to existing training data
- Retrain the model
- Update the model files

### When to Use Incremental Training

✅ **Use incremental training when:**
- New games have been added to `historical_games.json`
- You want to update the model with recent season data
- You want faster training (only processes new games)
- You want to keep the model current

❌ **Use full training (`train_model.py`) when:**
- First time training (no previous model)
- You want to retrain on ALL data from scratch
- You've made significant changes to features
- You want to ensure consistency across all data

## Process Flow

```
1. Check last training date from training_results.json
   ↓
2. Load historical_games.json
   ↓
3. Filter games with date > last training date
   ↓
4. Load existing training_data.csv (if exists)
   ↓
5. Extract features from new games
   ↓
6. Combine old + new training data
   ↓
7. Retrain model on combined dataset
   ↓
8. Save updated model and training date
```

## Example Output

```
============================================================
NBA Game Prediction - Incremental Training
============================================================

Last training date: 2024-01-15 10:30:00

Identifying new games...
Found 127 new games since last training

Combining datasets:
  Existing samples: 4478
  New samples: 127
  Combined (after dedup): 4605

Saved updated training data to data/training_data.csv

Preparing features...
Feature names: ['home_win_pct', 'home_wins', ...] (84 total)

Training set: 3684 examples
Test set: 921 examples

Training models...
[Training progress...]

============================================================
Best Model: Random Forest
Test Accuracy: 0.6587
Test AUC: 0.6952
============================================================

Saved model to models/best_model.pkl
Saved training results to models/training_results.json

Training date updated to: 2024-12-27 14:45:00
New games added: 127

Incremental training complete! ✅
```

## Workflow Recommendations

### Weekly Updates (During Season)
```bash
# 1. Collect new games from the past week
python scripts/collect_historical_data.py

# 2. Update model with new games
python models/train_incremental.py
```

### Monthly Updates
- Collect all recent games
- Run incremental training
- Check if accuracy improved

### End of Season
- Do a full retrain with all data: `python models/train_model.py`
- Ensures consistency and best possible model

## Benefits

1. **Faster Training** - Only processes new games, not entire dataset
2. **Stays Current** - Model learns from latest games and trends
3. **Efficient** - Reuses existing training data
4. **Convenient** - Can run regularly to keep model updated

## Limitations

1. **Not True Incremental Learning** - Still retrains on combined dataset (most ML models don't support true incremental learning)
2. **Requires Historical Data** - Needs `historical_games.json` and `training_data.csv`
3. **Date Parsing** - Relies on game dates being parseable

## Troubleshooting

### "No new games found"
- Check if `historical_games.json` has games after the last training date
- Verify game dates are parseable
- Consider running full training if needed

### "No previous training found"
- Will train on all available data (same as full training)
- This is fine for first-time setup

### Date Parsing Errors
- Check game date formats in `historical_games.json`
- The script tries multiple date formats automatically
- Games with unparseable dates are skipped (with warning)

## Comparison: Incremental vs Full Training

| Feature | Incremental Training | Full Training |
|---------|---------------------|---------------|
| **Speed** | Faster (only new games) | Slower (all games) |
| **Data** | Old + New combined | All from scratch |
| **Use Case** | Regular updates | Initial training |
| **Accuracy** | Similar | Similar |
| **Complexity** | Simpler workflow | Straightforward |

## Best Practices

1. **Run weekly during season** to keep model current
2. **Full retrain quarterly** to ensure consistency
3. **Monitor accuracy** after incremental training
4. **Keep backups** of previous models if needed
5. **Check new games count** before training (to ensure it found new data)

---

**Quick Command Reference:**
- Incremental: `python models/train_incremental.py`
- Full: `python models/train_model.py`
- Collect Data: `python scripts/collect_historical_data.py`

