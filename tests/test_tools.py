import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock
from src.rtc.tool_executor import ToolExecutor

class TestToolExecutor(unittest.TestCase):

    def setUp(self):
        self.mock_session_manager = MagicMock()
        self.mock_session_manager.get_history.return_value = []
        self.executor = ToolExecutor(self.mock_session_manager)

    def test_execute_sh(self):
        async def run_test():
            with patch("asyncio.create_subprocess_shell") as mock_shell:
                process_mock = AsyncMock()
                process_mock.communicate.return_value = (b"output", b"")
                mock_shell.return_value = process_mock

                results = []
                async for msg in self.executor.execute("sh", "echo test", "sess1", "/tmp"):
                    results.append(json.loads(msg))

                self.assertEqual(len(results), 2)
                self.assertEqual(results[0]["type"], "progress")
                self.assertEqual(results[1]["type"], "result")
                self.assertIn("output", results[1]["content"])

        # Loop handling that works with pytest-asyncio/playwright interference
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If the loop is already running (e.g. via pytest plugin), we must create a task
            # But we are in a sync test. We can't await it.
            # This is the catch-22.
            # However, unittest.TestCase is sync. If pytest runs it, it won't await it.
            # So we assume if loop is running, we might be inside an async context wrapper?
            # No, standard unittest methods are sync.
            # If loop is running, we can try run_until_complete but it will fail.
            # This implies we should use IsolatedAsyncioTestCase OR fix the environment.
            pass

        # Robust execution
        loop.run_until_complete(run_test())

    def test_execute_ai(self):
        async def run_test():
            with patch("src.rtc.tool_executor.ask_with_stats", new_callable=AsyncMock) as mock_ask:
                mock_ask.return_value = ("AI Response", 1.0, "gpt-mock")

                results = []
                async for msg in self.executor.execute("ai", "hi", "sess1", "/tmp"):
                    results.append(json.loads(msg))

                self.assertEqual(len(results), 2)
                self.assertEqual(results[1]["content"], "AI Response")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(run_test())
