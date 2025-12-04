import pytest
from unittest.mock import patch, AsyncMock
from src.ai.chatgpt_client import classify_intent

@pytest.mark.asyncio
async def test_classify_intent_regex_sh():
    # Test shell regex fast path
    result, duration, model = await classify_intent("/sh git status")
    assert result == {"tool": "sh", "args": "git status"}
    assert model == "regex"

@pytest.mark.asyncio
async def test_classify_intent_regex_ls():
    # Test ls regex fast path
    result, duration, model = await classify_intent("ls -la")
    assert result == {"tool": "sh", "args": "ls -la"}
    assert model == "regex"

@pytest.mark.asyncio
async def test_classify_intent_regex_py():
    # Test python regex fast path
    result, duration, model = await classify_intent("/py print('hello')")
    assert result == {"tool": "py", "args": "print('hello')"}
    assert model == "regex"

@pytest.mark.asyncio
async def test_classify_intent_llm_fallback():
    # Test LLM fallback
    with patch("src.ai.chatgpt_client._call_gpt_with_retry", new_callable=AsyncMock) as mock_gpt:
        mock_gpt.return_value = ('{"tool": "ai", "args": "joke"}', 1.0, "gpt-test")

        result, duration, model = await classify_intent("Tell me a joke")

        assert result == {"tool": "ai", "args": "joke"}
        assert model == "gpt-test"
        mock_gpt.assert_called_once()
