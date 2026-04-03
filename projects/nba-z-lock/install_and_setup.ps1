# PowerShell script to set up Python virtual environment for NBA Prediction Tool

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NBA Prediction Tool - Python Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for Python installations
$pythonPaths = @()
$pythonVersions = @()

# Check common Python locations
$possiblePaths = @(
    "python",
    "python3",
    "py",
    "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
    "$env:PROGRAMFILES\Python*\python.exe",
    "$env:PROGRAMFILES(X86)\Python*\python.exe"
)

Write-Host "Checking for Python installation..." -ForegroundColor Yellow

foreach ($path in $possiblePaths) {
    try {
        if ($path -like "*\*") {
            # It's a wildcard path, try to resolve it
            $resolved = Resolve-Path $path -ErrorAction SilentlyContinue
            if ($resolved) {
                $pythonExe = $resolved[0].Path
                $version = & $pythonExe --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $pythonPaths += $pythonExe
                    $pythonVersions += $version
                    Write-Host "  Found: $pythonExe - $version" -ForegroundColor Green
                }
            }
        } else {
            # Try to run it directly
            $version = & $path --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $version -notlike "*was not found*") {
                $pythonPaths += $path
                $pythonVersions += $version
                Write-Host "  Found: $path - $version" -ForegroundColor Green
            }
        }
    } catch {
        # Continue checking other paths
    }
}

if ($pythonPaths.Count -eq 0) {
    Write-Host ""
    Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.11 (recommended):" -ForegroundColor Yellow
    Write-Host "  Note: CPython is the standard Python - just install 'Python' from python.org" -ForegroundColor Cyan
    Write-Host "  1. Visit: https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "  2. Download Python 3.11.x (this is CPython - the standard implementation)" -ForegroundColor Cyan
    Write-Host "  3. During installation, check 'Add Python to PATH'" -ForegroundColor Cyan
    Write-Host "  4. Restart your terminal after installation" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or install via Microsoft Store:" -ForegroundColor Yellow
    Write-Host "  1. Open Microsoft Store" -ForegroundColor Cyan
    Write-Host "  2. Search for 'Python 3.11'" -ForegroundColor Cyan
    Write-Host "  3. Install and restart terminal" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Use the first found Python
$pythonCmd = $pythonPaths[0]
Write-Host ""
Write-Host "Using Python: $pythonCmd" -ForegroundColor Green
Write-Host "Version: $($pythonVersions[0])" -ForegroundColor Green
Write-Host ""

# Check Python version
$versionOutput = & $pythonCmd --version 2>&1
$versionMatch = $versionOutput -match "Python (\d+)\.(\d+)"
if ($versionMatch) {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "Warning: Python 3.8+ is required. Found: $versionOutput" -ForegroundColor Yellow
        Write-Host "Please upgrade Python and try again." -ForegroundColor Yellow
        exit 1
    }
}

# Navigate to project directory
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host "Project directory: $projectDir" -ForegroundColor Cyan
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists" -ForegroundColor Yellow
    $overwrite = Read-Host "  Overwrite? (y/N)"
    if ($overwrite -eq "y" -or $overwrite -eq "Y") {
        Remove-Item -Recurse -Force "venv"
        Write-Host "  Removed existing virtual environment" -ForegroundColor Green
    } else {
        Write-Host "  Using existing virtual environment" -ForegroundColor Green
        $venvPython = "venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            $pythonCmd = $venvPython
        }
    }
}

if (-not (Test-Path "venv")) {
    & $pythonCmd -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Virtual environment created successfully" -ForegroundColor Green
}

# Activate virtual environment
$venvPython = "venv\Scripts\python.exe"
$venvPip = "venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "  Virtual environment Python not found at $venvPython" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Virtual environment Python: $venvPython" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
Write-Host "  pip upgraded" -ForegroundColor Green

# Install requirements
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  All dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  Some dependencies may have failed to install" -ForegroundColor Yellow
    }
} else {
    Write-Host "  requirements.txt not found" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "Setting up configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "  Created .env file from template" -ForegroundColor Green
        Write-Host "  Please edit .env and add your Ball Don't Lie API key" -ForegroundColor Yellow
    } else {
        @"
BALLDONTLIE_API_KEY=
API_TIER=free
RATE_LIMIT_PER_MIN=5
"@ | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "  Created basic .env file" -ForegroundColor Green
    }
} else {
    Write-Host "  .env file already exists" -ForegroundColor Green
}

# Create directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Yellow
$dirs = @("data", "data\cache", "models", "static", "templates")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env and add your Ball Don't Lie API key" -ForegroundColor Cyan
Write-Host "2. Activate virtual environment:" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "3. Test API connection:" -ForegroundColor Cyan
Write-Host "   python scripts\test_api.py" -ForegroundColor White
Write-Host "4. Collect data:" -ForegroundColor Cyan
Write-Host "   python scripts\collect_historical_data.py" -ForegroundColor White
Write-Host "5. Train model:" -ForegroundColor Cyan
Write-Host "   python models\train_model.py" -ForegroundColor White
Write-Host "6. Run the app:" -ForegroundColor Cyan
Write-Host "   python app.py" -ForegroundColor White
Write-Host ""
Write-Host "Then open: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host ""

