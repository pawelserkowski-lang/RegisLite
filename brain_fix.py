import os

# --- BUDOWANIE PLIKU: debugger_loop.py ---
loop_lines = [
    "import os",
    "import asyncio",
    "from .debugger_analyzer import scan_project",
    "from .debugger_fix import generate_patches",
    "from .debugger_patcher import apply_patches",
    "",
    "async def start_debug_loop(session_id: str):",
    "    project_path = f'workspace/{session_id}/project'",
    "    logs = []",
    "    logs.append(f'🔍 Start sesji {session_id}...')",
    "",
    "    if not os.path.exists(project_path):",
    "        logs.append('❌ BŁĄD: Brak projektu!')",
    "        return logs",
    "",
    "    MAX_ROUNDS = 5",
    "    mode = 'FIX'",
    "",
    "    for i in range(1, MAX_ROUNDS + 1):",
    "        logs.append(f'\\n--- 🔄 RUNDA {i}/{MAX_ROUNDS} ---')",
    "        files = scan_project(project_path)",
    "        if not files:",
    "            logs.append('⚠️ Pusty projekt.')",
    "            break",
    "",
    "        explicit_targets = []",
    "        for f in files:",
    "            content = f.get('content', '')",
    "            if any(tag in content for tag in ['FIXME', 'TODO', 'BUG']):",
    "                explicit_targets.append(f['path'])",
    "",
    "        errors = []",
    "        if explicit_targets:",
    "            logs.append(f'🎯 Znaleziono znaczniki w {len(explicit_targets)} plikach.')",
    "            errors = explicit_targets",
    "            mode = 'FIX'",
    "        else:",
    "            if i == 1:",
    "                logs.append('🕵️ Brak znaczników. Tryb: AUDYT...')",
    "                errors = ['AUDYT_OGOLNY: Przeanalizuj kod, znajdź błędy logiczne.']",
    "                mode = 'AUDIT'",
    "            else:",
    "                logs.append('✅ Projekt czysty.')",
    "                break",
    "",
    "        patches_text = await generate_patches(str(errors), files)",
    "        if 'NO_CHANGES_NEEDED' in patches_text:",
    "            logs.append('✅ AI zatwierdziło kod.')",
    "            break",
    "        if 'LLM error' in patches_text:",
    "            logs.append(f'❌ Błąd AI: {patches_text}')",
    "            break",
    "",
    "        changed = apply_patches(patches_text, project_path)",
    "        if changed:",
    "            logs.append(f'🛠️ Naprawiono: {changed}')",
    "        else:",
    "            if mode == 'AUDIT':",
    "                logs.append('ℹ️ Audyt zakończony (brak zmian).')",
    "                break",
    "            logs.append('⚠️ AI nie podało poprawnych zmian.')",
    "",
    "    logs.append('\\n🏁 Koniec.')",
    "    return logs"
]

# --- BUDOWANIE PLIKU: debugger_fix.py ---
fix_lines = [
    "import traceback, sys, platform, os",
    "from typing import Dict, List",
    "from ai.chatgpt_client import ask",
    "",
    "# Srodowisko",
    "PYTHON_VER = f'{sys.version_info.major}.{sys.version_info.minor}'",
    "OS_NAME = f'{platform.system()} {platform.release()}'",
    "PATH_SEP = os.sep",
    "",
    "PATCH_INSTRUCTIONS = f'''",
    "Jesteś Starszym Inżynierem (Senior Python Dev).",
    "",
    "[[ TWOJE ŚRODOWISKO ]]",
    "- System: {OS_NAME}",
    "- Python: {PYTHON_VER}",
    "- Separator: \"{PATH_SEP}\"",
    "- Dostęp: PEŁNY",
    "",
    "[[ ZADANIE ]]",
    "1. AUDYT_OGOLNY -> Przeanalizuj całość.",
    "2. FIXME/TODO -> Napraw konkretne miejsca.",
    "3. Zwróć kod w blokach FILE lub NO_CHANGES_NEEDED.",
    "",
    "[[ FORMAT ]]",
    "FILE: sciezka{PATH_SEP}plik.py",
    "```python",
    "<kod>",
    "```",
    "END_FILE",
    "'''",
    "",
    "def _format_files(files: List[Dict[str, str]]) -> str:",
    "    formatted = []",
    "    for f in files[:20]:",
    "        path = f['path']",
    "        content = f.get('content', '')",
    "        if len(content) > 30000: content = '<ZA DUŻY>'",
    "        formatted.append(f'=== PLIK: {path} ===\\n{content}\\n')",
    "    return '\\n'.join(formatted)",
    "",
    "async def generate_patches(errors: str, files: List[Dict[str, str]]) -> str:",
    "    files_str = _format_files(files)",
    "    header = f'SYSTEM: {OS_NAME} | CWD: {os.getcwd()}'",
    "    prompt = f'{PATCH_INSTRUCTIONS}\\n[{header}]\\nZADANIE:\\n{errors}\\nPLIKI:\\n{files_str}'",
    "    try:",
    "        return await ask(prompt)",
    "    except Exception as e:",
    "        return f'LLM error: {traceback.format_exc()}'"
]

def write_file(path, lines):
    full_path = os.path.join(*path.split("/"))
    try:
        content = "\n".join(lines)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Naprawiono: {full_path}")
    except Exception as e:
        print(f"❌ Błąd zapisu {full_path}: {e}")

if __name__ == "__main__":
    print("=== REGISLITE BRAIN FIXER ===")
    write_file("debugger/debugger_loop.py", loop_lines)
    write_file("debugger/debugger_fix.py", fix_lines)
    print("\n👉 GOTOWE! Zrestartuj teraz start.bat")