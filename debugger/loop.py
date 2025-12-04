# debugger/loop.py
import shutil
from .analyzer import simple_scan
from .fix import generate_fix
from .patcher import apply_patch

async def start_debug_loop(session_id: str, max_iters: int = 5):
    workspace = f"workspace/{session_id}"
    project = f"{workspace}/project"
    logs = ["Rozpoczynam auto-naprawę kodu..."]

    for it in range(1, max_iters + 1):
        logs.append(f"\nITERACJA {it}/{max_iters}")
        errors = simple_scan(project)

        if "Kod czysty" in errors[0]["message"]:
            logs.append("Kod jest idealny! Kończę pracę.")
            break

        for err in errors:
            logs.append(f"Błąd w {err['file']}:{err['line']} → {err['message']}")
            diff = generate_fix(err)
            logs.append(f"Propozycja fixu:\n{diff}")
            result = apply_patch(session_id, diff)
            logs.append(f"{result['status']}")

    shutil.rmtree(f"{workspace}/output_fixed", ignore_errors=True)
    shutil.copytree(project, f"{workspace}/output_fixed")

    logs.append("\nGOTOWE! Sprawdź folder: workspace/{session_id}/output_fixed")
    return {"status": "success", "logs": "\n".join(logs), "session": session_id}
