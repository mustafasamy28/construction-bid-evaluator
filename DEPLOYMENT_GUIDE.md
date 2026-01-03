# Deployment Guide - Streamlit Community Cloud

## Quick Deploy (5 minutes)

### Option 1: Streamlit Community Cloud (Recommended - Free)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/construction-bid-evaluator.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Add Secrets (API Keys)**
   - In Streamlit Cloud dashboard, go to "Settings" → "Secrets"
   - Add your API keys:
   ```toml
   OPENAI_API_KEY = "your_openai_key"
   SERPER_API_KEY = "your_serper_key"
   LANGSMITH_API_KEY = "your_langsmith_key"
   LANGSMITH_PROJECT = "bid-evaluation-agent"
   ```

4. **Done!** Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## Option 2: Docker Deployment

### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Deploy to Railway/Render/Fly.io
- Push to GitHub
- Connect repository to platform
- Set environment variables
- Deploy!

---

## Option 3: Local Network Sharing

### Run with custom port
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Access from other devices
- Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Access: `http://YOUR_IP:8501`

---

## Environment Variables Setup

### For Streamlit Cloud (Secrets)
Create `.streamlit/secrets.toml` in Streamlit Cloud dashboard:
```toml
OPENAI_API_KEY = "sk-..."
SERPER_API_KEY = "..."
LANGSMITH_API_KEY = "..."  # Optional
LANGSMITH_PROJECT = "bid-evaluation-agent"  # Optional
```

### For Docker/Other Platforms
Set environment variables:
```bash
export OPENAI_API_KEY="sk-..."
export SERPER_API_KEY="..."
export LANGSMITH_API_KEY="..."  # Optional
export LANGSMITH_PROJECT="bid-evaluation-agent"  # Optional
```

---

## Troubleshooting

### App won't start
- Check `requirements-deploy.txt` is correct
- Verify `app.py` is in root directory
- Check Streamlit Cloud logs for errors

### API keys not working
- Verify secrets are set correctly in Streamlit Cloud
- Check key names match exactly (case-sensitive)
- Restart app after adding secrets

### Import errors
- Ensure all dependencies in `requirements-deploy.txt`
- Check Python version (3.9+)

### Slow performance
- Serper API calls can be slow (30s timeout)
- Consider caching contractor profiles
- Monitor LangSmith for bottlenecks

---

## Security Notes

- ✅ Never commit `.env` file (already in `.gitignore`)
- ✅ Use Streamlit Cloud secrets for API keys
- ✅ Don't hardcode API keys in code
- ✅ Use environment variables in production

---

## Cost Considerations

### Free Tier Limits
- **Streamlit Cloud**: Free, unlimited apps
- **OpenAI API**: Pay per use (~$0.15 per evaluation)
- **Serper API**: Free tier available, then pay per search
- **LangSmith**: Free tier available

### Estimated Costs
- **Per evaluation**: ~$0.15-0.30 (depending on bids count)
- **Serper searches**: ~$0.001 per contractor search
- **Monthly (100 evaluations)**: ~$15-30

---

## Post-Deployment Checklist

- [ ] Test with sample JSON file
- [ ] Verify API keys work
- [ ] Check error handling
- [ ] Test with multiple bids
- [ ] Verify Serper searches work
- [ ] Check LangSmith tracing (if enabled)
- [ ] Share link with team

---

## Quick Start Commands

```bash
# 1. Initialize git (if not done)
git init
git add .
git commit -m "Ready for deployment"

# 2. Push to GitHub
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main

# 3. Deploy on Streamlit Cloud
# Go to https://share.streamlit.io and follow steps above
```

---

*Your app will be live in minutes! 🚀*

