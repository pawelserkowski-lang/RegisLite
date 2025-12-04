import json
import logging
from src.ai.model_client import classify_intent
from src.rtc.session_manager import SessionManager
from src.rtc.tool_executor import ToolExecutor
from src.config.errors import BaseError

logger = logging.getLogger(__name__)

# Instancja singleton (dla uproszczenia w pamięci RAM)
session_manager = SessionManager()
tool_executor = ToolExecutor(session_manager)


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
        session_manager.add_message(session_id, "user", raw_cmd)

        yield response("🤔 Analizuję...", "progress")
        intent, r_time, r_model = await classify_intent(raw_cmd)

        tool = intent.get("tool", "ai")
        args = intent.get("args", "")

        yield response(f"🎯 Narzędzie: {tool.upper()}", "progress")

        # 2. Delegacja do ToolExecutor
        # ToolExecutor zwraca generator wiadomości JSON
        async for msg in tool_executor.execute(tool, args, session_id, workspace):
            yield msg

    except BaseError as e:
        logger.error(f"Known Error: {e.message} ({e.details})")
        yield response(f"⚠️ Błąd: {e.message}", "error")
    except Exception as e:
        logger.error(f"Critical Error: {e}", exc_info=True)
        yield response(f"💥 Błąd krytyczny: {str(e)}", "error")
