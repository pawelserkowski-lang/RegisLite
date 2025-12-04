import os
import time
import json
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def _call_gpt(messages, model=None, json_mode=False):
    """Pomocnicza funkcja do wołania API"""
    if not OPENAI_API_KEY:
        raise Exception("Brak klucza API!")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model or OPENAI_MODEL,
        "messages": messages
    }
    
    if json_mode:
        data["response_format"] = {"type": "json_object"}

    start_time = time.time()
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    duration = time.time() - start_time
    
    if resp.status_code != 200:
        raise Exception(f"OpenAI Error {resp.status_code}: {resp.text}")

    content = resp.json()["choices"][0]["message"]["content"]
    return content, duration, (model or OPENAI_MODEL)

async def classify_intent(user_input: str):
    """
    Analizuje co użytkownik miał na myśli.
    Zwraca JSON: { "tool": "sh"|"py"|"ai"|"file", "args": "..." }
    """
    system_prompt = """
    Jesteś routerem komend dla systemu RegisLite.
    Twoim zadaniem jest klasyfikacja intencji użytkownika na jedną z kategorii:
    - "sh": komendy systemowe (git, ls, dir, mkdir, instalacja pakietów)
    - "py": krótki kod python do obliczeń lub testów
    - "file": operacje na plikach (czytanie, zapisywanie)
    - "ai": zwykła rozmowa, pytania o kod, prośby o wyjaśnienie
    
    Zwróć TYLKO JSON w formacie: {"tool": "...", "args": "..."}.
    Przykład: "pokaż pliki" -> {"tool": "sh", "args": "dir"}
    Przykład: "policz 2+2" -> {"tool": "py", "args": "print(2+2)"}
    """
    
    try:
        content, duration, model = _call_gpt(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            model="gpt-4o-mini", # Używamy szybkiego modelu do routingu
            json_mode=True
        )
        return json.loads(content), duration, model
    except Exception as e:
        # Fallback do zwykłego AI
        return {"tool": "ai", "args": user_input}, 0.0, "error-fallback"

async def ask_with_stats(prompt: str):
    """Zwykłe zapytanie, ale zwraca też metadane"""
    content, duration, model = _call_gpt([{"role": "user", "content": prompt}])
    return content, duration, model

# Kompatybilność wsteczna dla starych modułów
async def ask(prompt: str) -> str:
    c, _, _ = await ask_with_stats(prompt)
    return c
