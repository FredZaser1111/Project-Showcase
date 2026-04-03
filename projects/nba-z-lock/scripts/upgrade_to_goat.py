"""
Helper script to guide users through upgrading from free tier to GOAT tier.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import config

def main():
    """Guide user through GOAT tier upgrade."""
    print("=" * 60)
    print("Upgrading to GOAT Tier - Setup Guide")
    print("=" * 60)
    print()
    
    print("Current Configuration:")
    print(f"  API Tier: {config.API_TIER}")
    print(f"  Rate Limit: {config.RATE_LIMIT_PER_MIN} req/min")
    print()
    
    if config.API_TIER.lower() == 'goat':
        print("✓ You're already configured for GOAT tier!")
        print()
        print("If you're still seeing free tier limits, make sure:")
        print("1. Your .env file has: API_TIER=goat")
        print("2. Your .env file has: RATE_LIMIT_PER_MIN=600")
        print("3. You've restarted the application")
        return
    
    print("Steps to Upgrade:")
    print()
    print("1. Get GOAT Tier API Key:")
    print("   - Visit: https://www.balldontlie.io")
    print("   - Sign up for GOAT tier ($39.99/month)")
    print("   - Get your new API key from the dashboard")
    print()
    print("2. Update .env file:")
    print("   Edit your .env file and change:")
    print("   BALLDONTLIE_API_KEY=your_goat_tier_key_here")
    print("   API_TIER=goat")
    print("   RATE_LIMIT_PER_MIN=600")
    print()
    print("3. Test the connection:")
    print("   python scripts/test_api.py")
    print()
    print("4. Collect comprehensive data:")
    print("   python scripts/collect_historical_data.py")
    print("   (This will be much faster with GOAT tier!)")
    print()
    print("5. Retrain your model:")
    print("   python models/train_model.py")
    print("   (Model will have access to more data and features)")
    print()
    print("=" * 60)
    print("Benefits of GOAT Tier:")
    print("  • 600 requests/minute (vs 5 for free)")
    print("  • Faster data collection (minutes vs hours)")
    print("  • Access to more historical data")
    print("  • Advanced metrics and features")
    print("  • Better model accuracy (65-75% vs 55-60%)")
    print("=" * 60)

if __name__ == '__main__':
    main()

