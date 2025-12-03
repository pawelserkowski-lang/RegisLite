import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


async def ask(prompt: str) -> str:
    """
    Bardzo prosty klient HTTP do OpenAI Chat Completions.
    Uwaga: funkcja jest async, ale wywołuje requests synchronicznie –
    dla prostoty działania w tym projekcie.
    """
    if not OPENAI_API_KEY:
        return "Brak klucza OPENAI_API_KEY w zmiennych środowiskowych."

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "model": "gpt-4.1",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    resp = requests.post(url, headers=headers, json=data, timeout=60)
    if resp.status_code != 200:
        return f"OpenAI API error: {resp.status_code} {resp.text}"

    j = resp.json()
    try:
        return j["choices"][0]["message"]["content"]
    except Exception:
        return str(j)
