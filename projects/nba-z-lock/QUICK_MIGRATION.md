# Quick Migration: Ball Don't Lie → NBA_API

## Summary

**Difficulty**: Easy (2-3 hours)  
**Cost Savings**: $0/month (NBA_API is free!)  
**Odds**: Already handled - your `probability_to_moneyline()` function works perfectly

## Step-by-Step Migration

### 1. Install NBA_API

```powershell
.\venv\Scripts\python.exe -m pip install nba_api
```

### 2. Swap API Client

**Option A: Replace file**
```powershell
# Backup old client
Move-Item api_client.py api_client_balldontlie.py

# Use new client
Move-Item api_client_nba.py api_client.py
```

**Option B: Update imports**
In `app.py`, change:
```python
from api_client import APIClient
```
to:
```python
from api_client_nba import NBAAPIClient as APIClient
```

### 3. Update Config (Remove API Key)

Edit `config.py`:
```python
# Remove API key requirement
API_KEY = ''  # Not needed for NBA_API
API_BASE_URL = ''  # Not used with NBA_API
```

Or update `.env`:
```
# NBA_API doesn't need an API key!
BALLDONTLIE_API_KEY=
API_TIER=free
```

### 4. Update Data Collection Script

Edit `scripts/collect_historical_data.py`:
- Change `from api_client import APIClient` to use NBA_API client
- Update data collection logic to use NBA_API methods

### 5. Adjust Feature Engineering (If Needed)

Check `feature_engineering.py` - may need minor field name adjustments:
- NBA_API might use different field names
- Test with sample data first

### 6. Test

```powershell
# Test API connection
python -c "from api_client_nba import NBAAPIClient; client = NBAAPIClient(); print(client.get_all_teams())"

# Test Flask app
python app.py
```

## What Stays the Same ✅

- **UI** - Zero changes needed
- **Odds Calculation** - Already works, no changes
- **ML Models** - No changes
- **Flask Routes** - No changes (uses abstraction)

## Odds - You're Already Set! ✅

Your `probability_to_moneyline()` function in `models/predictor.py` already:
- Converts win probability to money line odds
- Works with any API
- No changes needed!

If you want real sportsbook odds later, you can add a separate API just for odds display.

## Benefits of NBA_API

- ✅ **Free** - No API costs
- ✅ **Official** - Direct from NBA.com
- ✅ **Comprehensive** - Full statistics database
- ✅ **Reliable** - Official source

## Potential Issues

1. **Rate Limits**: NBA_API may have different rate limits
2. **Data Structure**: Field names might differ (easy to map)
3. **Historical Data**: Collection method may differ

All solvable in 2-3 hours!

## Need Help?

The new `api_client_nba.py` is ready to use. Just swap it in and adjust field mappings if needed.

