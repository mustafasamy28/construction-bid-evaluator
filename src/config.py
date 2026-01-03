import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
# Try Streamlit secrets first (for Streamlit Cloud), then .env file
def get_secret(key: str, default: str = None):
    """Get secret from Streamlit secrets or environment variable."""
    try:
        import streamlit as st
        return st.secrets.get(key) or os.getenv(key, default)
    except (AttributeError, FileNotFoundError, RuntimeError):
        # Not in Streamlit context or secrets not available
        load_dotenv()
        return os.getenv(key, default)

OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
SERPER_API_KEY = get_secret("SERPER_API_KEY")
LANGSMITH_API_KEY = get_secret("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = get_secret("LANGSMITH_PROJECT", "bid-evaluation-agent")

# Models
gpt4o_mini = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=OPENAI_API_KEY,
)

gpt4o = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    api_key=OPENAI_API_KEY,
)

# LangSmith - Only enable if API key is provided
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
else:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

