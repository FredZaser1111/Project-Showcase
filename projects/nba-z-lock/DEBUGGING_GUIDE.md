# NBA Z-LOCK Debugging Guide

## Current Issue: Feature Mismatch

**Problem:** Predictions are failing with error:
```
X has 62 features, but SelectKBest is expecting 19 features as input.
```

**Root Cause:**
- Model was trained with feature selection (SelectKBest) that selected 19 features
- Selector expects 19 input features
- We're now extracting 62 features
- Feature mismatch causes prediction to fail

**Current Status:**
- Selector expects: 19 features
- Feature names file has: 62 features
- Model type: VotingClassifier (RandomForest + GradientBoosting)

## Solutions

### Option 1: Retrain Model with All 62 Features (RECOMMENDED)
This ensures the model works with all current features.

```bash
cd "C:\cursor projects portfolio\nba-prediction-tool"
.\venv\Scripts\python.exe models/train_advanced.py
```

**Note:** Make sure `feature_names.json` is updated to include all 62 features before training.

### Option 2: Fix Feature Selection Pipeline
Ensure the selector is trained on all 62 features, then selects 19.

### Option 3: Skip Feature Selection (TEMPORARY FIX)
The code now skips feature selection if there's a mismatch, but the model may not work correctly since it was trained on 19 features.

## Debugging Tools

### 1. Test Prediction Endpoint
```bash
.\venv\Scripts\python.exe test_prediction_debug.py
```

### 2. Check Model Structure
```bash
.\venv\Scripts\python.exe check_model.py
```

### 3. Check Selector
```bash
.\venv\Scripts\python.exe check_selector.py
```

### 4. Frontend Console Logging
Open browser DevTools (F12) and check console for:
- `[PREDICT]` - Prediction request logs
- `[DISPLAY]` - Display function logs
- Error messages

### 5. Flask Server Logs
Check the Flask terminal for:
- `PREDICTION REQUEST RECEIVED`
- `[FE]` - Feature engineering logs
- `[ROSTER]` - Roster loading logs
- Error tracebacks

## Current Fixes Applied

1. ✅ Feature count validation before selector
2. ✅ Skip selector if mismatch detected
3. ✅ Enhanced error handling
4. ✅ Frontend timeout (60s)
5. ✅ Comprehensive logging
6. ✅ Test scripts for debugging

## Next Steps

1. **Retrain the model** with all 62 features to fix the mismatch
2. **Test predictions** after retraining
3. **Monitor logs** to ensure everything works

## Quick Test

After retraining, test with:
```bash
.\venv\Scripts\python.exe test_prediction_debug.py
```

Expected: Status 200, successful prediction with probabilities.


