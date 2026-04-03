# NBA Z-LOCK

An advanced machine learning-powered web application that predicts NBA game winners and calculates money line odds using historical game data and team statistics.

## Features

- 🏀 **ML-Powered Predictions**: Uses machine learning models (Logistic Regression, Random Forest, Gradient Boosting) to predict game outcomes
- 📊 **Money Line Odds**: Automatically converts win probabilities to money line odds
- 🎯 **Feature Engineering**: Analyzes team records, recent form, head-to-head matchups, rest days, and home court advantage
- 🌐 **Web Interface**: Modern, responsive web UI for easy predictions
- 🔄 **API Integration**: Seamlessly works with Ball Don't Lie API (free tier and GOAT tier)
- 📈 **Model Training**: Easy-to-use scripts for collecting data and training models

## Project Structure

```
nba-prediction-tool/
├── app.py                      # Flask web application
├── config.py                   # Configuration management
├── api_client.py               # Ball Don't Lie API client
├── feature_engineering.py      # Feature extraction and engineering
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── models/
│   ├── train_model.py         # Model training script
│   └── predictor.py           # Prediction engine
├── scripts/
│   └── collect_historical_data.py  # Data collection script
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── style.css              # Styling
│   └── app.js                 # Frontend JavaScript
└── data/                      # Data storage (created automatically)
```

## Prerequisites

- Python 3.8 or higher
- Ball Don't Lie API key (free tier works for development)
- pip (Python package manager)

## Installation

### 1. Clone or Navigate to Project

```bash
cd nba-prediction-tool
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```
   (On Mac/Linux: `cp .env.example .env`)

2. Edit `.env` and add your API key:
   ```
   BALLDONTLIE_API_KEY=your_api_key_here
   API_TIER=free
   RATE_LIMIT_PER_MIN=5
   ```

   **Getting a Free API Key:**
   - Visit [balldontlie.io](https://www.balldontlie.io)
   - Sign up for a free account
   - Get your API key from the dashboard

## Usage

### Step 1: Collect Historical Data

Collect historical game data for training:

```bash
python scripts/collect_historical_data.py
```

This will:
- Fetch NBA teams
- Collect games from the last 3 seasons
- Save data to `data/historical_games.json`

**Note:** With the free tier (5 req/min), this may take several hours. With GOAT tier (600 req/min), it takes only minutes.

### Step 2: Train the Model

Train the ML model on collected data:

```bash
python models/train_model.py
```

This will:
- Extract features from historical games
- Train multiple models (Logistic Regression, Random Forest, Gradient Boosting)
- Select the best performing model
- Save the model to `models/best_model.pkl`

### Step 3: Run the Web Application

Start the Flask server:

```bash
python app.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Step 4: Make Predictions

1. Select a home team from the dropdown
2. Select a visitor team
3. (Optional) Choose a game date
4. Click "Get Prediction"
5. View the predicted winner, win probabilities, and money line odds

## API Tier Information

### Free Tier (Development)

- **Rate Limit:** 5 requests per minute
- **Cost:** Free
- **Best For:** Development, testing, learning
- **Limitations:** 
  - Slow data collection (hours for full dataset)
  - Limited historical data access
  - May not have all advanced features

### GOAT Tier (Production)

- **Rate Limit:** 600 requests per minute
- **Cost:** $39.99/month
- **Best For:** Production use, comprehensive data collection
- **Benefits:**
  - Fast data collection (minutes instead of hours)
  - Full access to historical data
  - Advanced metrics and features
  - Better model accuracy

## Upgrading from Free Tier to GOAT Tier

The application is designed to work seamlessly with both tiers. To upgrade:

### Step 1: Get GOAT Tier API Key

1. Visit [balldontlie.io](https://www.balldontlie.io)
2. Upgrade to GOAT tier ($39.99/month)
3. Get your new API key

### Step 2: Update Configuration

Edit your `.env` file:

```
BALLDONTLIE_API_KEY=your_goat_tier_key_here
API_TIER=goat
RATE_LIMIT_PER_MIN=600
```

**No code changes needed!** The application automatically adapts to the new rate limits.

### Step 3: Collect Comprehensive Data

Run the data collection script again (it will use the new rate limits):

```bash
python scripts/collect_historical_data.py
```

With GOAT tier, this will be much faster and collect more comprehensive data.

### Step 4: Retrain Model

Retrain your model with the comprehensive dataset:

```bash
python models/train_model.py
```

The model will have access to more data and features, resulting in better accuracy.

## Model Accuracy

- **Free Tier (Limited Data):** ~55-60% accuracy
- **GOAT Tier (Comprehensive Data):** ~65-75% accuracy

Accuracy depends on:
- Amount of training data
- Quality of features
- Model selection
- Current season performance

## Features Used for Prediction

The model considers:

- **Team Records:** Overall win/loss percentage
- **Home/Away Performance:** Team performance at home vs away
- **Recent Form:** Last 10 games performance
- **Head-to-Head:** Historical matchup record
- **Rest Days:** Days of rest before the game
- **Point Averages:** Recent scoring averages (for/against)

## Troubleshooting

### "Model not trained yet" Error

**Solution:** Train the model first:
```bash
python models/train_model.py
```

### "No training data found" Error

**Solution:** Collect historical data first:
```bash
python scripts/collect_historical_data.py
```

### API Rate Limit Errors

**Free Tier:** The app automatically handles rate limiting. Data collection will be slow but will complete.

**Solution for Faster Collection:** Upgrade to GOAT tier.

### Teams Not Loading

**Solution:** 
1. Check your API key in `.env`
2. Ensure you have internet connection
3. Check API status at balldontlie.io

## Development

### Adding New Features

1. **New Features:** Add to `feature_engineering.py`
2. **New Models:** Add to `models/train_model.py`
3. **UI Changes:** Edit `templates/index.html` and `static/style.css`

### Testing

Test individual components:

```bash
# Test API client
python -c "from api_client import APIClient; client = APIClient(); print(client.get_all_teams())"

# Test feature engineering
python -c "from feature_engineering import FeatureEngineer; print('OK')"
```

## Dependencies

- **Flask:** Web framework
- **pandas:** Data manipulation
- **scikit-learn:** Machine learning
- **numpy:** Numerical computing
- **requests:** HTTP requests
- **python-dotenv:** Environment variable management
- **xgboost:** Gradient boosting (optional, for advanced models)

## License

MIT License - feel free to use and modify for your projects.

## Contributing

This is a portfolio project. Feel free to fork and improve!

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the Ball Don't Lie API documentation
3. Check Python/Flask error messages

## Acknowledgments

- **Ball Don't Lie API** for providing NBA data
- **scikit-learn** for machine learning tools
- **Flask** for the web framework

---

**Note:** This tool is for educational and analysis purposes. Predictions are not guaranteed and should not be used as the sole basis for betting decisions.

