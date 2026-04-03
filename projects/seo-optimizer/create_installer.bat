@echo off
REM Batch script to create Start Menu shortcut
REM Users can double-click this after extracting the zip file

echo Creating Start Menu shortcut for Engineering Content Generator...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0create_installer.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Success! The app is now in your Start Menu.
    echo You can close this window.
) else (
    echo.
    echo Error occurred. Please check the error message above.
)

pause

