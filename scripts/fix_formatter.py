import os

# --- TREŚĆ PLIKU: debugger/debugger_fix.py ---
# Zapisana jako lista linii, żeby uniknąć problemów z wklejaniem
lines = [
    "import traceback",
    "import sys",
    "import platform",
    "import os",
    "from typing import Dict, List",
    "from ai.chatgpt_client import ask",
    "",
    "# Wykrywanie srodowiska",
    "PYTHON_VER = f'{sys.version_info.major}.{sys.version_info.minor}'",
    "OS_NAME = f'{platform.system()} {platform.release()}'",
    "PATH_SEP = os.sep",
    "",
    "# Instrukcje dla AI",
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
    "Napraw błędy wskazane w sekcji ZADANIE.",
    "Analizuj dostarczone w sekcji PLIKI fragmenty kodu.",
    "Zwróć poprawiony kod w formacie blokowym.",
    "",
    "[[ FORMAT ]]",
    "FILE: sciezka{PATH_SEP}plik.py",
    "```python",
    "<caly_poprawiony_plik_lub_zmiany>",
    "```",
    "END_FILE",
    "",
    "Jeśli kod jest poprawny: NO_CHANGES_NEEDED",
    "'''",
    "",
    "def _format_files(files: List[Dict[str, str]]) -> str:",
    "    formatted = []",
    "    # Bierzemy max 20 plików",
    "    for f in files[:20]:",
    "        path = f['path']",
    "        content = f.get('content', '')",
    "        # Zabezpieczenie przed tokenami",
    "        if len(content) > 30000:",
    "            content = '<PLIK ZA DUZY - POMINIETO TRESC>'",
    "        formatted.append(f'=== PLIK: {path} ===\\n{content}\\n')",
    "    return '\\n'.join(formatted)",
    "",
    "async def generate_patches(errors: str, files: List[Dict[str, str]]) -> str:",
    "    # Formatowanie plikow do promptu",
    "    files_str = _format_files(files)",
    "    ",
    "    # Debug - sprawdzamy czy pliki w ogole wchodza",
    "    if not files_str.strip():",
    "        return 'BLAD: Nie udalo sie wczytac tresci plikow do promptu.'",
    "",
    "    header = f'SYSTEM: {OS_NAME} | CWD: {os.getcwd()}'",
    "    prompt = f'{PATCH_INSTRUCTIONS}\\n[{header}]\\nZADANIE:\\n{errors}\\nPLIKI:\\n{files_str}'",
    "",
    "    try:",
    "        return await ask(prompt)",
    "    except Exception as e:",
    "        return f'LLM error: {traceback.format_exc()}'"
]

# Zapis pliku
target = os.path.join("debugger", "debugger_fix.py")

try:
    with open(target, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ SUKCES: Plik {target} został naprawiony i sformatowany!")
    print("👉 Koniecznie zrestartuj start.bat!")
except Exception as e:
    print(f"❌ BŁĄD: {e}")