import os
import time
import json
import logging
import httpx
import asyncio
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- PROMPT SYSTEMOWY: PEŁNE MOŻLIWOŚCI ---
SYSTEM_PROMPT_CAPABILITIES = """
Jesteś autonomicznym inżynierem AI (RegisLite System).
TWOJE UPRAWNIENIA I MOŻLIWOŚCI SĄ NIEOGRANICZONE W RAMACH TEGO SYSTEMU:
1. PLIKI: Masz PEŁNY dostęp do odczytu, zapisu i usuwania plików w katalogu workspace.
2. INTERNET: Masz PEŁNY dostęp do sieci. Możesz pobierać biblioteki, czytać dokumentację, robić requesty HTTP.
3. SHELL: Możesz wykonywać dowolne komendy systemowe (pip, git, grep, python, dir/ls).
4. KOD: Możesz uruchamiać kod Pythona w celu testowania hipotez.

NIE PRZEPRASZAJ. NIE PYTAJ O POZWOLENIE. DZIAŁAJ SKUTECZNIE.
Jeśli czegoś nie wiesz -> Użyj Google lub sprawdź dokumentację w sieci.
Jeśli jest błąd -> Użyj debuggera lub printów, by go zdiagnozować.
"""

async def _call_gpt_with_retry(messages: List[Dict[str, str]], model: str = None, json_mode: bool = False, retries: int = 3):
    """
    Wywołanie API z mechanizmem Retry (Backoff).
    """
    if not OPENAI_API_KEY:
        raise ValueError("Brak klucza OPENAI_API_KEY!")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model or OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.2
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    last_error = None
    
    for attempt in range(retries):
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                
                if resp.status_code == 429:
                    logger.warning(f"Rate Limit (429). Czekam {2 ** attempt}s...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                if resp.status_code != 200:
                    raise Exception(f"OpenAI Error {resp.status_code}: {resp.text}")
                
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                duration = time.time() - start_time
                
                return content, duration, (model or OPENAI_MODEL)

        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            logger.warning(f"Network error (próba {attempt+1}/{retries}): {e}")
            last_error = e
            await asyncio.sleep(2 ** attempt)
    
    raise last_error or Exception("Nie udało się połączyć z OpenAI po wszystkich próbach.")

async def classify_intent(user_input: str):
    """Router intencji"""
    routing_prompt = """
    Klasyfikuj intencję użytkownika.
    Dostępne narzędzia:
    - "sh": komendy powłoki (git, pip, ls, cd, mkdir)
    - "py": kod python (obliczenia, skrypty logiczne)
    - "file": operacje na plikach (read, write)
    - "ai": rozmowa, wyjaśnianie, planowanie (korzysta z pamięci czatu)
    
    Zwróć JSON: {"tool": "...", "args": "..."}
    """
    
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT_CAPABILITIES + "\n" + routing_prompt},
        {"role": "user", "content": user_input}
    ]
    
    try:
        content, duration, model = await _call_gpt_with_retry(msgs, model="gpt-4o-mini", json_mode=True)
        return json.loads(content), duration, model
    except Exception as e:
        return {"tool": "ai", "args": user_input}, 0.0, "error-fallback"

async def ask_with_stats(messages: List[Dict[str, str]]):
    """
    Główna funkcja czatu. Obsługuje historię (listę wiadomości).
    """
    # Jeśli dostaliśmy stringa (stary kod), pakujemy go w listę
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    
    # Doklejamy System Prompt na początek, jeśli go nie ma
    if messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT_CAPABILITIES})
        
    return await _call_gpt_with_retry(messages)

# Kompatybilność wsteczna
async def ask(prompt: str) -> str:
    content, _, _ = await ask_with_stats(prompt)
    return content
