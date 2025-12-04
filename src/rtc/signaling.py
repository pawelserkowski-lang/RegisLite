import json
import asyncio
import logging
from collections import defaultdict
from src.services.python_tool import exec_python
from src.services.file_tool import file_crud
import subprocess
from src.ai.chatgpt_client import classify_intent, ask_with_stats

logger = logging.getLogger(__name__)

# PAMIĘĆ SESJI (w pamięci RAM serwera)
# Format: { session_id: [ {"role": "user", "content": "..."} ... ] }
SESSION_MEMORY = defaultdict(list)

async def handle_command(raw_cmd: str, session_id: str):
    workspace = f"workspace/{session_id}/project"
    
    def response(text, type="log", duration=0, model="-"):
        return json.dumps({
            "type": type,
            "content": text,
            "meta": {"duration": f"{duration:.2f}s", "model": model}
        })

    try:
        # 1. Dodaj wiadomość użytkownika do pamięci
        SESSION_MEMORY[session_id].append({"role": "user", "content": raw_cmd})
        
        yield response("🤔 Analizuję...", "progress")
        intent, r_time, r_model = await classify_intent(raw_cmd)
        
        tool = intent.get("tool", "ai")
        args = intent.get("args", "")
        
        yield response(f"🎯 Narzędzie: {tool.upper()}", "progress")
        
        output_content = ""
        used_model = "-"
        exec_time = r_time

        # 2. Wykonanie
        if tool == "ai":
            yield response("🧠 Myślę...", "progress")
            # Przekazujemy CAŁĄ historię rozmowy
            history = SESSION_MEMORY[session_id]
            answer, ai_time, ai_model = await ask_with_stats(history)
            
            output_content = answer
            exec_time += ai_time
            used_model = ai_model
            
            yield response(answer, "result", exec_time, used_model)

        elif tool == "py":
            yield response("🐍 Wykonuję Python...", "progress")
            res = await exec_python(args)
            output_content = f"```python\n{args}\n```\nWYNIK:\n{res}"
            yield response(output_content, "result", exec_time, "python")

        elif tool == "sh":
            yield response(f"💻 Shell: {args}", "progress")
            proc = await asyncio.create_subprocess_shell(
                args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=workspace
            )
            stdout, stderr = await proc.communicate()
            res = (stdout.decode() + stderr.decode()).strip()
            output_content = f"```bash\n$ {args}\n{res}\n```"
            yield response(output_content, "result", exec_time, "shell")

        elif tool == "file":
            yield response("📂 Filesystem...", "progress")
            parts = args.split(" ", 1)
            res = file_crud(parts[0], parts[1] if len(parts) > 1 else "", workspace)
            output_content = f"FILE OP: {res}"
            yield response(res, "result", exec_time, "fs")

        # 3. Zapisz odpowiedź asystenta do pamięci (żeby AI pamiętało co zrobiło)
        SESSION_MEMORY[session_id].append({"role": "assistant", "content": output_content})

        # Ogranicznik pamięci (ostatnie 20 wiadomości, żeby nie zapchać tokenów)
        if len(SESSION_MEMORY[session_id]) > 20:
            SESSION_MEMORY[session_id] = SESSION_MEMORY[session_id][-20:]

    except Exception as e:
        logger.error(f"Error: {e}")
        yield response(f"💥 Błąd: {str(e)}", "error")
