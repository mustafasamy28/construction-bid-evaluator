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

# Store secrets (will be loaded when Streamlit is initialized)
OPENAI_API_KEY = None
SERPER_API_KEY = None
LANGSMITH_API_KEY = None
LANGSMITH_PROJECT = "bid-evaluation-agent"

# Models - will be initialized lazily
_gpt4o_mini = None
_gpt4o = None

def _load_secrets():
    """Load secrets from Streamlit or environment variables."""
    global OPENAI_API_KEY, SERPER_API_KEY, LANGSMITH_API_KEY, LANGSMITH_PROJECT
    OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
    SERPER_API_KEY = get_secret("SERPER_API_KEY")
    LANGSMITH_API_KEY = get_secret("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = get_secret("LANGSMITH_PROJECT", "bid-evaluation-agent")

def _init_langsmith():
    """Initialize LangSmith if API key is available."""
    global LANGSMITH_API_KEY, LANGSMITH_PROJECT
    if LANGSMITH_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"

def get_gpt4o_mini():
    """Get GPT-4o-mini model instance, loading secrets if needed."""
    global _gpt4o_mini, OPENAI_API_KEY
    if _gpt4o_mini is None:
        if OPENAI_API_KEY is None:
            _load_secrets()
            _init_langsmith()  # Initialize LangSmith when we first load secrets
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found!\n\n"
                "Please add it in Streamlit Cloud:\n"
                "1. Go to your app dashboard\n"
                "2. Click 'Settings' → 'Secrets'\n"
                "3. Add:\n"
                "   OPENAI_API_KEY = 'your_key_here'\n"
                "   SERPER_API_KEY = 'your_key_here'\n"
            )
        _gpt4o_mini = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=OPENAI_API_KEY,
        )
    return _gpt4o_mini

def get_gpt4o():
    """Get GPT-4o model instance, loading secrets if needed."""
    global _gpt4o, OPENAI_API_KEY
    if _gpt4o is None:
        if OPENAI_API_KEY is None:
            _load_secrets()
            _init_langsmith()  # Initialize LangSmith when we first load secrets
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found!\n\n"
                "Please add it in Streamlit Cloud:\n"
                "1. Go to your app dashboard\n"
                "2. Click 'Settings' → 'Secrets'\n"
                "3. Add:\n"
                "   OPENAI_API_KEY = 'your_key_here'\n"
                "   SERPER_API_KEY = 'your_key_here'\n"
            )
        _gpt4o = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            api_key=OPENAI_API_KEY,
        )
    return _gpt4o

# Lazy model accessors - work like variables but initialize on first access
class _LazyModel:
    """Lazy model wrapper that initializes on first access."""
    def __init__(self, getter_func):
        self._getter = getter_func
        self._instance = None
    
    def _ensure_initialized(self):
        """Ensure model is initialized."""
        if self._instance is None:
            self._instance = self._getter()
        return self._instance
    
    def __getattr__(self, name):
        # Delegate all attribute access to the actual model
        return getattr(self._ensure_initialized(), name)
    
    def __call__(self, *args, **kwargs):
        # Allow calling the model directly
        return self._ensure_initialized()(*args, **kwargs)

# Create lazy model instances that work transparently
gpt4o_mini = _LazyModel(get_gpt4o_mini)
gpt4o = _LazyModel(get_gpt4o)

# LangSmith - Only enable if API key is provided
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
else:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

