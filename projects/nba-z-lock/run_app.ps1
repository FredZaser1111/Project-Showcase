# PowerShell script to run the NBA Prediction Tool web app

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host "NBA Money Line Predictor" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
$venvPython = "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run the setup script first:" -ForegroundColor Yellow
    Write-Host "  .\install_and_setup.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Creating basic .env file..." -ForegroundColor Yellow
    @"
BALLDONTLIE_API_KEY=
API_TIER=free
RATE_LIMIT_PER_MIN=5
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "Please edit .env and add your API key" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting Flask application..." -ForegroundColor Green
Write-Host "Open your browser to: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the Flask app
& $venvPython app.py


