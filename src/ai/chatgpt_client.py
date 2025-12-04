import os
import time
import json
import logging
import httpx
import asyncio
from typing import List, Dict, Tuple, Union, Any
from src.ai.prompts import SYSTEM_PROMPT_CAPABILITIES, ROUTING_PROMPT
from src.config.errors import APIError

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


async def _call_gpt_with_retry(
    messages: List[Dict[str, str]],
    model: str = None,
    json_mode: bool = False,
    retries: int = 3
) -> Tuple[str, float, str]:
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
                    raise APIError(
                        f"OpenAI Error {resp.status_code}", details=resp.text
                    )

                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                duration = time.time() - start_time

                return content, duration, (model or OPENAI_MODEL)

        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            logger.warning(f"Network error (próba {attempt + 1}/{retries}): {e}")
            last_error = e
            await asyncio.sleep(2 ** attempt)

    raise APIError(
        "Nie udało się połączyć z OpenAI po wszystkich próbach.",
        details=str(last_error)
    )


async def classify_intent(user_input: str) -> Tuple[Dict[str, Any], float, str]:
    """Router intencji z optymalizacją regex."""
    # 1. Fast Path (Regex-like checks)
    user_input_stripped = user_input.strip()

    # Shell commands explicitly starting with /sh, $, or common commands
    if user_input_stripped.startswith(("/sh", "$")):
        cmd = user_input_stripped.lstrip("/sh$ ").strip()
        return {"tool": "sh", "args": cmd}, 0.0, "regex"

    if user_input_stripped.startswith("ls ") or user_input_stripped == "ls":
        return {"tool": "sh", "args": user_input_stripped}, 0.0, "regex"

    # Python commands
    if user_input_stripped.startswith("/py"):
        code = user_input_stripped[3:].strip()
        return {"tool": "py", "args": code}, 0.0, "regex"

    # 2. LLM Fallback
    msgs = [
        {"role": "system", "content": ROUTING_PROMPT},
        {"role": "user", "content": user_input}
    ]

    try:
        content, duration, model = await _call_gpt_with_retry(
            msgs, model="gpt-4o-mini", json_mode=True
        )
        return json.loads(content), duration, model
    except APIError:
        # Fallback to AI chat if classification fails
        return {"tool": "ai", "args": user_input}, 0.0, "error-fallback"
    except Exception as e:
        logger.error(f"JSON Parsing or other error in classify_intent: {e}")
        return {"tool": "ai", "args": user_input}, 0.0, "error-fallback"


async def ask_with_stats(
    messages: Union[List[Dict[str, str]], str]
) -> Tuple[str, float, str]:
    """
    Główna funkcja czatu. Obsługuje historię (listę wiadomości).
    """
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    # Ensure system prompt is present
    if not messages or messages[0]["role"] != "system":
        messages.insert(
            0, {"role": "system", "content": SYSTEM_PROMPT_CAPABILITIES}
        )

    return await _call_gpt_with_retry(messages)


# Kompatybilność wsteczna
async def ask(prompt: str) -> str:
    content, _, _ = await ask_with_stats(prompt)
    return content
