"""Check if .env file has all required API keys."""
import os
from dotenv import load_dotenv

load_dotenv()

required_keys = {
    "OPENAI_API_KEY": "Required - Used for GPT-4o-mini and GPT-4o models",
    "SERPER_API_KEY": "Required - Used for contractor web searches",
    "LANGSMITH_API_KEY": "Optional - Used for tracing and monitoring",
    "LANGSMITH_PROJECT": "Optional - LangSmith project name (defaults to 'bid-evaluation-agent')",
}

print("Checking .env file for required API keys...\n")

missing_required = []
missing_optional = []
present = []

for key, description in required_keys.items():
    value = os.getenv(key)
    if value:
        # Check if it's a placeholder or empty
        if value.strip() and not value.startswith("your_") and len(value) > 10:
            present.append((key, description))
            print(f"[OK] {key}: Present")
        else:
            if key in ["OPENAI_API_KEY", "SERPER_API_KEY"]:
                missing_required.append((key, description))
                print(f"[MISSING] {key}: {description}")
            else:
                missing_optional.append((key, description))
                print(f"[OPTIONAL] {key}: Not set or placeholder")
    else:
        if key in ["OPENAI_API_KEY", "SERPER_API_KEY"]:
            missing_required.append((key, description))
            print(f"[MISSING] {key}: {description}")
        else:
            missing_optional.append((key, description))
            print(f"[OPTIONAL] {key}: Not set")

print("\n" + "="*60)
if missing_required:
    print("\n[ERROR] Missing REQUIRED API keys:")
    for key, desc in missing_required:
        print(f"  - {key}: {desc}")
    print("\nThe application will NOT work without these keys.")
else:
    print("\n[SUCCESS] All REQUIRED API keys are present!")

if missing_optional:
    print("\n[INFO] Optional keys not set:")
    for key, desc in missing_optional:
        print(f"  - {key}: {desc}")
    print("\nThe application will work without these, but:")
    print("  - Without LANGSMITH_API_KEY: No tracing/monitoring")
    print("  - Without LANGSMITH_PROJECT: Uses default project name")

print("\n" + "="*60)
print("\nLangSmith Setup Info:")
print("  - LANGSMITH_API_KEY: Get from https://smith.langchain.com/")
print("  - LANGSMITH_PROJECT: Optional, defaults to 'bid-evaluation-agent'")
print("  - LangSmith is used for:")
print("    * Tracing LLM calls")
print("    * Monitoring performance")
print("    * Debugging issues")
print("    * Viewing detailed execution logs")
print("\n  If you don't have LangSmith, you can:")
print("    1. Sign up at https://smith.langchain.com/ (free tier available)")
print("    2. Or remove/comment out LangSmith config in src/config.py")

