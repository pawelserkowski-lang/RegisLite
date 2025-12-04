import os
import asyncio
from .debugger_analyzer import scan_project
from .debugger_fix import generate_patches
from .debugger_patcher import apply_patches

async def start_debug_loop(session_id: str):
    project_path = f"workspace/{session_id}/project"
    logs = []
    
    def log(msg):
        logs.append(msg)

    log(f"🔍 Start sesji {session_id}...")
    if not os.path.exists(project_path):
        log("❌ BŁĄD: Brak projektu!")
        return logs

    MAX_ROUNDS = 5
    previous_patches = [] # Pamięć co już robiliśmy

    for i in range(1, MAX_ROUNDS + 1):
        log(f"\n--- 🔄 RUNDA {i}/{MAX_ROUNDS} ---")
        
        # 1. Pełny skan
        all_files = scan_project(project_path)
        if not all_files:
            log("⚠️ Pusty projekt.")
            break

        # 2. Filtracja kontekstu (OSZCZĘDNOŚĆ TOKENÓW!)
        context_files = []
        explicit_targets = []
        
        # Szukamy znaczników błędów
        for f in all_files:
            content = f.get("content", "")
            path = f["path"]
            
            has_tag = any(tag in content for tag in ["FIXME", "TODO", "BUG", "ERROR"])
            # Pliki edytowane w poprzedniej rundzie też bierzemy do kontekstu
            was_edited = any(p in path for p in previous_patches)
            
            if has_tag:
                explicit_targets.append(path)
            
            if has_tag or was_edited or i == 1:
                # W 1. rundzie bierzemy wszystko (lub limit), w kolejnych tylko istotne
                context_files.append(f)

        # Jeśli runda > 1 i nie ma żadnych punktów zaczepienia -> koniec
        if i > 1 and not context_files and not explicit_targets:
            log("✅ Brak nowych celów do naprawy.")
            break
            
        # Jeśli kontekst jest pusty (np. runda 2, brak błędów), ale kod działa -> OK
        if not context_files:
            # Fallback: weź main.py lub app.py żeby sprawdzić czy działa
            context_files = [f for f in all_files if "main" in f["path"] or "app" in f["path"]]

        log(f"📉 Zoptymalizowany kontekst: {len(context_files)} plików (z {len(all_files)})")
        
        # 3. Decyzja o trybie
        errors_desc = []
        if explicit_targets:
            log(f"🎯 Znaleziono znaczniki w: {explicit_targets}")
            errors_desc = explicit_targets
        else:
            if i == 1:
                log("🕵️ Tryb AUDYT (szukam ukrytych błędów)...")
                errors_desc = ["AUDYT_OGOLNY: Kod działa? Są błędy logiczne?"]
            else:
                log("✅ Projekt wygląda na czysty.")
                break

        # 4. Generowanie (AI)
        patches_text = await generate_patches(str(errors_desc), context_files)
        
        if "NO_CHANGES_NEEDED" in patches_text:
            log("✅ AI zatwierdziło kod.")
            break
        if "LLM error" in patches_text:
            log(f"❌ Błąd AI: {patches_text}")
            break

        # 5. Aplikowanie
        changed_files = apply_patches(patches_text, project_path)
        if changed_files:
            log(f"🛠️ Naprawiono: {changed_files}")
            previous_patches = changed_files # Zapamiętaj co zmieniliśmy
        else:
            log("⚠️ AI nie podało poprawnych zmian.")
            if i > 1: break # Jak w kolejnej rundzie nic nie wymyślił, to koniec

    log("\n🏁 Koniec debugowania.")
    return logs
