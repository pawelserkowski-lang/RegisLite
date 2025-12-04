Write-Host "=== Regis INTELLECT UPDATE ===" -ForegroundColor Cyan
Set-Location (Split-Path $MyInvocation.MyCommand.Path)

# 1. MĄDRZEJSZY SKANER (Ignoruje śmieci)
$analyzerCode = @'
import os
from typing import List, Dict

def scan_project(base_path: str) -> List[Dict[str, str]]:
    """
    Skanuje projekt, ale OMIJA foldery systemowe i biblioteki.
    """
    result = []
    
    # Lista folderów do ignorowania (czarna lista)
    IGNORE_DIRS = {
        "node_modules", "venv", ".venv", ".git", "__pycache__", 
        "dist", "build", "coverage", ".idea", ".vscode"
    }
    
    # Lista rozszerzeń do ignorowania (binarki, mapy, obrazki)
    IGNORE_EXT = {
        ".map", ".png", ".jpg", ".jpeg", ".gif", ".ico", 
        ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin",
        ".lock", ".json", ".zip", ".tar", ".gz" 
    }

    if not os.path.exists(base_path):
        return result

    for root, dirs, files in os.walk(base_path):
        # 1. Modyfikujemy 'dirs' in-place, żeby os.walk nie wchodził w śmieci
        # (to jest kluczowe dla wydajności!)
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for name in files:
            # 2. Ignorujemy pliki po rozszerzeniu
            _, ext = os.path.splitext(name)
            if ext.lower() in IGNORE_EXT:
                continue

            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, base_path)
            
            try:
                # Limit wielkości pojedynczego pliku (np. max 100KB), żeby nie zatkać AI
                if os.path.getsize(full_path) > 100 * 1024:
                    continue

                with open(full_path, "r", encoding="utf8") as f:
                    content = f.read()
                    result.append({"path": rel_path, "content": content})
            except Exception:
                # Ignorujemy pliki, których nie da się przeczytać (np. binarne)
                pass

    return result
'@
$analyzerCode | Set-Content "debugger/debugger_analyzer.py" -Encoding UTF8
Write-Host "[1/2] debugger_analyzer.py naprawiony (ignoruje node_modules)" -ForegroundColor Green


# 2. CIERPLIWSZY KLIENT (Większy timeout)
$clientCode = @'
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
'@
$clientCode | Set-Content "ai/chatgpt_client.py" -Encoding UTF8
Write-Host "[2/2] ai/chatgpt_client.py naprawiony (timeout 120s + obsługa błędów)" -ForegroundColor Green

Write-Host "`n✅ GOTOWE! Teraz zrestartuj serwer i spróbuj ponownie." -ForegroundColor Yellow