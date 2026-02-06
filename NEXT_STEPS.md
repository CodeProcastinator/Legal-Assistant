# ⚡ NEXT STEPS - Your Action Plan

## 🎯 Immediate Actions (Do These NOW!)

### Step 1: Get Gemini API Key (5 min)
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. **Copy and save the key!**

### Step 2: Test Locally (15 min)

**Windows:**
```powershell
cd legal-assistant
.\setup.bat
# After setup completes:
venv\Scripts\activate
streamlit run app.py
```

**Mac/Linux:**
```bash
cd legal-assistant
chmod +x setup.sh
./setup.sh
source venv/bin/activate
streamlit run app.py
```

### Step 3: Verify Everything Works
1. Open http://localhost:8501
2. **Setup API Key:**
   - Rename `.env.example` to `.env`
   - Paste your key in `.env`
   - Restart app
3. Upload `data/sample_contracts/vendor_contract_sample.txt`
4. Click "Analyze Contract"
5. Check all tabs work
6. Test export buttons

---

## 🚀 Deploy to Streamlit Cloud (30 min)

### Push to GitHub
```bash
cd legal-assistant
git init
git add .
git commit -m "Legal Assistant - GUVI Hackathon 2026"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/legal-assistant.git
git push -u origin main
```

### Deploy
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repo
5. Main file: `app.py`
6. Click "Deploy"

### Add Secrets
1. In Streamlit dashboard → App Settings → Secrets
2. Add:
```toml
GEMINI_API_KEY = "your-key-here"
```

### Your Live URL
`https://your-app.streamlit.app`

---

## 🎬 Record Demo (30 min)

1. Read `DEMO_SCRIPT.md`
2. Open Loom or OBS
3. Record 5-7 minute walkthrough
4. Upload to YouTube (unlisted) or Google Drive
5. Get shareable link

---

## 📋 Submission Checklist

- [ ] App deployed and working
- [ ] Live URL ready
- [ ] GitHub repo public
- [ ] Demo video recorded
- [ ] Demo video uploaded
- [ ] All links collected

### What You'll Submit:
1. **Live App URL**: https://your-app.streamlit.app
2. **GitHub URL**: https://github.com/username/legal-assistant
3. **Demo Video URL**: YouTube/Drive link

---

## ⏰ Time Estimates

| Task | Time |
|------|------|
| Get API Key | 5 min |
| Local Setup | 15 min |
| Testing | 10 min |
| GitHub Push | 10 min |
| Streamlit Deploy | 15 min |
| Demo Recording | 30 min |
| **Total** | **~1.5 hours** |

---

## 🆘 Quick Fixes

### "Module not found"
```bash
pip install -r requirements.txt
```

### "spaCy model error"
```bash
python -m spacy download en_core_web_sm
```

### "Streamlit command not found"
```bash
pip install streamlit
```

### "API error"
- Check API key is correct
- Ensure internet connection
- Try shorter contract text

---

## 🎉 YOU'VE GOT THIS!

The hard part is done - the code is complete and working.

Just:
1. ✅ Get API key
2. ✅ Deploy
3. ✅ Record
4. ✅ Submit

**GO DEPLOY AND WIN! 🚀**
