# GenAI Legal Assistant - GUVI Hackathon 2026[

**AI-Powered Contract Analysis for Indian SMEs**

This tool helps small business owners analyze legal contracts, identify risks, and understand complex legal terms using Google Gemini AI.

## 🚀 Quick Start

1. **Setup**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure API Key**:
   - Create a file named `.env`
   - Add your key: `GEMINI_API_KEY=your_key_here`
   - (Get a free key from [Google AI Studio](https://makersuite.google.com/app/apikey))

3. **Run**:
   ```bash
   streamlit run app.py
   ```

## ✨ Key Features

- **🔍 Risk Detection**: Identifies 15+ common risks (Unfair termination, Liability, etc.)
- **🧠 AI Insights**: Explains clauses in plain English
- **🇮🇳 India-Specific**: Detects PAN, GSTIN, and Indian legal context
- **📝 Templates**: Includes standard contracts (Employment, NDA, Vendor, etc.)
- **📄 Reports**: Export analysis as PDF or Text

---
🌐 **Live Demo:** https://legal-assistant-q4sgmtbtlppkd8jwga9pmx.streamlit.app

*Built for GUVI Hackathon 2026 | For educational purposes only.*
