# debugger/loop.py
import asyncio
from .analyzer import simple_scan
from .fix import generate_fake_fix
from .patcher import apply_patch

async def start_debug_loop(session_id: str, max_iters=5):
    workspace = f"workspace/{session_id}"
    project_path = f"{workspace}/project"
    
    logs = ["Rozpoczynam pętlę debugowania RegisLite..."]

    for i in range(1, max_iters + 1):
        logs.append(f"\n--- ITERACJA {i}/{max_iters} ---")
        errors = simple_scan(project_path)
        
        if len(errors) == 1 and "nie ma błędów" in errors[0]["message"]:
            logs.append("Kod jest czysty! Kończę pracę.")
            break
            
        for error in errors:
            logs.append(f"Błąd: {error['file']}:{error['line']} → {error['message']}")
            diff = generate_fake_fix(error)
            logs.append(f"GPT proponuje:\n{diff}")
            result = apply_patch(session_id, diff)
            logs.append(f"Patch zastosowany (backup: {result['backup_created']})")
    
    shutil.rmtree(f"{workspace}/output_fixed", ignore_errors=True)
    shutil.copytree(project_path, f"{workspace}/output_fixed")
    
    logs.append("\nGOTOWE! Pobierz folder output_fixed!")
    return {"status": "success", "logs": "\n".join(logs)}
