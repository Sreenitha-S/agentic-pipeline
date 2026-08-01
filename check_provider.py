"""
Zero-cost sanity check: shows which LLM provider get_llm() will select, WITHOUT making any
actual API call. Run this before eval/run_eval.py or main.py if you're not sure which provider
is active, or if you've just changed environment variables / API keys and want to confirm
before spending any quota.

Usage:
    python check_provider.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from llm_client import get_llm  # noqa: E402

print("Environment variables detected:")
for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY", "HF_TOKEN", "LLM_PROVIDER"):
    val = os.environ.get(key)
    if val and key != "LLM_PROVIDER":
        print(f"  {key} = set ({val[:8]}... , {len(val)} chars)")
    elif val:
        print(f"  {key} = {val}")
    else:
        print(f"  {key} = (not set)")

print()
llm = get_llm()
print(f"get_llm() will use: {type(llm).__name__}")
if type(llm).__name__ == "MockLLM":
    print("-> No real API calls will be made. Set an API key (see README) to use a real model.")
else:
    print("-> This provider will be used for main.py and eval/run_eval.py. No API call made yet.")
