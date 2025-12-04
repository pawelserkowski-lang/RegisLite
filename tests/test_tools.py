import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.rtc.tool_executor import ToolExecutor
import json

@pytest.fixture
def mock_session_manager():
    sm = MagicMock()
    sm.get_history.return_value = []
    return sm

@pytest.mark.asyncio
async def test_tool_executor_sh(mock_session_manager):
    executor = ToolExecutor(mock_session_manager)

    with patch("asyncio.create_subprocess_shell") as mock_shell:
        # Mock subprocess
        process_mock = AsyncMock()
        process_mock.communicate.return_value = (b"output", b"")
        mock_shell.return_value = process_mock

        results = []
        async for msg in executor.execute("sh", "echo test", "sess1", "/tmp"):
            results.append(json.loads(msg))

        # Sprawdzamy czy są 2 wiadomości: progress i result
        assert len(results) == 2
        assert results[0]["type"] == "progress"
        assert results[1]["type"] == "result"
        assert "output" in results[1]["content"]

@pytest.mark.asyncio
async def test_tool_executor_ai(mock_session_manager):
    executor = ToolExecutor(mock_session_manager)

    with patch("src.rtc.tool_executor.ask_with_stats", new_callable=AsyncMock) as mock_ask:
        mock_ask.return_value = ("AI Response", 1.0, "gpt-mock")

        results = []
        async for msg in executor.execute("ai", "hi", "sess1", "/tmp"):
            results.append(json.loads(msg))

        assert len(results) == 2
        assert results[1]["content"] == "AI Response"
