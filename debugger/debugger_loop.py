from .debugger_analyzer import scan_project
from .debugger_fix import generate_patches
from .debugger_patcher import apply_patches


async def start_debug_loop():
    """
    Prosta pętla debuggera:
    - maks. 10 przebiegów
    - szuka plików z 'FIXME' w treści
    - jeśli znajdzie, pyta GPT o poprawki
    - nakłada poprawki i kontynuuje
    """
    logs = []

    for i in range(10):
        logs.append(f"=== DEBUG PASS {i} ===")

        files = scan_project()
        if not files:
            logs.append("Brak plików w workspace/project.")
            break

        # prosta heurystyka – pliki z 'FIXME'
        errors = [f["path"] for f in files if "FIXME" in f["content"]]

        if not errors:
            logs.append("Brak błędów — projekt czysty.")
            break

        logs.append(f"Errors detected in: {errors}")

        patches_text = await generate_patches(str(errors), files)
        logs.append("Patches received from GPT.")

        changed_files = apply_patches(patches_text)
        logs.append(f"Patches applied to: {changed_files}")

    return logs
