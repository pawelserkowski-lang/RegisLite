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
