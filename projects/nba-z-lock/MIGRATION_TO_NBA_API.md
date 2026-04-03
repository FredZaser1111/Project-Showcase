# Migration Guide: Ball Don't Lie API → NBA_API

## Overview

This guide shows how to swap from Ball Don't Lie API to NBA_API (python-nba-api library) while keeping the UI intact.

## About NBA_API

- **Library**: `nba_api` (Python package)
- **Source**: NBA.com official statistics
- **Cost**: Free (no API key needed!)
- **Installation**: `pip install nba_api`

## Odds Solution

**Good News**: You already calculate odds from win probability! The `probability_to_moneyline()` function in `models/predictor.py` converts your ML model's win probability into implied money line odds.

**Options for Real Odds**:
1. **Keep current approach** (Recommended): Use calculated implied odds from your model
2. **Add separate odds API**: Use a free/cheap odds API just for display
3. **Scrape odds**: Get odds from free sources (legal considerations apply)

## Migration Steps

### Step 1: Install NBA_API

```powershell
.\venv\Scripts\python.exe -m pip install nba_api
```

### Step 2: Create New API Client

Create `api_client_nba.py` that uses NBA_API instead of Ball Don't Lie.

### Step 3: Update Config

Update `config.py` to support NBA_API (no API key needed).

### Step 4: Update Feature Engineering

Adjust `feature_engineering.py` to work with NBA_API data structure.

### Step 5: Test & Deploy

Test with new API, retrain model if needed.

## What Changes

### Files to Modify:
1. `api_client.py` → Replace with NBA_API calls
2. `config.py` → Remove API key requirement
3. `feature_engineering.py` → Adjust field mappings
4. `scripts/collect_historical_data.py` → Update data collection

### Files That Stay the Same:
- ✅ `templates/index.html` - UI unchanged
- ✅ `static/style.css` - Styling unchanged  
- ✅ `static/app.js` - Frontend logic unchanged
- ✅ `app.py` - Flask routes unchanged (uses API client abstraction)
- ✅ `models/train_model.py` - ML training unchanged
- ✅ `models/predictor.py` - Prediction logic unchanged (odds calculation stays!)

## Estimated Time: 2-4 hours

