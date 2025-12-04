import json
import asyncio
from services.python_tool import exec_python
from services.file_tool import file_crud
import subprocess
from ai.chatgpt_client import classify_intent, ask_with_stats

async def handle_command(raw_cmd: str, session_id: str):
    """
    Teraz ta funkcja zwraca JSON-string, żeby frontend mógł aktualizować UI.
    Format: { "type": "log"|"progress", "content": "...", "meta": {...} }
    """
    workspace = f"workspace/{session_id}/project"
    
    # Helper do formatowania odpowiedzi dla frontendu
    def response(text, type="log", duration=0, model="-"):
        return json.dumps({
            "type": type,
            "content": text,
            "meta": {
                "duration": f"{duration:.2f}s",
                "model": model
            }
        })

    # 1. Krok: Analiza Intencji (Router)
    try:
        # Raportujemy, że myślimy
        yield response("🤔 Analizuję intencję...", "progress")
        
        intent, router_time, router_model = await classify_intent(raw_cmd)
        tool = intent.get("tool", "ai")
        args = intent.get("args", "")
        
        yield response(f"🎯 Wybrano narzędzie: {tool.upper()}", "progress")
        
    except Exception as e:
        yield response(f"❌ Błąd routera: {str(e)}", "error")
        return

    # 2. Wykonanie właściwego narzędzia
    try:
        if tool == "ai":
            yield response("🧠 Generuję odpowiedź...", "progress")
            answer, ai_time, ai_model = await ask_with_stats(args)
            total_time = router_time + ai_time
            yield response(answer, "result", total_time, ai_model)

        elif tool == "py":
            yield response("🐍 Wykonuję kod...", "progress")
            # Symulujemy krótki delay dla UX ;)
            await asyncio.sleep(0.5)
            result = await exec_python(args)
            yield response(f"```python\n{args}\n```\n>>> {result}", "result", router_time, "python-sandbox")

        elif tool == "sh":
            yield response(f"🖥️ > {args}", "progress")
            process = subprocess.run(
                args, shell=True, capture_output=True, text=True, timeout=30, cwd=workspace
            )
            output = process.stdout or process.stderr or "(brak outputu)"
            yield response(f"```bash\n{output}\n```", "result", router_time, "shell")

        elif tool == "file":
            yield response(f"📂 Operacja plików...", "progress")
            # Prosty parser dla file_crud
            parts = args.split(" ", 1)
            action = parts[0]
            f_args = parts[1] if len(parts) > 1 else ""
            res = file_crud(action, f_args, workspace)
            yield response(res, "result", router_time, "fs-manager")

        else:
            yield response("⚠️ Nieznane narzędzie wybrane przez AI.", "error")

    except Exception as e:
        yield response(f"💥 Błąd wykonania: {str(e)}", "error")

