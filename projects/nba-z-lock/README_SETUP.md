# Setup Instructions for NBA Prediction Tool

## Quick Setup (Recommended)

### Step 1: Install Python

**Note:** CPython is the standard Python implementation. When you download Python from python.org, you're getting CPython - no need to specify it separately!

If you don't have Python installed:

1. **Download Python 3.11** (recommended) from [python.org](https://www.python.org/downloads/)
   - This is CPython (the standard Python implementation)
   - Look for "Python 3.11.x" in the downloads section
2. **During installation**, make sure to check **"Add Python to PATH"**
3. **Restart your terminal** after installation

Or install via **Microsoft Store**:
- Search for "Python 3.11"
- Install and restart terminal

### Step 2: Run Setup Script

Open PowerShell in the project directory and run:

```powershell
.\install_and_setup.ps1
```

This script will:
- ✅ Check for Python installation
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Create configuration files
- ✅ Set up directories

### Step 3: Configure API Key

1. Edit the `.env` file
2. Add your Ball Don't Lie API key:
   ```
   BALLDONTLIE_API_KEY=your_api_key_here
   ```

Get your API key from [balldontlie.io](https://www.balldontlie.io)

### Step 4: Run the App

```powershell
.\run_app.ps1
```

Or manually:
```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

Then open: **http://127.0.0.1:5000**

## Manual Setup

If the script doesn't work, follow these steps:

### 1. Create Virtual Environment

```powershell
python -m venv venv
```

### 2. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create .env File

Copy `env.example` to `.env` and add your API key.

### 5. Run the App

```powershell
python app.py
```

## Troubleshooting

### "Python was not found"

- Install Python 3.11 from [python.org](https://www.python.org/downloads/)
  - Note: This installs CPython (the standard Python - no need to specify it)
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal after installation

### "Execution Policy" Error

If you get an execution policy error when running `.ps1` scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Module not found" Errors

Make sure you've activated the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```

Then install requirements:
```powershell
pip install -r requirements.txt
```

### Port Already in Use

If port 5000 is already in use, edit `.env` and change:
```
FLASK_PORT=5001
```

## Next Steps

After setup:

1. **Test API**: `python scripts\test_api.py`
2. **Collect Data**: `python scripts\collect_historical_data.py`
3. **Train Model**: `python models\train_model.py`
4. **Run App**: `python app.py`

See [README.md](README.md) for full documentation.

