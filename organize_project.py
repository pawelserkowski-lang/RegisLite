import os
import shutil
from pathlib import Path

# --- KONFIGURACJA ŚCIEŻEK ---
PROJECT_ROOT = Path(".")
SRC_DIR = PROJECT_ROOT / "src"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DOCS_DIR = PROJECT_ROOT / "docs"

# Foldery, które trafią do src/ (logika aplikacji)
MODULES_TO_MOVE = ["ai", "rtc", "debugger", "services", "config", "static"]

# Główny plik aplikacji - zmienimy mu nazwę na main.py i wrzucimy do src
APP_FILES_MAP = {
    "app.py": "main.py"
}

# Skrypty pomocnicze i naprawcze - do folderu scripts/
SCRIPTS_TO_MOVE = [
    "brain_fix.py", "fix_final.py", "fix_formatter.py", 
    "repair_final.py", "upgrade_brain.py", 
    "check_size.ps1", "fix_debug_500.ps1", "fix_requirements.ps1",
    "fix_timeout_ignore.ps1", "git_push.ps1", "run.ps1", 
    "upgrade_ai_awareness.ps1", "upgrade_ui_ai.ps1", 
    "live.bat", "start.bat"
]

# Dokumentacja i logi - do folderu docs/
DOCS_TO_MOVE = [
    "ANALYSIS.md", "ENV_SETUP_GUIDE.md", "error_log.txt", 
    "install_log.txt", "server.log", "git_push prompt.txt", "logo prompt.txt"
]
# Folder notatki przenosimy cały do docs/notatki
NOTES_DIR = "notatki"

# Śmieci do usunięcia
TRASH = [
    "venv", "__pycache__", 
    "ai/__pycache__", "debugger/__pycache__", "rtc/__pycache__", "services/__pycache__",
    "niezbednik google drive.lnk"
]

def create_structure():
    """Tworzy foldery docelowe."""
    for d in [SRC_DIR, SCRIPTS_DIR, DOCS_DIR]:
        d.mkdir(exist_ok=True)
    # Dodaj __init__.py do src, aby był pakietem
    (SRC_DIR / "__init__.py").touch()
    print("✅ Struktura katalogów utworzona.")

def cleanup():
    """Usuwa venv i cache."""
    print("🧹 Rozpoczynam czyszczenie śmieci (to może chwilę potrwać)...")
    for item in TRASH:
        path = PROJECT_ROOT / item
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"   - Usunięto: {item}")
            except Exception as e:
                print(f"   ! Błąd przy usuwaniu {item}: {e}")

def move_items():
    """Przenosi pliki do odpowiednich folderów."""
    # 1. Moduły do src
    for module in MODULES_TO_MOVE:
        src = PROJECT_ROOT / module
        dst = SRC_DIR / module
        if src.exists():
            if dst.exists():
                print(f"⚠️  Moduł {module} już jest w src/, pomijam.")
            else:
                shutil.move(str(src), str(dst))
                print(f"📦 Przeniesiono moduł: {module} -> src/")

    # 2. App.py -> src/main.py
    for old, new in APP_FILES_MAP.items():
        src = PROJECT_ROOT / old
        dst = SRC_DIR / new
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"🚀 Przeniesiono aplikację: {old} -> src/{new}")

    # 3. Skrypty
    for script in SCRIPTS_TO_MOVE:
        src = PROJECT_ROOT / script
        dst = SCRIPTS_DIR / script
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"📜 Przeniesiono skrypt: {script} -> scripts/")

    # 4. Dokumentacja i logi
    for doc in DOCS_TO_MOVE:
        src = PROJECT_ROOT / doc
        dst = DOCS_DIR / doc
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"📄 Przeniesiono dok: {doc} -> docs/")
            
    # 5. Notatki
    src_notes = PROJECT_ROOT / NOTES_DIR
    dst_notes = DOCS_DIR / NOTES_DIR
    if src_notes.exists():
        if not dst_notes.exists():
            shutil.move(str(src_notes), str(dst_notes))
            print(f"📒 Przeniesiono notatki do docs/")

def create_run_script():
    """Tworzy plik run.py w głównym katalogu."""
    content = """
import uvicorn
import os
import sys

# Dodajemy katalog src do ścieżki systemowej
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    # Uruchamiamy aplikację wskazując na moduł w src
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
"""
    with open("run.py", "w", encoding="utf-8") as f:
        f.write(content.strip())
    print("✨ Utworzono nowy starter: run.py")

if __name__ == "__main__":
    create_structure()
    cleanup()
    move_items()
    create_run_script()
    print("\n✅ REFAKTORYZACJA ZAKOŃCZONA!")
    print("👉 Uruchom teraz: python run.py")