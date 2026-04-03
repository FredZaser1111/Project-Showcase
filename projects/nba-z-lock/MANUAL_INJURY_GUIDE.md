# Manual Injury Input Guide

## Overview

The NBA Z-LOCK tool now includes a **Manual Injury Input** feature that allows you to manually mark injured players before making predictions. This gives you full control over injury data and can significantly improve prediction accuracy when you have up-to-date injury information.

## How It Works

### 1. **Injury Input UI**
- Located in the prediction card, above the "Get Prediction" button
- Two sections: Home Team Injuries and Visitor Team Injuries
- Each section has:
  - **Key Players Available**: Number input (0-3) for how many key players are available
  - **Star Player Available**: Dropdown (Yes/No) for whether the star player is playing

### 2. **Default Values**
- **Key Players Available**: 3 (all available)
- **Star Player Available**: Yes (available)

### 3. **Using Manual Injuries**

**Example Scenario:**
- Lakers (Home) vs Warriors (Visitor)
- Lakers: LeBron James (star) is OUT, 2 key players available
- Warriors: All players healthy

**Steps:**
1. Select teams in the dropdowns
2. In the Injury Status section:
   - **Home Team (Lakers)**:
     - Key Players Available: `2`
     - Star Player Available: `No`
   - **Visitor Team (Warriors)**:
     - Key Players Available: `3` (default)
     - Star Player Available: `Yes` (default)
3. Click "Get Prediction"

### 4. **Clear Injuries Button**
- Resets all injury inputs to defaults (all players available)
- Useful when switching between different matchups

## How It Affects Predictions

The manual injury data directly impacts these features:
- `home_key_players_available` (0-3)
- `home_star_player_available` (0 or 1)
- `visitor_key_players_available` (0-3)
- `visitor_star_player_available` (0 or 1)
- `key_players_available_diff` (calculated automatically)

These features are used by the trained ML model to adjust win probabilities based on player availability.

## Priority System

The tool uses a priority system for injury data:

1. **Manual Injury Data** (Highest Priority)
   - If you manually set injuries in the UI, these values are used
   - Overrides automatic approximation

2. **Automatic Approximation** (Fallback)
   - If no manual data is provided, the tool uses performance-based approximation
   - Checks recent team scoring to infer player availability

3. **Default Values** (Last Resort)
   - If neither method works, assumes all players are available

## Tips for Best Results

1. **Check Official Sources**: Use NBA.com, ESPN, or team Twitter accounts for injury reports
2. **Update Before Each Prediction**: Injury status changes daily
3. **Be Specific**: 
   - If a star player is out, set "Star Player Available" to "No"
   - If multiple key players are out, reduce "Key Players Available" accordingly
4. **Clear When Switching Teams**: Use "Clear Injuries" when analyzing different matchups

## Technical Details

- Injury data is sent as JSON in the prediction request
- Only sent if different from defaults (optimizes API calls)
- Integrated into feature engineering pipeline
- Works with all trained models (enhanced, advanced, etc.)

## Example JSON Structure

```json
{
  "home": {
    "key_players_available": 2,
    "star_player_available": 0
  },
  "visitor": {
    "key_players_available": 3,
    "star_player_available": 1
  }
}
```

---

**Note**: This feature is optional. If you don't set any injuries, the tool will use automatic approximation or defaults.

