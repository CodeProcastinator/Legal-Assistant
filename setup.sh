#!/bin/bash

echo "========================================"
echo " GenAI Legal Assistant - Setup Script"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found! Please install Python 3.9+"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Upgrading pip..."
pip install --upgrade pip

echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[5/5] Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "To run the application:"
echo "  1. Activate: source venv/bin/activate"
echo "  2. Run: streamlit run app.py"
echo ""
echo "Get your FREE Gemini API key at:"
echo "  https://makersuite.google.com/app/apikey"
