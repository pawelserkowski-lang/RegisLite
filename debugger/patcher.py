# debugger/patcher.py
import os
import shutil

def apply_patch(session_id: str, diff: str):
    workspace = f"workspace/{session_id}"
    project = f"{workspace}/project"
    backup = f"{workspace}/backups/backup_{os.urandom(4).hex()}"
    shutil.copytree(project, backup)
    return {"backup_created": backup, "applied": "FAKE PATCH – działa!"}
