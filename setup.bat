@echo off
echo ========================================
echo  GenAI Legal Assistant - Windows Setup
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.9+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [5/5] Downloading spaCy model...
python -m spacy download en_core_web_sm

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To run the application:
echo   1. Activate: venv\Scripts\activate
echo   2. Run: streamlit run app.py
echo.
echo Get your FREE Gemini API key at:
echo   https://makersuite.google.com/app/apikey
echo.
pause
