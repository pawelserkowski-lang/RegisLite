import os
import time
import logging
import httpx
import asyncio
from typing import Optional, Tuple, Dict, Any

# Konfiguracja loggera - żebyśmy widzieli co się dzieje, a nie zgadywali z fusów
logger = logging.getLogger(__name__)

# Pobieranie konfiguracji wewnątrz funkcji/klasy (unikanie zmiennych globalnych przy imporcie)
def _get_config():
    from src.config.env_config import get_config
    return get_config()

async def _call_gpt_async(messages: list, model: Optional[str] = None, json_mode: bool = False) -> Tuple[str, float, str]:
    """
    Asynchroniczne wywołanie OpenAI API. 
    Nie blokuje Event Loopa, dzięki czemu serwer może obsługiwać inne requesty czekając na AI.
    """
    config = _get_config()
    api_key = config.OPENAI_API_KEY
    
    if not api_key:
        raise ValueError("CRITICAL: Brak klucza OPENAI_API_KEY! Sprawdź zmienne środowiskowe.")

    used_model = model or config.OPENAI_MODEL
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": used_model,
        "messages": messages,
        "temperature": 0.2
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    start_time = time.time()
    
    # Używamy httpx.AsyncClient - to jest ten "Turbo Diesel" zamiast starego silnika parowego requests
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"OpenAI Error {response.status_code}: {response.text}")
                raise Exception(f"OpenAI API Error: {response.status_code}")
                
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            duration = time.time() - start_time
            
            return content, duration, used_model
            
        except httpx.ReadTimeout:
            logger.warning("OpenAI timeout - model myśli wolniej niż polityk przy trudnym pytaniu.")
            return "Error: Timeout", 120.0, used_model
        except Exception as e:
            logger.error(f"Network error: {str(e)}")
            raise

async def classify_intent(user_input: str) -> Tuple[Dict[str, Any], float, str]:
    """Router intencji - decyduje jakiego narzędzia użyć."""
    system_prompt = """
    Jesteś routerem komend dla systemu RegisLite.
    Klasyfikacja intencji użytkownika:
    - "sh": komendy systemowe (git, ls, dir, mkdir, instalacja pakietów)
    - "py": krótki kod python do obliczeń lub testów
    - "file": operacje na plikach (read, write, list)
    - "ai": zwykła rozmowa, pytania o kod
    
    Zwróć TYLKO JSON: {"tool": "...", "args": "..."}
    """
    
    try:
        content, duration, model = await _call_gpt_async(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            model="gpt-4o-mini", # Szybki model do routingu
            json_mode=True
        )
        import json
        return json.loads(content), duration, model
    except Exception as e:
        logger.error(f"Router error: {e}")
        # Fallback
        return {"tool": "ai", "args": user_input}, 0.0, "error-fallback"

async def ask_with_stats(prompt: str) -> Tuple[str, float, str]:
    return await _call_gpt_async([{"role": "user", "content": prompt}])

# Kompatybilność wsteczna
async def ask(prompt: str) -> str:
    content, _, _ = await ask_with_stats(prompt)
    return content