@echo off
setlocal enabledelayedexpansion

:: =============================================================================
:: Never-tired-archaeologist - Automatic Setup Script
:: =============================================================================
:: This script will:
:: 1. Check for Python 3.12
:: 2. Create virtual environment
:: 3. Install dependencies
:: 4. Start the application
:: =============================================================================

echo.
echo ========================================
echo  Never-tired-archaeologist Setup
echo  Version 3.0
echo ========================================
echo.

:: Check if Python 3.12 is available
echo [1/5] Checking Python 3.12...
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.12 not found!
    echo.
    echo Please install Python 3.12 first:
    echo   winget install Python.Python.3.12
    echo.
    echo Or download from:
    echo   https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
py -3.12 --version
echo [OK] Python 3.12 found!
echo.

:: Check if virtual environment exists
if exist ".venv" (
    echo [2/5] Virtual environment already exists, skipping creation...
) else (
    echo [2/5] Creating virtual environment...
    py -3.12 -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created!
)
echo.

:: Activate virtual environment
echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment activated!
echo.

:: Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded!
echo.

:: Install dependencies
echo [5/5] Installing dependencies...
echo This may take a few minutes...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    echo.
    echo Try running manually:
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo [OK] All dependencies installed!
echo.

:: Check for .env file
if exist ".env" (
    echo [INFO] .env file found - API keys configured!
) else (
    echo [WARNING] No .env file found!
    echo.
    echo The app will start, but you need API keys for full functionality.
    echo.
    echo To configure API keys:
    echo   1. Copy .env.example to .env
    echo   2. Add your ANTHROPIC_API_KEY and GOOGLE_API_KEY
    echo.
    echo Get API keys from:
    echo   - Anthropic: https://console.anthropic.com/
    echo   - Google AI: https://aistudio.google.com/app/apikey
    echo.
)

:: Setup complete
echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Starting Never-tired-archaeologist...
echo.
timeout /t 2 /nobreak >nul

:: Start the application
python main.py

:: If app closed, keep window open
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error!
    echo.
    pause
)

endlocal
