# rtc/signaling.py
import asyncio
from services.python_tool import exec_python
from services.file_tool import file_crud
import subprocess
from debugger.chatgpt_client import ask_gpt

async def handle_command(cmd: str, session_id: str):
    if cmd.startswith("ai:"):
        prompt = cmd[3:]
        response = ask_gpt(prompt)
        return f"AI: {response}"
    elif cmd.startswith("py:"):
        code = cmd[3:]
        result = await exec_python(code)
        return f"Python: {result}"
    elif cmd.startswith("sh:"):
        shell_cmd = cmd[3:]
        result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
        return f"Shell: {result.stdout or result.stderr}"
    elif cmd.startswith("file:"):
        parts = cmd[5:].split(" ", 1)
        action = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        workspace = f"workspace/{session_id}/project"
        result = file_crud(action, args, workspace)
        return f"File: {result}"
    else:
        return "Nieznana komenda – użyj ai:/py:/sh:/file:"
