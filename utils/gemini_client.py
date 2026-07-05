"""
Gemini API client wrapper.
All agents use this module — never call the Gemini SDK directly from agents.
"""

import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_client_initialized = False


def _init():
    global _client_initialized
    if not _client_initialized:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable is not set. "
                "Set it in GitHub Secrets (for Actions) or in your .env file (local dev)."
            )
        genai.configure(api_key=api_key)
        _client_initialized = True


def ask(prompt: str, system_instruction: str = "", model: str = "gemini-1.5-pro") -> str:
    """
    Send a prompt to Gemini and return the response text.

    Args:
        prompt: The user-facing prompt content.
        system_instruction: Optional system-level instruction for the model role.
        model: Gemini model name. Defaults to gemini-1.5-pro.

    Returns:
        The model's response as a plain string.
    """
    _init()

    generation_config = genai.GenerationConfig(
        temperature=0.3,  # Low temperature for structured, consistent outputs
        response_mime_type="application/json",
    )

    gemini_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system_instruction if system_instruction else None,
        generation_config=generation_config,
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            # Retry on rate limit errors
            if "429" in error_str or "Resource exhausted" in error_str.lower():
                wait = 2 ** attempt * 5  # 5s, 10s, 20s
                print(f"[gemini_client] Rate limit hit. Retrying in {wait}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                if attempt == max_retries - 1:
                    raise
            else:
                raise

    raise RuntimeError("Gemini API call failed after maximum retries.")
