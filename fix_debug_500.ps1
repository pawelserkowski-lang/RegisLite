Write-Host "=== Regis DEBUGGER BRAIN TRANSPLANT ===" -ForegroundColor Cyan
Set-Location (Split-Path $MyInvocation.MyCommand.Path)

# 1. Naprawiamy ANALYZER (żeby skanował dobry folder)
$analyzerCode = @'
import os
from typing import List, Dict

def scan_project(base_path: str) -> List[Dict[str, str]]:
    """
    Skanuje podany katalog (base_path) i zwraca listę:
    { 'path': ścieżka_względna, 'content': zawartość }
    """
    result = []

    if not os.path.exists(base_path):
        return result

    for root, _, files in os.walk(base_path):
        for name in files:
            full_path = os.path.join(root, name)
            # Oblicz ścieżkę względną dla AI (np. main.py zamiast workspace/sesja/project/main.py)
            rel_path = os.path.relpath(full_path, base_path)
            
            try:
                with open(full_path, "r", encoding="utf8") as f:
                    content = f.read()
            except Exception:
                content = "[Binary or Error]"
                
            result.append({"path": rel_path, "content": content})

    return result
'@
$analyzerCode | Set-Content "debugger/debugger_analyzer.py" -Encoding UTF8
Write-Host "[1/3] debugger_analyzer.py naprawiony (obsługa ścieżek)" -ForegroundColor Green

# 2. Naprawiamy PATCHER (żeby zapisywał w dobrym folderze)
$patcherCode = @'
import os
import shutil
from typing import List

def apply_patches(patch_text: str, base_path: str) -> List[str]:
    """
    Aplikuje zmiany w plikach wewnątrz base_path.
    """
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
                _write_file(current_file, "\n".join(buffer), base_path)
                modified_files.append(current_file)
                buffer = []
            
            # Usuń ewentualne prefiksy ścieżek, jeśli AI zwariuje
            raw_path = line[len("FILE:"):].strip()
            current_file = raw_path.replace("workspace/project/", "").strip("/")
            
            in_code = False
            continue

        if line.strip().startswith("```"):
            in_code = not in_code
            continue

        if line.strip() == "END_FILE":
            if current_file and buffer:
                _write_file(current_file, "\n".join(buffer), base_path)
                modified_files.append(current_file)
            current_file = None
            buffer = []
            in_code = False
            continue

        if in_code and current_file:
            buffer.append(line)

    if current_file and buffer:
        _write_file(current_file, "\n".join(buffer), base_path)
        modified_files.append(current_file)

    return modified_files

def _write_file(rel_path: str, content: str, base_dir: str) -> None:
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if os.path.exists(full_path):
        shutil.copy(full_path, full_path + ".bak")

    with open(full_path, "w", encoding="utf8") as f:
        f.write(content)
'@
$patcherCode | Set-Content "debugger/debugger_patcher.py" -Encoding UTF8
Write-Host "[2/3] debugger_patcher.py naprawiony (obsługa backupów w sesji)" -ForegroundColor Green

# 3. Naprawiamy LOOP (Główna pętla - tu był błąd 500)
$loopCode = @'
import os
from .debugger_analyzer import scan_project
from .debugger_fix import generate_patches
from .debugger_patcher import apply_patches

async def start_debug_loop(session_id: str):
    """
    Pętla debuggera obsługująca konkretną sesję.
    """
    # Dynamiczna ścieżka do projektu w sesji
    project_path = f"workspace/{session_id}/project"
    
    logs = []
    logs.append(f"🔍 Rozpoczynam debugowanie sesji {session_id}...")
    logs.append(f"📂 Katalog roboczy: {project_path}")

    if not os.path.exists(project_path):
        logs.append("❌ BŁĄD: Katalog projektu nie istnieje!")
        return logs

    for i in range(1, 11): # Max 10 iteracji
        logs.append(f"\n--- 🔄 ITERACJA {i} ---")

        # 1. Skanowanie (przekazujemy ścieżkę!)
        files = scan_project(project_path)
        if not files:
            logs.append("⚠️ Pusty projekt lub brak plików tekstowych.")
            break

        # 2. Szukanie błędów (prosta heurystyka FIXME)
        # Możesz tu dodać też szukanie "Error" lub innych słów kluczowych
        errors = [f["path"] for f in files if "FIXME" in f.get("content", "")]

        if not errors:
            logs.append("✅ SUKCES: Nie znaleziono więcej 'FIXME'. Projekt czysty!")
            break

        logs.append(f"🐛 Znaleziono błędy w: {errors}")

        # 3. Pytanie do AI
        logs.append("🤖 Generuję poprawki (to może chwilę potrwać)...")
        patches_text = await generate_patches(str(errors), files)
        
        if "LLM error" in patches_text:
            logs.append(f"❌ Błąd AI: {patches_text}")
            break

        # 4. Aplikowanie zmian (przekazujemy ścieżkę!)
        changed = apply_patches(patches_text, project_path)
        if changed:
            logs.append(f"🛠️ Naprawiono pliki: {changed}")
        else:
            logs.append("⚠️ AI nie zwróciło poprawnych zmian (albo halucynuje).")
            # Czasem warto spróbować jeszcze raz, ale tu przerywamy pętlę nieskończoną
            if i > 3: 
                logs.append("🛑 Przerywam: brak postępów.")
                break

    logs.append("\n🏁 Debugowanie zakończone.")
    return logs
'@
$loopCode | Set-Content "debugger/debugger_loop.py" -Encoding UTF8
Write-Host "[3/3] debugger_loop.py naprawiony (przyjmuje session_id)" -ForegroundColor Green

Write-Host "`n✅ GOTOWE! Zrestartuj serwer (zamknij i uruchom start.bat)." -ForegroundColor Yellow