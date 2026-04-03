# Game Data Collection Implementation

## Overview
Game data collection for NBA_API has been fully implemented. The system can now collect historical game data using the free `nba_api` library.

## Implementation Details

### Methods Implemented

#### 1. `get_team_games(team_id, season)`
- Fetches all games for a specific team in a season
- Uses `TeamGameLog` endpoint from NBA_API
- Returns games in format compatible with feature engineering
- **Note**: Team game logs only include the team's own score. Opponent scores are matched up in `get_all_games()`

#### 2. `get_games_by_date(game_date)`
- Fetches all games for a specific date
- Uses `ScoreboardV2` endpoint from NBA_API
- Returns complete game data with both home and visitor scores
- **Best method for getting complete game data**

#### 3. `get_all_games(seasons)`
- Collects all games for specified seasons
- Iterates through all teams and matches up scores from both teams' game logs
- Removes duplicates and returns only complete games (with both scores)
- **Recommended for bulk historical data collection**

## Data Format

Games are returned in the following format (compatible with feature engineering):

```python
{
    'id': '0022301188',  # Game ID
    'date': '2024-04-14',  # ISO date format
    'home_team': {'id': 1610612754},  # Home team dict
    'visitor_team': {'id': 1610612737},  # Visitor team dict
    'home_team_id': 1610612754,  # Direct team ID
    'visitor_team_id': 1610612737,  # Direct team ID
    'home_team_score': 132,  # Home team points
    'visitor_team_score': 122  # Visitor team points
}
```

## Usage

### Collect Historical Data

Run the data collection script:

```bash
python scripts/collect_historical_data.py
```

This will:
1. Detect which API provider is configured (`nba_api` or `balldontlie`)
2. Collect games for the last 3 seasons
3. Save to `data/historical_games.json`

### Test Game Collection

Test the implementation:

```bash
python test_nba_api_games.py
```

## Rate Limiting

NBA_API is free but has rate limits. The client includes:
- Automatic rate limiting (60 requests/minute default)
- Caching to reduce API calls
- Retry logic with exponential backoff

## Score Matching

When collecting team games, scores are matched up by:
1. Collecting game logs for all teams
2. Matching games by `game_id`
3. Combining scores from both teams' perspectives
4. Filtering to only include games with complete scores

## Next Steps

1. **Collect Historical Data**: Run `python scripts/collect_historical_data.py`
2. **Train Model**: Run `python models/train_model.py`
3. **Test Predictions**: Use the web interface to make predictions

## Notes

- Date-based queries (`get_games_by_date`) return complete scores immediately
- Team-based queries need to be matched up in `get_all_games()` for complete data
- All methods cache results to reduce API calls
- The data format is compatible with existing feature engineering code

