# Streamlit Cloud Secrets Setup 🔐

## The Issue

Streamlit Cloud **doesn't automatically prompt** for secrets. You need to **manually add them** in the dashboard.

## How to Add Secrets

### Step 1: Go to Your App Dashboard
1. Visit: https://share.streamlit.io/
2. Sign in
3. Click on your app: `construction-bid-evaluator`

### Step 2: Open Secrets Settings
1. Click **"Settings"** (gear icon) in the bottom right
2. Click **"Secrets"** tab

### Step 3: Add Your API Keys
Paste this into the secrets editor:

```toml
OPENAI_API_KEY = "sk-your-openai-key-here"
SERPER_API_KEY = "your-serper-key-here"
LANGSMITH_API_KEY = "your-langsmith-key-here"
LANGSMITH_PROJECT = "bid-evaluation-agent"
```

**Important:**
- Replace the placeholder values with your actual keys
- Keep the quotes around the values
- `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT` are optional

### Step 4: Save and Restart
1. Click **"Save"**
2. The app will automatically restart
3. Wait for deployment to complete

## Verification

After adding secrets, your app should:
- ✅ Load without errors
- ✅ Show the upload interface
- ✅ Be ready to evaluate bids

## Troubleshooting

**Still getting API key errors?**
1. Verify secrets are saved (check the Secrets tab)
2. Make sure keys don't have extra spaces
3. Restart the app manually (Settings → Restart app)
4. Check logs for specific error messages

**Where to get API keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Serper**: https://serper.dev/api-key
- **LangSmith**: https://smith.langchain.com/ (optional)

---

**The code now handles missing secrets gracefully and will show a helpful error message if keys are not found.**

