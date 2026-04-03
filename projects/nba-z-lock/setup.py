"""
Setup script to help initialize the NBA Prediction Tool.
"""
import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from example if it doesn't exist."""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    if env_example.exists():
        print("Creating .env file from env.example...")
        with open(env_example, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("✓ Created .env file")
        print("  Please edit .env and add your Ball Don't Lie API key")
    else:
        print("⚠ env.example not found, creating basic .env file...")
        with open(env_file, 'w') as f:
            f.write("BALLDONTLIE_API_KEY=\n")
            f.write("API_TIER=free\n")
            f.write("RATE_LIMIT_PER_MIN=5\n")
        print("✓ Created basic .env file")

def create_directories():
    """Create necessary directories."""
    dirs = ['data', 'data/cache', 'models', 'static', 'templates']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✓ Created necessary directories")

def check_dependencies():
    """Check if required packages are installed."""
    required = ['flask', 'pandas', 'sklearn', 'numpy', 'requests', 'dotenv']
    missing = []
    
    for package in required:
        try:
            if package == 'sklearn':
                __import__('sklearn')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠ Missing packages: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False
    else:
        print("✓ All required packages are installed")
        return True

def main():
    """Main setup function."""
    print("=" * 60)
    print("NBA Money Line Predictor - Setup")
    print("=" * 60)
    print()
    
    print("1. Creating directories...")
    create_directories()
    print()
    
    print("2. Setting up environment file...")
    create_env_file()
    print()
    
    print("3. Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    print("=" * 60)
    if deps_ok:
        print("Setup complete! ✓")
        print()
        print("Next steps:")
        print("1. Edit .env and add your Ball Don't Lie API key")
        print("2. Run: python scripts/collect_historical_data.py")
        print("3. Run: python models/train_model.py")
        print("4. Run: python app.py")
    else:
        print("Setup incomplete - please install missing dependencies")
    print("=" * 60)

if __name__ == '__main__':
    main()

