# rtc/signaling.py - FIXED VERSION
import asyncio
from services.python_tool import exec_python
from services.file_tool import file_crud
import subprocess
from ai.chatgpt_client import ask

async def handle_command(cmd: str, session_id: str):
    """
    Obsługuje komendy z terminala WebSocket:
    - ai:prompt → zapytanie do ChatGPT
    - py:code → wykonanie kodu Python
    - sh:command → wykonanie komendy shell
    - file:action args → operacje na plikach
    """
    if cmd.startswith("ai:"):
        prompt = cmd[3:].strip()
        response = await ask(prompt)
        return f"AI: {response}"
    
    elif cmd.startswith("py:"):
        code = cmd[3:].strip()
        result = await exec_python(code)
        return f"Python: {result}"
    
    elif cmd.startswith("sh:"):
        shell_cmd = cmd[3:].strip()
        try:
            result = subprocess.run(
                shell_cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return f"Shell: {result.stdout or result.stderr}"
        except subprocess.TimeoutExpired:
            return "Shell: [ERROR] Timeout - komenda trwała za długo"
        except Exception as e:
            return f"Shell: [ERROR] {str(e)}"
    
    elif cmd.startswith("file:"):
        parts = cmd[5:].split(" ", 1)
        action = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        workspace = f"workspace/{session_id}/project"
        result = file_crud(action, args, workspace)
        return f"File: {result}"
    
    else:
        return "❌ Nieznana komenda! Użyj: ai: / py: / sh: / file:"
