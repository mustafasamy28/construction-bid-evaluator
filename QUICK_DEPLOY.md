# Quick Deploy Guide 🚀

## Deploy to Streamlit Cloud (5 minutes)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to **https://share.streamlit.io/**
2. Click **"Sign in"** (use GitHub)
3. Click **"New app"**
4. Select your repository
5. Set **Main file path**: `app.py`
6. Click **"Deploy"**

### Step 3: Add API Keys (Secrets)
1. In Streamlit Cloud dashboard → **"Settings"** → **"Secrets"**
2. Paste this and fill in your keys:
```toml
OPENAI_API_KEY = "sk-your-key-here"
SERPER_API_KEY = "your-serper-key"
LANGSMITH_API_KEY = "your-langsmith-key"  # Optional
LANGSMITH_PROJECT = "bid-evaluation-agent"  # Optional
```
3. Click **"Save"**
4. App will auto-restart

### Step 4: Share Your Link! 🎉
Your app is live at: `https://YOUR_APP_NAME.streamlit.app`

---

## What You Need

- ✅ GitHub account (free)
- ✅ OpenAI API key
- ✅ Serper API key (get from https://serper.dev)
- ✅ Streamlit Cloud account (free)

---

## Troubleshooting

**App won't start?**
- Check `requirements-deploy.txt` exists
- Verify `app.py` is in root directory
- Check Streamlit Cloud logs

**API keys not working?**
- Verify secrets are saved correctly
- Check key names match exactly
- Restart app after adding secrets

**Import errors?**
- Ensure all files are committed to GitHub
- Check Python version (3.9+)

---

## Files Created for Deployment

- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.gitignore` - Excludes sensitive files
- ✅ `requirements-deploy.txt` - Production dependencies
- ✅ `DEPLOYMENT_GUIDE.md` - Full deployment guide

---

**That's it! Your app will be live in minutes.** 🎊

