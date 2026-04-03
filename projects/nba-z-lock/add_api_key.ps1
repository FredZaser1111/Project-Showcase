# Helper script to add API key to .env file

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Add Ball Don't Lie API Key" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
$envFile = ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    if (Test-Path "env.example") {
        Copy-Item "env.example" $envFile
    } else {
        @"
BALLDONTLIE_API_KEY=
API_TIER=free
RATE_LIMIT_PER_MIN=5
"@ | Out-File -FilePath $envFile -Encoding utf8
    }
}

Write-Host "Current .env configuration:" -ForegroundColor Yellow
Write-Host ""
Get-Content $envFile | ForEach-Object {
    if ($_ -match "BALLDONTLIE_API_KEY") {
        if ($_ -match "BALLDONTLIE_API_KEY=$") {
            Write-Host "  $_ (empty)" -ForegroundColor Red
        } else {
            $key = $_ -replace "BALLDONTLIE_API_KEY=", ""
            $masked = if ($key.Length -gt 10) { $key.Substring(0, 10) + "..." } else { "***" }
            Write-Host "  BALLDONTLIE_API_KEY=$masked" -ForegroundColor Green
        }
    } else {
        Write-Host "  $_" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Enter your Ball Don't Lie API key:" -ForegroundColor Cyan
Write-Host "(Get it from: https://www.balldontlie.io)" -ForegroundColor Gray
Write-Host ""
$apiKey = Read-Host "API Key"

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host ""
    Write-Host "No API key entered. Exiting." -ForegroundColor Yellow
    exit 0
}

# Update .env file
$content = Get-Content $envFile
$newContent = @()
$keyUpdated = $false

foreach ($line in $content) {
    if ($line -match "^BALLDONTLIE_API_KEY=") {
        $newContent += "BALLDONTLIE_API_KEY=$apiKey"
        $keyUpdated = $true
    } else {
        $newContent += $line
    }
}

# If key wasn't found, add it
if (-not $keyUpdated) {
    $newContent = @("BALLDONTLIE_API_KEY=$apiKey") + $newContent
}

$newContent | Out-File -FilePath $envFile -Encoding utf8

Write-Host ""
Write-Host "API key added successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart the Flask app (if running)" -ForegroundColor Cyan
Write-Host "2. Refresh your browser" -ForegroundColor Cyan
Write-Host "3. Teams should now load in the dropdown" -ForegroundColor Cyan
Write-Host ""
