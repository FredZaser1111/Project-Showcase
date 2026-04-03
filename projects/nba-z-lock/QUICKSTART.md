# Quick Start Guide

Get up and running with the NBA Money Line Predictor in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Get API Key

1. Visit [balldontlie.io](https://www.balldontlie.io)
2. Sign up for a free account
3. Get your API key from the dashboard

## Step 3: Configure

```bash
# Copy example environment file
copy env.example .env
# (On Mac/Linux: cp env.example .env)

# Edit .env and add your API key
# BALLDONTLIE_API_KEY=your_key_here
```

## Step 4: Collect Data (Optional for Testing)

For a quick test, you can skip this step and use sample data. But for best results:

```bash
python scripts/collect_historical_data.py
```

**Note:** With free tier (5 req/min), this takes several hours. With GOAT tier (600 req/min), it takes minutes.

## Step 5: Train Model

```bash
python models/train_model.py
```

This will:
- Extract features from historical games
- Train multiple ML models
- Select the best one
- Save it for predictions

## Step 6: Run the App

```bash
python app.py
```

Then open your browser to: `http://127.0.0.1:5000`

## Step 7: Make Predictions!

1. Select a home team
2. Select a visitor team
3. Click "Get Prediction"
4. View win probabilities and money line odds!

## Troubleshooting

### "Model not trained yet"
→ Run `python models/train_model.py`

### "No training data found"
→ Run `python scripts/collect_historical_data.py`

### "API key not found"
→ Check your `.env` file has `BALLDONTLIE_API_KEY=your_key`

## Need Help?

See the full [README.md](README.md) for detailed documentation.

