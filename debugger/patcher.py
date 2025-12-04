# debugger/patcher.py
import os
import shutil

def apply_patch(session_id: str, diff: str):
    workspace = f"workspace/{session_id}"
    backup_dir = f"{workspace}/backups/backup_{os.urandom(4).hex()}"
    shutil.copytree(f"{workspace}/project", backup_dir)
    return {"backup": backup_dir, "status": "FAKE PATCH ZASTOSOWANY (backup zrobiony)"}
