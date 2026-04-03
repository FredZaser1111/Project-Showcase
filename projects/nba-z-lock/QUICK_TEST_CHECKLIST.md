# Quick Test Checklist - Fractional Injury System

## ✅ Step-by-Step Test

### 1. Open the App
- [ ] Navigate to http://127.0.0.1:5000
- [ ] Check browser console (F12) for any JavaScript errors

### 2. Select Teams
- [ ] Select a **Home Team** (e.g., Los Angeles Lakers)
- [ ] Select a **Visitor Team** (e.g., Golden State Warriors)
- [ ] Verify teams are different

### 3. Test Player Selection
- [ ] Select 1-2 players from **Home Team** dropdown (Ctrl+Click for multiple)
- [ ] **CHECK**: Does the "Set Player Status & Probability" section appear?
- [ ] **CHECK**: Do selected players show up with status dropdowns?

### 4. Test Status Options

#### Test A: Out Status
- [ ] Select a player's status dropdown
- [ ] Choose **"Out (0%)"**
- [ ] **CHECK**: Probability slider should disappear
- [ ] **CHECK**: Console should show probability = 0.0

#### Test B: Available Status  
- [ ] Select another player's status dropdown
- [ ] Choose **"Available (100%)"**
- [ ] **CHECK**: Probability slider should disappear
- [ ] **CHECK**: Console should show probability = 1.0

#### Test C: Questionable Status (MAIN TEST)
- [ ] Select a player's status dropdown
- [ ] Choose **"Questionable"**
- [ ] **CHECK**: Probability slider should appear
- [ ] **CHECK**: Default should be 50%
- [ ] **CHECK**: Should see "50%" next to slider

### 5. Test Probability Slider
- [ ] With a player set to "Questionable"
- [ ] Move slider to 25%
- [ ] **CHECK**: Percentage display updates to "25%"
- [ ] Move slider to 75%
- [ ] **CHECK**: Percentage display updates to "75%"
- [ ] Check browser console - should see updated probability values

### 6. Test Multiple Players
- [ ] Select 3 players total (mix of home/visitor)
- [ ] Set different statuses:
  - Player 1: Out
  - Player 2: Questionable at 40%
  - Player 3: Available
- [ ] **CHECK**: All three should show correct status/probability

### 7. Test Prediction with Probabilities
- [ ] Select teams
- [ ] Select a **star player** (⭐), set to "Questionable" at 30%
- [ ] Click **"Get Prediction"**
- [ ] **CHECK**: Prediction should complete successfully
- [ ] **CHECK**: Check browser Network tab → /api/predict request
  - Request body should show: `"Player Name": 0.3`
- [ ] **CHECK**: Check server terminal logs
  - Should see: `[INJURY] Processing X players with probabilities...`
  - Should see fractional values like: `star_player_available: 0.3`

### 8. Test Clear Functionality
- [ ] With players selected and statuses set
- [ ] Click **"Clear All Injuries"**
- [ ] **CHECK**: All selections cleared
- [ ] **CHECK**: Status management section disappears
- [ ] **CHECK**: Player dropdowns reset

## 🐛 Common Issues to Watch For

- [ ] Status management section doesn't appear when players selected
- [ ] Probability slider doesn't show for "Questionable"
- [ ] Slider value doesn't update in real-time
- [ ] JavaScript errors in console
- [ ] 500 error when making prediction
- [ ] Backend doesn't receive probability values
- [ ] Predictions fail with error messages

## ✅ Success Indicators

You'll know it's working if:
1. ✅ Status management UI appears when players are selected
2. ✅ "Questionable" shows probability slider (1-99%)
3. ✅ Slider updates percentage in real-time
4. ✅ Network request shows probability values (0.0-1.0)
5. ✅ Backend logs show fractional availability values
6. ✅ Predictions complete without errors
7. ✅ Win probabilities change based on injury status

---

**If everything works:** 🎉 The fractional injury system is fully functional!

**If you see errors:** Check the browser console and server logs for error messages.



