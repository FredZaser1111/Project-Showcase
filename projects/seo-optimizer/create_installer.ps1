# PowerShell Script to Create Start Menu Shortcut
# Users can run this after extracting the zip file

$appName = "Engineering Content Generator"
$exePath = Join-Path $PSScriptRoot "EngineeringContentGenerator.exe"
$startMenuPath = [Environment]::GetFolderPath("Programs")
$shortcutPath = Join-Path $startMenuPath "$appName.lnk"

Write-Host "Creating Start Menu shortcut..." -ForegroundColor Cyan

if (Test-Path $exePath) {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $exePath
    $Shortcut.WorkingDirectory = $PSScriptRoot
    $Shortcut.Description = "Engineering Content Generator - AI-Powered Q&A Post Generator"
    $Shortcut.Save()
    
    Write-Host "Shortcut created successfully!" -ForegroundColor Green
    Write-Host "Location: $shortcutPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "The app will now appear in your Start Menu!" -ForegroundColor Cyan
} else {
    Write-Host "Error: EngineeringContentGenerator.exe not found!" -ForegroundColor Red
    Write-Host "Make sure you're running this script from the extracted folder." -ForegroundColor Yellow
    exit 1
}
