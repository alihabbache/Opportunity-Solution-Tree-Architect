"""
LLM API client wrapper — powered by Groq.
Uses the groq SDK for fast, free-tier inference via Llama 3.3 70B.
All agents use this module — never call the LLM SDK directly from agents.
"""

import os
import time
from groq import Groq, RateLimitError
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY environment variable is not set. "
                "Set it in GitHub Secrets (for Actions) or in your .env file (local dev). "
                "Get a free key at https://console.groq.com"
            )
        _client = Groq(api_key=api_key)
    return _client


def ask(prompt: str, system_instruction: str = "", model: str = "llama-3.3-70b-versatile") -> str:
    """
    Send a prompt to Groq and return the response text.

    Args:
        prompt: The user-facing prompt content.
        system_instruction: Optional system-level instruction for the model role.
        model: Groq model name. Defaults to llama-3.3-70b-versatile.

    Returns:
        The model's response as a plain string.
    """
    client = _get_client()

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            wait = 2 ** attempt * 15  # 15s, 30s, 60s
            print(f"[groq_client] Rate limit hit. Retrying in {wait}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)
            if attempt == max_retries - 1:
                raise
        except Exception as e:
            raise

    raise RuntimeError("Groq API call failed after maximum retries.")
