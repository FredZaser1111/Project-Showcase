# Quick Start - Get Running in 40 Minutes

## ✅ FASTEST PATH (You Already Have Everything!)

Since you have a trained model and data, you can start **RIGHT NOW**:

### Step 1: Check Virtual Environment (30 seconds)
```powershell
# Make sure venv exists and is activated
.\venv\Scripts\Activate.ps1
```

### Step 2: Start the App (10 seconds)
```powershell
python app.py
```

**OR use the PowerShell script:**
```powershell
.\run_app.ps1
```

### Step 3: Open Browser
Navigate to: **http://127.0.0.1:5000**

---

## ⚡ What You Already Have (No Setup Needed!)

✅ **Trained Model**: `models/best_model.pkl`
✅ **Historical Data**: `data/historical_games.json`  
✅ **Training Data**: `data/training_data.csv`
✅ **Model Files**: scaler, feature_names

---

## 🔧 If Something Doesn't Work:

### Issue: "Module not found" or dependencies missing
```powershell
# Reinstall dependencies (2 minutes)
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: ".env file not found" 
**You might not need it for predictions!** The app will try to load historical data from files first.

But if you want to fetch new data:
1. Create `.env` file:
   ```
   BALLDONTLIE_API_KEY=your_key_here
   API_TIER=free
   RATE_LIMIT_PER_MIN=5
   ```
2. Get API key from: https://balldontlie.io

### Issue: "Model not found"
This shouldn't happen since you have `models/best_model.pkl`, but if it does:
```powershell
# Quick retrain (10-15 minutes if you have data)
python models/train_model.py
```

### Issue: "No historical games data"
This shouldn't happen since you have `data/historical_games.json`, but if it does:
- The app can still work with limited data
- Or collect more: `python scripts/collect_historical_data.py` (takes hours on free tier)

---

## 🎯 TIME BREAKDOWN:

- **Start App**: 10 seconds
- **Troubleshooting**: 0-5 minutes (if needed)
- **Total**: < 5 minutes if everything works!

You're already set up! Just start the app! 🚀

