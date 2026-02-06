# ⚡ Quick Start Guide

Get the Legal Assistant running in 5 minutes!

## Step 1: Get Gemini API Key (Free!)

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key

## Step 2: Install & Run

### Windows
```powershell
cd legal-assistant
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

### Mac/Linux
```bash
cd legal-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

## Step 3: Use the App

1. Open http://localhost:8501
2. Paste API key in sidebar
3. Upload a contract (PDF/DOCX/TXT)
4. Click "Analyze Contract"
5. Review results in tabs

## Sample Contract

Test with: `data/sample_contracts/vendor_contract_sample.txt`

## Common Issues

### "spacy model not found"
```bash
python -m spacy download en_core_web_sm
```

### "streamlit not found"
```bash
pip install streamlit
```

### API errors
- Check API key is correct
- Ensure you have internet connection
- Try a simpler/shorter contract

## Need Help?

- Check README.md for detailed docs
- Look at DEPLOYMENT.md for hosting
