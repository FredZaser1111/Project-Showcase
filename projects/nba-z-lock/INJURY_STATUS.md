# Injury Status in NBA Z-LOCK

## Current Status: ❌ **NOT IMPLEMENTED**

The tool **does not currently account for injuries**. This is a significant limitation that could improve accuracy by **+2-3%**.

## Why Injuries Matter

Injuries to key players can dramatically affect game outcomes:
- **Star player out**: Can reduce team win probability by 10-20%
- **Multiple starters out**: Even bigger impact
- **Load management**: Rest days for star players

## What's Missing

Currently, the model uses:
- ✅ Team records
- ✅ Recent form
- ✅ Advanced metrics
- ✅ Rest days
- ❌ **Player availability** (injuries, rest)
- ❌ **Star player status**

## NBA_API Limitations

The free `nba_api` library **does not provide real-time injury data**. It provides:
- ✅ Team rosters
- ✅ Game statistics
- ✅ Player statistics
- ❌ **No injury reports**
- ❌ **No player status** (probable, questionable, out)

## Solutions

### Option 1: Manual Entry (Free)
- Add a simple UI to mark players as injured
- Store in a local file
- Use in predictions

**Pros**: Free, immediate  
**Cons**: Manual work, not real-time

### Option 2: Injury API (Paid)
- **SportsDataIO**: $50-100/month
- **TheScore API**: $100-200/month
- **ESPN API**: Limited availability

**Pros**: Real-time, automated  
**Cons**: Cost

### Option 3: Web Scraping (Free but Complex)
- Scrape injury reports from NBA.com or ESPN
- Parse HTML/JSON
- Update daily

**Pros**: Free  
**Cons**: Fragile, may break, legal concerns

### Option 4: Approximate with Historical Data (Free)
- Use historical games where key players didn't play
- Estimate impact based on past performance
- Infer from game logs (if player didn't play, they were likely injured/rested)

**Pros**: Free, uses existing data  
**Cons**: Not real-time, less accurate

## Recommended Approach

For **Phase 1**, I recommend **Option 4** (Approximate with Historical Data):

1. **Identify key players** from rosters (top 3 by minutes/points)
2. **Check game logs** to see if they played
3. **Create features**:
   - `home_key_players_available` (0-3)
   - `visitor_key_players_available` (0-3)
   - `home_star_player_played_last_game` (0/1)
   - `visitor_star_player_played_last_game` (0/1)

This gives us **some injury awareness** without external APIs.

## Impact on Accuracy

Adding injury features could improve accuracy by:
- **+1-2%**: Basic player availability (historical)
- **+2-3%**: Real-time injury data (API)
- **+3-5%**: Full injury + load management tracking

## Implementation Status

- ❌ **Not implemented** in current model
- ✅ **Planned** for Phase 1 improvements
- 📝 **Documented** in ROAD_TO_75_PERCENT.md

## Next Steps

Would you like me to:
1. **Implement basic player availability** using historical game logs?
2. **Add manual injury input** to the web interface?
3. **Research free injury data sources**?
4. **Leave as-is** for now?

