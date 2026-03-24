"""LLM client — Multi-model integration (Gemini and Groq)."""

import time
import httpx
import google.generativeai as genai
from app.config import get_settings


_configured = False


def _ensure_configured() -> None:
    """Configure API keys for litellm."""
    global _configured
    if not _configured:
        settings = get_settings()
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
        _configured = True


def _generate_gemini(model_id: str, system_prompt: str, user_prompt: str) -> str:
    """Generate using Google Gemini."""
    model = genai.GenerativeModel(
        model_name=model_id,
        system_instruction=system_prompt,
    )
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(user_prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise e
    return ""


def _generate_groq(model_id: str, system_prompt: str, user_prompt: str) -> str:
    """Generate using Groq HTTP API."""
    settings = get_settings()
    api_key = settings.groq_api_key
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is not set. Please get a free key at https://console.groq.com/keys")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def generate(system_prompt: str, user_prompt: str, model_name: str | None = None) -> str:
    """Generate a response using the appropriate provider.

    Args:
        system_prompt: System-level instructions.
        user_prompt: User message with context and question.
        model_name: The LiteLLM model string to use. Defaults to chat_model.

    Returns:
        The model's text response.
    """
    _ensure_configured()
    settings = get_settings()
    actual_model = model_name or settings.chat_model

    if actual_model.startswith("groq/"):
        model_id = actual_model.split("groq/")[1]
        return _generate_groq(model_id, system_prompt, user_prompt)
    elif actual_model.startswith("gemini/"):
        model_id = actual_model.split("gemini/")[1]
        return _generate_gemini(model_id, system_prompt, user_prompt)
    else:
        # Fallback to gemini directly
        return _generate_gemini(actual_model, system_prompt, user_prompt)
