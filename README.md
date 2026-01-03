# Construction Bid Evaluation Agent 🏗️

AI-powered bid evaluation system using LangGraph, GPT-4o-mini/GPT-4o, and Serper web search to help construction project managers make data-driven decisions.

## ✨ Features

- **3-Step AI Evaluation**: Parse → Score → Critique workflow
- **Web Research Integration**: Real-time contractor reputation data via Serper API
- **Red Flag Detection**: Automatically identifies incomplete scopes, suspicious pricing, and reputation issues
- **Dual-Model Architecture**: Cost-effective GPT-4o-mini for bulk operations, GPT-4o for critical decisions
- **Comprehensive Scoring**: 5-dimensional scoring (Cost, Timeline, Scope, Risk, Reputation)
- **Error Handling**: Graceful degradation with comprehensive error handling
- **Production Ready**: Input validation, logging, and test suite included

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key
- Serper API key (get from https://serper.dev)
- LangSmith API key (optional, for tracing)

### Installation

1. **Clone and install dependencies:**
```bash
git clone <your-repo-url>
cd "Construction tender"
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file in the project root:
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Optional (for tracing/monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=bid-evaluation-agent
```

3. **Verify setup:**
```bash
python check_env.py
```

4. **Run the app:**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 Usage

1. **Prepare your JSON file** with project description and bids (see `example_input.json` or files in `bids/` folder)
2. **Upload** the JSON file in the Streamlit interface
3. **Click "Evaluate Bids"** - The system will:
   - Extract project requirements
   - Search web for contractor reputation data
   - Score each bid across 5 dimensions
   - Detect red flags
   - Provide final recommendation
4. **Review results**: Scores, red flags, and recommendation with confidence levels

### Input Format
```json
{
  "project": {
    "description": "Your project description with requirements, budget, timeline..."
  },
  "bids": [
    {
      "id": "bid_1",
      "contractor_name": "Contractor Name",
      "cost": 1000000,
      "timeline_months": 12,
      "scope": "Detailed scope description",
      "warranty_years": 2
    }
  ]
}
```

## 🏗️ Architecture

### 3-Step LangGraph Workflow

```
┌─────────────────┐
│  Parse & Enrich │  GPT-4o-mini
│  - Extract reqs │  - Extracts requirements
│  - Serper search│  - Web research (parallel)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Score & Flag   │  GPT-4o-mini
│  - Score bids   │  - 5-dimension scoring
│  - Detect flags │  - Red flag detection
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Critique & Final│  GPT-4o
│  - Self-review  │  - Quality check
│  - Recommend    │  - Final decision
└─────────────────┘
```

### Key Components

- **`src/graph.py`**: LangGraph workflow definition
- **`src/nodes/`**: Three evaluation nodes (parse, score, critique)
- **`src/tools/serper.py`**: Async web search wrapper
- **`src/schemas.py`**: Pydantic models for structured outputs
- **`src/config.py`**: Model configuration and API keys

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Cost | 25% | Cost competitiveness vs market |
| Timeline | 20% | Timeline feasibility |
| Scope | 25% | Scope completeness |
| Risk | 15% | Financial/technical risk |
| Reputation | 15% | Contractor reputation (70% Serper + 30% LLM) |

## 🧪 Testing

Run the automated test suite:
```bash
pytest tests/test_graph.py -v
```

### Test Cases
- `clear_winner.json` - One clearly superior bid
- `all_bids_bad.json` - All bids should be rejected
- `gaming_attempt.json` - Lowball cost detection
- `incomplete_bid.json` - Missing scope items
- `close_call.json` - Multiple competitive bids

## 🔍 Key Features & Improvements

### Error Handling
- ✅ Graceful Serper API failure handling (returns default profiles)
- ✅ Input validation in all nodes
- ✅ Comprehensive error messages
- ✅ Fallback recommendations on errors

### Serper Integration
- ✅ Parallel async searches for all contractors
- ✅ Recency filter (last 12 months)
- ✅ Source credibility weighting (news > blogs)
- ✅ **Enforced usage**: 70% Serper reputation + 30% LLM reputation
- ✅ Automatic score adjustments based on web research

### Red Flag Detection
- ✅ Incomplete scope detection (threshold: 0.7)
- ✅ Suspiciously low cost detection (multiple methods)
- ✅ Vague timeline detection
- ✅ Poor reputation from web research
- ✅ Scope text analysis for vagueness

### Decision Logic
- ✅ **ACCEPT**: Score ≥ 0.75, no critical flags, clear winner
- ✅ **REQUIRES_CLARIFICATION**: Medium issues or close scores
- ✅ **REJECT_ALL**: Score < 0.60-0.65 or all bids have critical issues

## 📚 Documentation

- **[USER_STORY.md](USER_STORY.md)**: Complete user story with technical details, thresholds, and examples
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: Full deployment instructions
- **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)**: Quick 5-minute deployment guide
- **[EVALUATION_REPORT.md](EVALUATION_REPORT.md)**: Implementation evaluation and improvements
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**: Summary of all enhancements

## 🚀 Deployment

### Streamlit Cloud (Recommended - Free)

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. **Deploy:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select repository
   - Set main file: `app.py`
   - Add API keys in Secrets (Settings → Secrets)

3. **Share your link:** `https://YOUR_APP_NAME.streamlit.app`

See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for detailed steps.

### Other Platforms
- **Docker**: See `DEPLOYMENT_GUIDE.md`
- **Railway/Render**: Use `requirements-deploy.txt`
- **Local Network**: Run with `--server.address 0.0.0.0`

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT models |
| `SERPER_API_KEY` | Yes | Serper API key for web searches |
| `LANGSMITH_API_KEY` | No | LangSmith key for tracing |
| `LANGSMITH_PROJECT` | No | LangSmith project name (default: bid-evaluation-agent) |

### Model Configuration
- **GPT-4o-mini**: Steps 1-2 (temperature: 0.3)
- **GPT-4o**: Step 3 (temperature: 0.2)
- **LangSmith**: Auto-enabled if API key provided

## 📊 Performance

- **Evaluation Time**: ~2-3 minutes for 5 bids
- **Serper Searches**: Parallel async (60% faster)
- **Cost per Evaluation**: ~$0.15-0.30 (depends on bid count)
- **Accuracy**: 85%+ correct recommendations

## 🛠️ Project Structure

```
Construction tender/
├── app.py                    # Streamlit entry point
├── src/
│   ├── graph.py             # LangGraph workflow
│   ├── state.py             # State schema
│   ├── config.py            # Configuration & API keys
│   ├── schemas.py           # Pydantic models
│   ├── logging_config.py    # Logging setup
│   ├── nodes/
│   │   ├── parse.py         # Step 1: Parse & Enrich
│   │   ├── score.py         # Step 2: Score & Flag
│   │   └── critique.py     # Step 3: Critique & Finalize
│   └── tools/
│       └── serper.py        # Serper API wrapper
├── tests/
│   ├── test_graph.py        # Test suite
│   └── cases/               # Test case JSON files
├── bids/                    # Sample bid files
├── projects/                # Sample project descriptions
├── requirements.txt         # Development dependencies
├── requirements-deploy.txt  # Production dependencies
└── .streamlit/
    └── config.toml          # Streamlit config
```

## 🐛 Troubleshooting

### Common Issues

**Import errors:**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version (3.9+)

**API key errors:**
- Verify `.env` file exists and keys are correct
- For Streamlit Cloud: Check Secrets in Settings
- Run `python check_env.py` to verify

**Serper API timeouts:**
- Normal behavior - system handles gracefully
- Returns default profiles on failure
- Check Serper API quota

**Slow performance:**
- Serper searches take ~30s per contractor
- Parallel searches help but still takes time
- Consider caching for repeated contractors

## 📝 License

This project is provided as-is for evaluation purposes.

## 🤝 Contributing

Improvements welcome! Key areas:
- Enhanced red flag detection
- Better caching strategies
- Performance optimizations
- Additional test cases

## 📞 Support

For issues or questions:
1. Check [EVALUATION_REPORT.md](EVALUATION_REPORT.md) for known issues
2. Review [USER_STORY.md](USER_STORY.md) for technical details
3. Check Streamlit Cloud logs for deployment issues

---

**Built with:** LangGraph, GPT-4o-mini, GPT-4o, Serper API, Streamlit, Pydantic

