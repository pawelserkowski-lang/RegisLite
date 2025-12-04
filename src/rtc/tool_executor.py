import asyncio
import json
import logging
from src.services.python_tool import exec_python
from src.services.file_tool import file_crud
from src.ai.model_client import ask_with_stats

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Wykonuje narzędzia zidentyfikowane przez router intencji.
    """
    def __init__(self, session_manager):
        self.session_manager = session_manager

    async def execute(
        self, tool: str, args: str, session_id: str, workspace_path: str
    ):
        """
        Uruchamia odpowiednie narzędzie i zwraca generator response.
        """
        def response(text, type_msg="log", dur=0, model="-"):
            return json.dumps({
                "type": type_msg,
                "content": text,
                "meta": {"duration": f"{dur:.2f}s", "model": model}
            })

        if tool == "ai":
            yield response("🧠 Myślę...", "progress")
            history = self.session_manager.get_history(session_id)
            answer, ai_time, ai_model = await ask_with_stats(history)
            yield response(answer, "result", ai_time, ai_model)
            self.session_manager.add_message(session_id, "assistant", answer)

        elif tool == "py":
            yield response("🐍 Wykonuję Python...", "progress")
            # TODO: Dodać obsługę timeoutów i izolacji
            res = await exec_python(args)
            output_content = f"```python\n{args}\n```\nWYNIK:\n{res}"
            yield response(output_content, "result", 0.0, "python")
            self.session_manager.add_message(
                session_id, "assistant", output_content
            )

        elif tool == "sh":
            yield response(f"💻 Shell: {args}", "progress")
            proc = await asyncio.create_subprocess_shell(
                args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace_path
            )
            stdout, stderr = await proc.communicate()
            res = (stdout.decode() + stderr.decode()).strip()
            output_content = f"```bash\n$ {args}\n{res}\n```"
            yield response(output_content, "result", 0.0, "shell")
            self.session_manager.add_message(
                session_id, "assistant", output_content
            )

        elif tool == "file":
            yield response("📂 Filesystem...", "progress")
            # Prosty parser args: "ścieżka [treść]"
            parts = args.split(" ", 1)
            path = parts[0]
            content = parts[1] if len(parts) > 1 else ""

            res = file_crud(path, content, workspace_path)
            output_content = f"FILE OP: {res}"
            yield response(res, "result", 0.0, "fs")
            self.session_manager.add_message(
                session_id, "assistant", output_content
            )

        else:
            yield response(f"Nieznane narzędzie: {tool}", "error")
