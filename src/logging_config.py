"""Logging configuration for the bid evaluation agent."""
import logging
import sys
from pathlib import Path

# Try to create logs directory, but handle errors gracefully (e.g., in Streamlit Cloud)
LOG_DIR = Path(__file__).parent.parent / "logs"
try:
    LOG_DIR.mkdir(exist_ok=True)
    # Try to create file handler
    file_handler = logging.FileHandler(LOG_DIR / "bid_evaluation.log")
    handlers = [file_handler, logging.StreamHandler(sys.stdout)]
except (PermissionError, OSError, Exception):
    # If we can't create logs directory (e.g., in Streamlit Cloud), use console only
    handlers = [logging.StreamHandler(sys.stdout)]

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

# Set specific log levels for external libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("langchain").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)

