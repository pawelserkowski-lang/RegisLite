import os
import requests
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

async def ask(prompt: str) -> str:
    """
    Klient OpenAI z wydłużonym czasem oczekiwania (120s).
    """
    if not OPENAI_API_KEY:
        return "Brak klucza OPENAI_API_KEY w zmiennych środowiskowych."

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Zabezpieczenie przed zbyt długim promptem
    # Jeśli prompt jest gigantyczny, ucinamy go (chamsko, ale skutecznie)
    if len(prompt) > 100000:
        return "BŁĄD: Prompt jest za duży (>100k znaków). Zmniejsz liczbę plików w projekcie."

    data = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    try:
        # Timeout zwiększony do 120 sekund
        resp = requests.post(url, headers=headers, json=data, timeout=120)
        
        if resp.status_code != 200:
            return f"OpenAI API error: {resp.status_code} {resp.text}"

        j = resp.json()
        return j["choices"][0]["message"]["content"]
        
    except requests.exceptions.Timeout:
        return "OpenAI Timeout: Model myślał za długo (ponad 120s). Spróbuj na mniejszym kawałku kodu."
    except Exception as e:
        return f"Client error: {str(e)}"
