"""
Gemini API client wrapper.
Uses the new google-genai SDK (replaces deprecated google-generativeai).
All agents use this module — never call the Gemini SDK directly from agents.
"""

import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable is not set. "
                "Set it in GitHub Secrets (for Actions) or in your .env file (local dev)."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def ask(prompt: str, system_instruction: str = "", model: str = "gemini-2.0-flash") -> str:
    """
    Send a prompt to Gemini and return the response text.

    Args:
        prompt: The user-facing prompt content.
        system_instruction: Optional system-level instruction for the model role.
        model: Gemini model name. Defaults to gemini-2.0-flash.

    Returns:
        The model's response as a plain string.
    """
    client = _get_client()

    config = types.GenerateContentConfig(
        temperature=0.3,
        response_mime_type="application/json",
        system_instruction=system_instruction if system_instruction else None,
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "resource exhausted" in error_str.lower():
                wait = 2 ** attempt * 5  # 5s, 10s, 20s
                print(f"[gemini_client] Rate limit hit. Retrying in {wait}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                if attempt == max_retries - 1:
                    raise
            else:
                raise

    raise RuntimeError("Gemini API call failed after maximum retries.")
