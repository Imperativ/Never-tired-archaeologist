@echo off
echo ======================================================================
echo Never-Tired-Archaeologist Web Interface
echo ======================================================================
echo.
echo Starting web server...
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Loading database and starting Flask server...
echo.
echo Open your browser and navigate to:
echo.
echo     http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.
echo ======================================================================
echo.

.venv\Scripts\python.exe web_interface.py

pause
