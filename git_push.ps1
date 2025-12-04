# ══════════════════════════════════════════════════════════════════════════════
#     🚀 REGISLITE ULTIMATE GIT PUSH SCRIPT 🚀
#     Wersja: 4.5-PATCHED (Config Module Edition)
#     Data: 04.12.2025 23:37
#     Autor: pawelserkowski-lang
#     Motto: "Kod piszemy z sercem, pierogi jemy z masłem!" 🥟
# ══════════════════════════════════════════════════════════════════════════════

param(
    [string]$CommitMessage = "",
    [switch]$SkipTests = $false
)

Clear-Host
Write-Host "`n`n" -NoNewline

# ══════════════════════════════════════════════════════════════════════════════
# ASCII ART INTRO
# ══════════════════════════════════════════════════════════════════════════════

Write-Host "  ██████╗ ███████╗ ██████╗ ██╗███████╗██╗     ██╗████████╗███████╗" -ForegroundColor Cyan
Write-Host "  ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝██║     ██║╚══██╔══╝██╔════╝" -ForegroundColor Cyan
Write-Host "  ██████╔╝█████╗  ██║  ███╗██║███████╗██║     ██║   ██║   █████╗  " -ForegroundColor Cyan
Write-Host "  ██╔══██╗██╔══╝  ██║   ██║██║╚════██║██║     ██║   ██║   ██╔══╝  " -ForegroundColor Cyan
Write-Host "  ██║  ██║███████╗╚██████╔╝██║███████║███████╗██║   ██║   ███████╗" -ForegroundColor Cyan
Write-Host "  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝   ╚═╝   ╚══════╝" -ForegroundColor Cyan
Write-Host "`n          🚀 ULTIMATE GIT PUSH - EDITION 4.5 PATCHED 🚀" -ForegroundColor Magenta
Write-Host "          📅 $(Get-Date -Format 'dd.MM.yyyy HH:mm:ss')" -ForegroundColor Yellow
Write-Host "          🥟 Przygotuj pierogi - lecą zmiany! 🥟`n" -ForegroundColor Green

Set-Location (Split-Path $MyInvocation.MyCommand.Path)

$startTime = Get-Date

# ══════════════════════════════════════════════════════════════════════════════
# KROK 1: Tworzenie struktury folderów
# ══════════════════════════════════════════════════════════════════════════════

Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  [1/9] 📁 TWORZENIE STRUKTURY FOLDERÓW..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

$folders = @(
    "ai",
    "debugger", 
    "rtc",
    "services",
    "static",
    "config",
    "workspace",
    "workspace/backups",
    "docs"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
    Write-Host "  ✓ $folder" -ForegroundColor Green
}

Write-Host "`n  🎉 Wszystkie foldery gotowe!`n" -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# KROK 2: Zapisywanie plików - CONFIG MODULE
# ══════════════════════════════════════════════════════════════════════════════

Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  [2/9] 🔧 ZAPISYWANIE CONFIG MODULE..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

# config/__init__.py
@'
"""RegisLite Configuration Package"""
from .env_config import get_config, Config, get_api_key

__all__ = ['get_config', 'Config', 'get_api_key']
'@ | Out-File -Encoding utf8 "config/__init__.py"
Write-Host "  ✓ config/__init__.py" -ForegroundColor Green

# config/env_config.py - PEŁNA WERSJA
@'
# config/env_config.py
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    REGISLITE ENVIRONMENT CONFIGURATION                       ║
║                                                                              ║
║  ZASADA NADRZĘDNA: WSZYSTKIE KLUCZE API ZAWSZE Z WINDOWS ENV VARS!         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=False)
    logger.info(f"✓ Załadowano .env z: {ENV_FILE}")

def get_api_key(key_name: str, required: bool = True, default: Optional[str] = None, description: str = "") -> Optional[str]:
    value = os.environ.get(key_name)
    if value:
        logger.info(f"✓ [{key_name}] załadowany z: Windows ENV")
        return value
    value = os.getenv(key_name)
    if value:
        logger.info(f"✓ [{key_name}] załadowany z: .env file")
        return value
    if default is not None:
        logger.warning(f"⚠ [{key_name}] używam wartości domyślnej")
        return default
    if required:
        error_msg = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         BRAK WYMAGANEGO KLUCZA API!                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
Klucz: {key_name}
{f'Opis: {description}' if description else ''}
Ustaw w Windows ENV: setx {key_name} "twoj-klucz" /M
"""
        logger.error(error_msg)
        raise ValueError(f"Brak wymaganego klucza: {key_name}")
    logger.warning(f"⚠ [{key_name}] brak wartości (opcjonalny klucz)")
    return None

class Config:
    def __init__(self):
        logger.info("=" * 80)
        logger.info("🔧 REGISLITE CONFIG - Ładowanie konfiguracji...")
        logger.info("=" * 80)
        self.OPENAI_API_KEY = get_api_key("OPENAI_API_KEY", required=True, description="Klucz do OpenAI API")
        self.ANTHROPIC_API_KEY = get_api_key("ANTHROPIC_API_KEY", required=False)
        self.GITHUB_TOKEN = get_api_key("GITHUB_TOKEN", required=False)
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
        self.MAX_ZIP_SIZE_MB = int(os.getenv("MAX_ZIP_SIZE_MB", "50"))
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.SHELL_TIMEOUT = int(os.getenv("SHELL_TIMEOUT", "30"))
        self.WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "workspace"))
        self.BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "workspace/backups"))
        self.WORKSPACE_DIR.mkdir(exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("=" * 80)
        logger.info("✅ Konfiguracja załadowana pomyślnie!")
        logger.info("=" * 80)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_openai_key": bool(self.OPENAI_API_KEY),
            "has_anthropic_key": bool(self.ANTHROPIC_API_KEY),
            "has_github_token": bool(self.GITHUB_TOKEN),
            "debug": self.DEBUG,
            "max_iterations": self.MAX_ITERATIONS,
            "max_zip_size_mb": self.MAX_ZIP_SIZE_MB,
            "openai_model": self.OPENAI_MODEL,
        }
    
    def validate(self) -> bool:
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY jest wymagany!")
        logger.info("✅ Walidacja konfiguracji: OK")
        return True

_config_instance: Optional[Config] = None

def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
'@ | Out-File -Encoding utf8 "config/env_config.py"
Write-Host "  ✓ config/env_config.py" -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# KROK 3: AI MODULE
# ══════════════════════════════════════════════════════════════════════════════

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  [3/9] 🤖 ZAPISYWANIE AI MODULE..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

# ai/__init__.py
@'
# ai package marker
'@ | Out-File -Encoding utf8 "ai/__init__.py"
Write-Host "  ✓ ai/__init__.py" -ForegroundColor Green

# ai/chatgpt_client.py - PATCHED VERSION
@'
# ai/chatgpt_client.py
import requests
import logging
from typing import Optional
from config.env_config import get_config

logger = logging.getLogger(__name__)
config = get_config()

async def ask(prompt: str, model: Optional[str] = None) -> str:
    api_key = config.OPENAI_API_KEY
    if not api_key:
        raise ValueError("Brak OPENAI_API_KEY w Windows Environment Variables!")
    model = model or config.OPENAI_MODEL
    logger.info(f"🤖 Wysyłam zapytanie do OpenAI ({model})...")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2, "max_tokens": 2000}
    try:
        timeout = getattr(config, 'OPENAI_TIMEOUT', 60)
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        if response.status_code != 200:
            error_detail = response.text[:200]
            logger.error(f"❌ OpenAI API Error [{response.status_code}]: {error_detail}")
            if response.status_code == 401:
                return "❌ BŁĄD: Nieprawidłowy klucz API!"
            elif response.status_code == 429:
                return "❌ BŁĄD: Rate limit exceeded!"
            else:
                return f"❌ BŁĄD OpenAI API: {response.status_code}"
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        logger.info(f"✅ Otrzymano odpowiedź ({len(content)} znaków)")
        return content.strip()
    except requests.Timeout:
        return f"❌ BŁĄD: Timeout - OpenAI nie odpowiedział"
    except Exception as e:
        logger.error(f"❌ Błąd: {e}", exc_info=True)
        return f"❌ BŁĄD: {str(e)}"
'@ | Out-File -Encoding utf8 "ai/chatgpt_client.py"
Write-Host "  ✓ ai/chatgpt_client.py (PATCHED)" -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# KROK 4: DEBUGGER MODULE
# ══════════════════════════════════════════════════════════════════════════════

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  [4/9] 🐛 ZAPISYWANIE DEBUGGER MODULE..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

# debugger/__init__.py
@'
# debugger package marker
'@ | Out-File -Encoding utf8 "debugger/__init__.py"
Write-Host "  ✓ debugger/__init__.py" -ForegroundColor Green

# debugger/debugger_analyzer.py
@'
# debugger/debugger_analyzer.py
import os
from typing import List, Dict

def scan_project() -> List[Dict[str, str]]:
    base = "workspace/project"
    result = []
    if not os.path.exists(base):
        return result
    for root, _, files in os.walk(base):
        for name in files:
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf8") as f:
                    content = f.read()
            except Exception:
                content = ""
            result.append({"path": path, "content": content})
    return result
'@ | Out-File -Encoding utf8 "debugger/debugger_analyzer.py"
Write-Host "  ✓ debugger/debugger_analyzer.py" -ForegroundColor Green

# debugger/debugger_fix.py
@'
# debugger/debugger_fix.py
import traceback
from typing import Dict, List
from ai.chatgpt_client import ask

PATCH_INSTRUCTIONS = """
Jesteś asystentem AI naprawiającym kod.
Zwróć poprawki TYLKO w następującym formacie:
FILE: <ścieżka_pliku>
```python
<pełna poprawiona treść>
```
END_FILE

Plan: najpierw wypisz plan w 1-3 punktach, potem patch.
"""

def _format_files(files: List[Dict[str, str]]) -> str:
    formatted = []
    for f in files:
        formatted.append(f"FILE: {f['path']}")
        formatted.append("```")
        formatted.append(f.get("content", ""))
        formatted.append("```")
    return "\n".join(formatted)

async def generate_patches(errors: str, files: List[Dict[str, str]]) -> str:
    prompt = f"{PATCH_INSTRUCTIONS}\n\nBłędy: {errors}\n\nPliki:\n{_format_files(files)}"
    try:
        return await ask(prompt)
    except Exception:
        return f"LLM error: {traceback.format_exc()}"
'@ | Out-File -Encoding utf8 "debugger/debugger_fix.py"
Write-Host "  ✓ debugger/debugger_fix.py" -ForegroundColor Green

# debugger/debugger_patcher.py
@'
# debugger/debugger_patcher.py
import os
import shutil
from typing import List

def apply_patches(patch_text: str) -> List[str]:
    if not patch_text:
        return []
    lines = patch_text.splitlines()
    current_file = None
    buffer = []
    in_code = False
    modified_files: List[str] = []
    for line in lines:
        if line.startswith("FILE:"):
            if current_file and buffer:
                _write_file(current_file, "\n".join(buffer))
                modified_files.append(current_file)
                buffer = []
            current_file = line[len("FILE:"):].strip()
            in_code = False
            continue
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if line.strip() == "END_FILE":
            if current_file and buffer:
                _write_file(current_file, "\n".join(buffer))
                modified_files.append(current_file)
            current_file = None
            buffer = []
            in_code = False
            continue
        if in_code and current_file:
            buffer.append(line)
    if current_file and buffer:
        _write_file(current_file, "\n".join(buffer))
        modified_files.append(current_file)
    return modified_files

def _write_file(relative_path: str, content: str) -> None:
    base = "workspace/project"
    if relative_path.startswith(base):
        full_path = relative_path
    else:
        full_path = os.path.join(base, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    if os.path.exists(full_path):
        backup_path = full_path + ".bak"
        shutil.copy(full_path, backup_path)
    with open(full_path, "w", encoding="utf8") as f:
        f.write(content)
'@ | Out-File -Encoding utf8 "debugger/debugger_patcher.py"
Write-Host "  ✓ debugger/debugger_patcher.py" -ForegroundColor Green

# debugger/debugger_loop.py
@'
# debugger/debugger_loop.py
import os
import shutil
from typing import List, Dict, Any
from .debugger_analyzer import scan_project
from .debugger_fix import generate_patches
from .debugger_patcher import apply_patches

async def start_debug_loop(session_id: str, max_iterations: int = 10) -> Dict[str, Any]:
    workspace = f"workspace/{session_id}"
    project_path = f"{workspace}/project"
    if not os.path.exists(project_path):
        return {"status": "error", "message": f"Projekt nie istnieje: {project_path}", "logs": []}
    logs: List[str] = []
    total_errors_found = 0
    total_files_fixed = 0
    logs.append("=" * 60)
    logs.append("🚀 REGISLITE DEBUGGER 4.5 - START")
    logs.append("=" * 60)
    logs.append(f"Session ID: {session_id}")
    logs.append(f"Max iterations: {max_iterations}")
    logs.append("")
    for iteration in range(1, max_iterations + 1):
        logs.append(f"\n{'='*60}")
        logs.append(f"🔄 ITERACJA {iteration}/{max_iterations}")
        logs.append(f"{'='*60}")
        logs.append("📂 Skanuję projekt...")
        files = scan_project()
        if not files:
            logs.append("⚠️  Brak plików do analizy!")
            break
        logs.append(f"✅ Znaleziono {len(files)} plików")
        files_with_errors = []
        for f in files:
            content = f.get("content", "")
            if "FIXME" in content or "TODO:" in content or "BUG:" in content:
                files_with_errors.append(f)
        if not files_with_errors:
            logs.append("✨ Brak błędów - kod jest czysty!")
            logs.append("🎉 Projekt naprawiony!")
            break
        total_errors_found += len(files_with_errors)
        logs.append(f"🐛 Znaleziono {len(files_with_errors)} plików z błędami")
        logs.append("\n🤖 Generuję patche przez GPT...")
        error_summary = f"Znaleziono {len(files_with_errors)} plików z FIXME/TODO/BUG"
        try:
            patches_text = await generate_patches(error_summary, files_with_errors)
            if not patches_text or "error" in patches_text.lower()[:50]:
                logs.append(f"⚠️  GPT zwrócił błąd")
                continue
            logs.append(f"✅ Otrzymano patche")
        except Exception as e:
            logs.append(f"❌ BŁĄD GPT: {str(e)}")
            continue
        logs.append("\n✂️  Aplikuję patche...")
        try:
            modified_files = apply_patches(patches_text)
            if not modified_files:
                logs.append("⚠️  Brak plików do modyfikacji")
                continue
            total_files_fixed += len(modified_files)
            logs.append(f"✅ Zmodyfikowano {len(modified_files)} plików")
        except Exception as e:
            logs.append(f"❌ BŁĄD PATCHING: {str(e)}")
            continue
    logs.append(f"\n{'='*60}")
    logs.append("🏁 DEBUGOWANIE ZAKOŃCZONE")
    logs.append(f"{'='*60}")
    logs.append(f"📊 Statystyki:")
    logs.append(f"   - Iteracji: {iteration}")
    logs.append(f"   - Błędów znalezionych: {total_errors_found}")
    logs.append(f"   - Plików naprawionych: {total_files_fixed}")
    output_path = f"{workspace}/output_fixed"
    try:
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        shutil.copytree(project_path, output_path)
        logs.append(f"\n✅ Naprawiony projekt: {output_path}")
    except Exception as e:
        logs.append(f"\n⚠️  Nie udało się skopiować: {e}")
    logs.append("\n🥟 Gotowe! Czas na pierogi! 🥟\n")
    return {"status": "success", "logs": logs, "iterations": iteration, "errors_found": total_errors_found, "files_fixed": total_files_fixed}
'@ | Out-File -Encoding utf8 "debugger/debugger_loop.py"
Write-Host "  ✓ debugger/debugger_loop.py" -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# KROK 5: RTC MODULE
# ══════════════════════════════════════════════════════════════════════════════

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  [5/9] 💬 ZAPISYWANIE RTC MODULE..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

# rtc/__init__.py
@'
# rtc package marker
'@ | Out-File -Encoding utf8 "rtc/__init__.py"
Write-Host "  ✓ rtc/__init__.py" -ForegroundColor Green

# rtc/signaling.py
@'
# rtc/signaling.py
import asyncio
from services.python_tool import exec_python
from services.file_tool import file_crud
import subprocess
from ai.chatgpt_client import ask

async def handle_command(cmd: str, session_id: str):
    if cmd.startswith("ai:"):
        prompt = cmd[3:].strip()
        response = await ask(prompt)
        return f"AI: {response}"
    elif cmd.startswith("py:"):
        code = cmd[3:].strip()
        result = await exec_python(code)
        return f"Python: {result}"
    elif cmd.startswith("sh:"):
        shell_cmd = cmd[3:].strip()
        try:
            result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, timeout=30)
            return f"Shell: {result.stdout or result.stderr}"
        except subprocess.TimeoutExpired:
            return "Shell: [ERROR] Timeout"
        except Exception as e:
            return f"Shell: [ERROR] {str(e)}"
    elif cmd.startswith("file:"):
        parts = cmd[5:].split(" ", 1)
        action = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        workspace = f"workspace/{session_id}/project"
        result = file_crud(action, args, workspace)
        return f"File: {result}"
    else:
        return "❌ Nieznana komenda! Użyj: ai: / py: / sh: / file:"
'@ | Out-File -Encoding utf8 "rtc/signaling.py"
Write-Host "  ✓ rtc/signaling.py" -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# KROK 6: SERVICES MODULE
# ══════════════════════════════════════════════════════════════════════════════

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  [6/9] 🛠️  ZAPISYWANIE SERVICES MODULE..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

# services/__init__.py
@'
# services package marker
'@ | Out-File -Encoding utf8 "services/__init__.py"
Write-Host "  ✓ services/__init__.py" -ForegroundColor Green

# services/python_tool.py
@'
# services/python_tool.py
import ast
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

async def exec_python(code: str):
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Eval, ast.Exec, ast.Delete, ast.Global, ast.Nonlocal)):
                return "[ERROR] Dangerous code blocked!"
        f = StringIO()
        e = StringIO()
        with redirect_stdout(f), redirect_stderr(e):
            exec(code, {"__builtins__": {}}, {})
        out = f.getvalue() + e.getvalue()
        return out or "OK – kod wykonany bez błędów"
    except Exception as err:
        return f"[ERROR] {str(err)}"
'@ | Out-File -Encoding utf8 "services/python_tool.py"
Write-Host "  ✓ services/python_tool.py" -ForegroundColor Green

# services/file_tool.py
@'
# services/file_tool.py
import os

def file_crud(action: str, args: str, base_path: str):
    full_path = os.path.join(base_path, args.split()[0]) if args else ""
    if action == "read":
        if os.path.exists(full_path):
            with open(full_path, "r") as f:
                content = f.read()
                return content[:500] + "..." if len(content) > 500 else content
        return "[ERROR] Plik nie istnieje"
    elif action == "write":
        content = args.split(" ", 1)[1] if " " in args else ""
        os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return "Zapisano!"
    elif action == "delete":
        if os.path.exists(full_path):
            os.remove(full_path)
            return "Usunięto!"
        return "[ERROR] Nie znaleziono"
    elif action == "list":
        return "\n".join(os.listdir(base_path))
    else:
        return "Komenda: read/write/delete/list path"
'@ | Out-File -Encoding utf8 "services/file_tool.py"
Write-Host "  ✓ services/file_tool.py" -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# KROK 7: GŁÓWNA APLIKACJA I STATIC
# ══════════════════════════════════════════════════════════════════════════════

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  [7/9] 🚀 ZAPISYWANIE APP.PY I DASHBOARD..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

# app.py - PATCHED VERSION
@'
# app.py
import os
import shutil
import uuid
import logging
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from debugger.debugger_loop import start_debug_loop
from rtc.signaling import handle_command
from config.env_config import get_config

try:
    config = get_config()
    config.validate()
except Exception as