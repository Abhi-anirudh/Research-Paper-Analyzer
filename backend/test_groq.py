import os
from app.config import get_settings
import httpx

settings = get_settings()
api_key = settings.groq_api_key
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
payload = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "system", "content": "You are a bot."},
        {"role": "user", "content": "Hello"}
    ]
}

try:
    with httpx.Client() as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        print("Success:", r.json())
except httpx.HTTPStatusError as e:
    print("Error status:", e.response.status_code)
    print("Error text:", e.response.text)
except Exception as e:
    print("Other error:", e)
