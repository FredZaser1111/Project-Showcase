@echo off
REM Diagnostics script for Engineering Content Generator
REM This helps identify issues when the app won't start

echo ========================================
echo Engineering Content Generator
echo Diagnostics Tool
echo ========================================
echo.

echo [1/8] Checking Windows version...
ver
echo.

echo [2/8] Checking Python installation...
python --version 2>nul
if %errorlevel% neq 0 (
    echo   WARNING: Python not found in PATH (this is OK for standalone exe)
) else (
    echo   OK: Python found
)
echo.

echo [3/8] Checking if port 5001 is available...
netstat -ano | findstr :5001 >nul
if %errorlevel% equ 0 (
    echo   WARNING: Port 5001 is in use!
    echo   Finding process using port 5001...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
        echo   Process ID: %%a
        tasklist /FI "PID eq %%a" /FO LIST | findstr "Image Name"
    )
) else (
    echo   OK: Port 5001 is available
)
echo.

echo [4/8] Checking Windows Firewall...
netsh advfirewall firewall show rule name="Engineering Content Generator" >nul 2>&1
if %errorlevel% equ 0 (
    echo   OK: Firewall rule exists
) else (
    echo   INFO: No firewall rule found (may need to allow app through firewall)
)
echo.

echo [5/8] Checking file permissions...
if exist "EngineeringContentGenerator.exe" (
    echo   OK: Executable found
    icacls "EngineeringContentGenerator.exe" | findstr /C:"Everyone" /C:"Users" >nul
    if %errorlevel% equ 0 (
        echo   OK: File permissions look good
    ) else (
        echo   WARNING: May have permission issues
    )
) else (
    echo   ERROR: Executable not found in current directory!
    echo   Current directory: %CD%
)
echo.

echo [6/8] Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| findstr /C:"bytes free"') do set freespace=%%a
echo   Free space: %freespace% bytes
echo.

echo [7/8] Checking antivirus exclusions...
echo   INFO: Check Windows Security for exclusions
echo   Path: Windows Security ^> Virus ^& threat protection ^> Manage settings ^> Exclusions
echo.

echo [8/8] Checking required files...
if exist "_internal" (
    echo   OK: _internal folder found
) else (
    echo   ERROR: _internal folder not found! App may not be properly extracted.
)
if exist "frontend" (
    echo   OK: frontend folder found
) else (
    echo   ERROR: frontend folder not found!
)
echo.

echo ========================================
echo Diagnostics Complete
echo ========================================
echo.
echo Common Solutions:
echo   1. If port 5001 is in use: Close other applications or change port
echo   2. If Windows Defender blocks: Add exception in Windows Security
echo   3. If files missing: Make sure you extracted the entire zip file
echo   4. If permission errors: Try running as Administrator
echo.
echo Press any key to exit...
pause >nul

