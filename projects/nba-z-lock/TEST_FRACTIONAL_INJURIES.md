# Testing Guide: Fractional/Probability Injury System

## Test Scenarios

### Test 1: Basic Player Selection
1. Open the web app at http://127.0.0.1:5000
2. Select a home team (e.g., Lakers)
3. Select a visitor team (e.g., Warriors)
4. Select 1-2 players from the home team dropdown
5. **Expected**: Status management UI should appear showing selected players

### Test 2: Status Selection (Out)
1. Select a player from home team
2. In the status management section, set player status to "Out (0%)"
3. **Expected**: 
   - Probability slider should hide
   - Player should be marked as 0% available
   - Console should show probability = 0.0

### Test 3: Status Selection (Available)
1. Select a player from visitor team
2. Set player status to "Available (100%)"
3. **Expected**:
   - Probability slider should hide
   - Player should be marked as 100% available
   - Console should show probability = 1.0

### Test 4: Status Selection (Questionable) - MAIN TEST
1. Select a star player (⭐) from home team
2. Set player status to "Questionable"
3. **Expected**:
   - Probability slider should appear
   - Default should be 50%
   - Slider should show "50%" next to it

### Test 5: Probability Adjustment
1. With a player set to "Questionable"
2. Adjust the probability slider (try 25%, 50%, 75%)
3. **Expected**:
   - Percentage value should update in real-time
   - Console logs should show updated probability values
   - Values should be between 0.01 and 0.99

### Test 6: Multiple Players with Different Statuses
1. Select 3 players from home team:
   - Player 1: Set to "Out" (0%)
   - Player 2: Set to "Questionable" at 60%
   - Player 3: Set to "Available" (100%)
2. **Expected**:
   - All three players should appear in status management
   - Each should show correct status and probability
   - Console should show all three probabilities

### Test 7: Prediction with Fractional Values
1. Select teams
2. Select a star player, set to "Questionable" at 40%
3. Click "Get Prediction"
4. **Expected**:
   - Backend should receive probability values (0.4 for that player)
   - Backend logs should show fractional availability (e.g., star_player_available: 0.4)
   - Prediction should complete successfully
   - Prediction should reflect reduced win probability due to questionable star player

### Test 8: Clear Functionality
1. Select multiple players and set various statuses
2. Click "Clear All Injuries"
3. **Expected**:
   - All selections should clear
   - Status management UI should disappear
   - playerStatuses object should be empty

### Test 9: Clear Individual Team
1. Select players from both home and visitor teams
2. Click "Clear" for home team
3. **Expected**:
   - Only home team players should be cleared
   - Visitor team players should remain
   - Status management should update accordingly

## Console Checks

Open browser developer tools (F12) and check:

1. **When players are selected**: Should see logs like:
   ```
   home team: 2 injured player(s) - Player1, Player2
   ```

2. **When status changes**: Check for probability values in console

3. **When making prediction**: Check Network tab → /api/predict request
   - Request body should have `injury_data` with probabilities
   - Should see structure like:
   ```json
   {
     "injured_players": {
       "home": {
         "Player Name": 0.4
       }
     }
   }
   ```

4. **Backend logs**: Check terminal for:
   - `[INJURY] Processing X players with probabilities...`
   - `[INJURY] Home team availability: {key_players_available: X, star_player_available: Y}`
   - Fractional values (e.g., 0.4, 0.75, etc.)

## Error Checks

Watch for:
- JavaScript errors in browser console
- 500 errors in Network tab
- Backend traceback errors in terminal
- UI not updating when status changes
- Probability slider not appearing for "Questionable"
- Values not being sent to backend correctly

## Success Criteria

✅ Status management UI appears when players selected
✅ Three status options work correctly
✅ Probability slider appears/disappears correctly
✅ Probability values update in real-time
✅ Fractional values sent to backend
✅ Backend processes fractional values correctly
✅ Predictions complete without errors
✅ Clear functionality works for all/individual teams



