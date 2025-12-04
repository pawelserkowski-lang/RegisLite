import json
import asyncio
import subprocess
import logging
from src.services.python_tool import exec_python
from src.services.file_tool import file_crud
# UWAGA: Importujemy nowe funkcje async
from src.ai.chatgpt_client import classify_intent, ask_with_stats

logger = logging.getLogger(__name__)

async def handle_command(raw_cmd: str, session_id: str):
    """
    Orkiestrator WebSocket.
    """
    workspace = f"workspace/{session_id}/project"
    
    def response(text, type="log", duration=0, model="-"):
        return json.dumps({
            "type": type,
            "content": text,
            "meta": {"duration": f"{duration:.2f}s", "model": model}
        })

    try:
        # --- ETAP 1: ROUTING ---
        yield response("🤔 Analizuję...", "progress")
        intent, r_time, r_model = await classify_intent(raw_cmd)
        
        tool = intent.get("tool", "ai")
        args = intent.get("args", "")
        
        yield response(f"🎯 Narzędzie: {tool.upper()}", "progress")
        
        # --- ETAP 2: EGZEKUCJA ---
        if tool == "ai":
            yield response("🧠 Myślę...", "progress")
            answer, ai_time, ai_model = await ask_with_stats(args)
            yield response(answer, "result", r_time + ai_time, ai_model)

        elif tool == "py":
            yield response("🐍 Wykonuję kod...", "progress")
            res = await exec_python(args) # To już jest async w Twoim kodzie? Jeśli nie, warto sprawdzić.
            # Jeśli exec_python nie jest async, trzeba go owinąć, ale w services/python_tool.py wyglądał na async.
            yield response(f"```python\n{args}\n```\n>>> {res}", "result", r_time, "python-sandbox")

        elif tool == "sh":
            yield response(f"💻 Shell: {args}", "progress")
            # Uruchamianie w podprocesie bez blokowania
            proc = await asyncio.create_subprocess_shell(
                args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace
            )
            stdout, stderr = await proc.communicate()
            output = stdout.decode() + stderr.decode()
            yield response(f"```bash\n{output}\n```", "result", r_time, "shell")

        elif tool == "file":
            yield response("📂 System plików...", "progress")
            parts = args.split(" ", 1)
            action = parts[0]
            f_args = parts[1] if len(parts) > 1 else ""
            # File operations są szybkie, ale dla dużych plików warto by to dać w run_in_executor
            res = file_crud(action, f_args, workspace)
            yield response(res, "result", r_time, "fs")

    except Exception as e:
        logger.error(f"Signaling Error: {e}")
        yield response(f"💥 Błąd krytyczny: {str(e)}", "error")