import os

# 1. NOWY DEBUGGER LOOP (Z obsługą Audytu)
loop_code = r'''import os
import asyncio
from .debugger_analyzer import scan_project
from .debugger_fix import generate_patches
from .debugger_patcher import apply_patches

async def start_debug_loop(session_id: str):
    """
    Pętla debuggera:
    - Runda 1: Szuka FIXME. Jak nie ma -> Tryb AUDYT.
    - Kolejne rundy: Poprawia błędy.
    """
    project_path = f"workspace/{session_id}/project"
    logs = []
    logs.append(f"🔍 Start sesji {session_id}...")
    
    if not os.path.exists(project_path):
        logs.append("❌ BŁĄD: Brak projektu!")
        return logs

    MAX_ROUNDS = 5 
    mode = "FIX"

    for i in range(1, MAX_ROUNDS + 1):
        logs.append(f"\n--- 🔄 RUNDA {i}/{MAX_ROUNDS} ---")
        
        files = scan_project(project_path)
        if not files:
            logs.append("⚠️ Pusty projekt.")
            break

        # Szukamy jawnych błędów
        explicit_targets = []
        for f in files:
            if any(tag in f.get("content", "") for tag in ["FIXME", "TODO", "BUG"]):
                explicit_targets.append(f["path"])
        
        errors = []
        if explicit_targets:
            logs.append(f"🎯 Znaleziono znaczniki w {len(explicit_targets)} plikach.")
            errors = explicit_targets
            mode = "FIX"
        else:
            if i == 1:
                logs.append("🕵️ Brak 'FIXME'. Włączam tryb PEŁNEGO AUDYTU...")
                errors = ["AUDYT_OGOLNY: Przeanalizuj kod, znajdź błędy logiczne, braki w imporcie i bezpieczeństwo."]
                mode = "AUDIT"
            else:
                logs.append("✅ Projekt czysty.")
                break

        # Generowanie
        patches_text = await generate_patches(str(errors), files)
        
        if "NO_CHANGES_NEEDED" in patches_text:
            logs.append("✅ AI zatwierdziło kod.")
            break
        if "LLM error" in patches_text:
            logs.append(f"❌ Błąd AI: {patches_text}")
            break

        # Aplikowanie
        changed = apply_patches(patches_text, project_path)
        if changed:
            logs.append(f"🛠️ Naprawiono: {changed}")
        else:
            if mode == "AUDIT":
                logs.append("ℹ️ Audyt zakończony (brak zmian w kodzie).")
                break
            logs.append("⚠️ AI nie podało poprawnych zmian.")

    logs.append("\n🏁 Koniec.")
    return logs
'''

# 2. NOWY DEBUGGER FIX (Z obsługą Systemu i Audytu)
fix_code = r'''import traceback
import sys
import platform
import os
from typing import Dict, List
from ai.chatgpt_client import ask

# Wykrywanie środowiska
PYTHON_VER = f"{sys.version_info.major}.{sys.version_info.minor}"
OS_NAME = f"{platform.system()} {platform.release()}"
PATH_SEP = os.sep

PATCH_INSTRUCTIONS = f"""
Jesteś Starszym Inżynierem (Senior Python Dev).

[[ TWOJE ŚRODOWISKO ]]
- System: {OS_NAME}
- Python: {PYTHON_VER}
- Separator: '{PATH_SEP}'
- Dostęp: PEŁNY (Internet + Pliki)

[[ ZADANIE ]]
1. Jeśli wejście to "AUDYT_OGOLNY": Przeanalizuj całość. Szukaj błędów logicznych.
2. Jeśli są błędy: Zwróć kod w blokach FILE.
3. Jeśli kod jest OK: Zwróć NO_CHANGES_NEEDED.

[[ FORMAT ]]
FILE: sciezka{PATH_SEP}plik.py
```python
<kod>