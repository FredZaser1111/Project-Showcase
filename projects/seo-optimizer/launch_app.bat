@echo off
REM Launcher script that waits for server to start before opening browser
REM This prevents "website temporarily down" errors

echo Starting Engineering Content Generator...
echo Please wait while the server starts...
echo.

REM Start the app in the background
start "" "%~dp0EngineeringContentGenerator.exe"

REM Wait for server to be ready (check if port 5001 is listening)
echo Waiting for server to start...
timeout /t 15 /nobreak >nul

REM Try to connect to the server (retry up to 10 times)
set RETRIES=0
:CHECK_SERVER
set /a RETRIES+=1
if %RETRIES% GTR 10 (
    echo Server is taking longer than expected to start.
    echo Please check the console window for errors.
    echo You can manually open: http://localhost:5001
    pause
    exit /b
)

REM Check if port 5001 is listening
netstat -an | findstr ":5001" | findstr "LISTENING" >nul
if %ERRORLEVEL% EQU 0 (
    echo Server is ready!
    echo Opening browser...
    timeout /t 2 /nobreak >nul
    start http://localhost:5001
    exit /b
) else (
    echo Still waiting... (%RETRIES%/10)
    timeout /t 2 /nobreak >nul
    goto CHECK_SERVER
)

