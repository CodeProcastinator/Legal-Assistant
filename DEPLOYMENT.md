# Deployment Guide

## Streamlit Cloud (Recommended - Free!)

### 1. Prepare Repository

```bash
# Initialize git
cd legal-assistant
git init
git add .
git commit -m "Initial commit - Legal Assistant"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/legal-assistant.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `app.py`
6. Click "Deploy"

### 3. Configure Secrets

In Streamlit Cloud dashboard:
1. Go to App Settings → Secrets
2. Add:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

### 4. Your App is Live!

URL: `https://your-app-name.streamlit.app`

---

## Alternative: Render.com

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: legal-assistant
    env: python
    buildCommand: pip install -r requirements.txt && python -m spacy download en_core_web_sm
    startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

2. Connect GitHub repo to Render
3. Deploy

---

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy app
COPY . .

# Expose port
EXPOSE 8501

# Run
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build & Run
```bash
docker build -t legal-assistant .
docker run -p 8501:8501 -e GEMINI_API_KEY="your-key" legal-assistant
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| GEMINI_API_KEY | Google Gemini API key | For AI features |
| PORT | Server port (default: 8501) | No |

---

## Post-Deployment Checklist

- [ ] App loads correctly
- [ ] File upload works
- [ ] Analysis completes
- [ ] AI features work (if API key set)
- [ ] Export buttons functional
- [ ] Templates load correctly
