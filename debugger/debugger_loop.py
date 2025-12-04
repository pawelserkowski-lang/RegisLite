import os
import asyncio
from .debugger_analyzer import scan_project
from .debugger_fix import generate_patches
from .debugger_patcher import apply_patches

async def start_debug_loop(session_id: str):
    # --- Pętla naprawiona: obsługuje session_id ---
    project_path = f'workspace/{session_id}/project'
    logs = []
    logs.append(f'🔍 Start sesji {session_id}...')

    if not os.path.exists(project_path):
        logs.append('❌ BŁĄD: Brak projektu!')
        return logs

    MAX_ROUNDS = 5
    mode = 'FIX'

    for i in range(1, MAX_ROUNDS + 1):
        logs.append(f'\n--- 🔄 RUNDA {i}/{MAX_ROUNDS} ---')
        files = scan_project(project_path)
        if not files:
            logs.append('⚠️ Pusty projekt.')
            break

        # Wykrywanie FIXME
        explicit_targets = []
        for f in files:
            content = f.get('content', '')
            if any(tag in content for tag in ['FIXME', 'TODO', 'BUG']):
                explicit_targets.append(f['path'])

        errors = []
        if explicit_targets:
            logs.append(f'🎯 Znaleziono znaczniki w {len(explicit_targets)} plikach.')
            errors = explicit_targets
            mode = 'FIX'
        else:
            if i == 1:
                logs.append('🕵️ Brak znaczników. Tryb: AUDYT...')
                errors = ['AUDYT_OGOLNY: Przeanalizuj kod, znajdź błędy logiczne.']
                mode = 'AUDIT'
            else:
                logs.append('✅ Projekt czysty.')
                break

        # Generowanie
        patches_text = await generate_patches(str(errors), files)
        if 'NO_CHANGES_NEEDED' in patches_text:
            logs.append('✅ AI zatwierdziło kod.')
            break
        if 'LLM error' in patches_text:
            logs.append(f'❌ Błąd AI: {patches_text}')
            break

        # Aplikowanie
        changed = apply_patches(patches_text, project_path)
        if changed:
            logs.append(f'🛠️ Naprawiono: {changed}')
        else:
            if mode == 'AUDIT':
                logs.append('ℹ️ Audyt zakończony (brak zmian).')
                break
            logs.append('⚠️ AI nie podało poprawnych zmian.')

    logs.append('\n🏁 Koniec.')
    return logs