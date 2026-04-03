"""
Configuration management for NBA Prediction Tool.
Reads settings from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
# Choose API: 'balldontlie' or 'nba_api'
API_PROVIDER = os.getenv('API_PROVIDER', 'nba_api').lower()

API_KEY = os.getenv('BALLDONTLIE_API_KEY', '')
API_TIER = os.getenv('API_TIER', 'free').lower()
RATE_LIMIT_PER_MIN = int(os.getenv('RATE_LIMIT_PER_MIN', '5'))

# API Base URL
API_BASE_URL = 'https://api.balldontlie.io/v1'

# Rate limits by tier
TIER_RATE_LIMITS = {
    'free': 5,
    'goat': 600
}

# If tier is specified, override rate limit
if API_TIER in TIER_RATE_LIMITS:
    RATE_LIMIT_PER_MIN = TIER_RATE_LIMITS[API_TIER]

# Data storage paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Flask configuration
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))

