import sys
import os
from pathlib import Path
import pytest

# 1. Set environment variables BEFORE any imports that might use them
os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
os.environ["GEMINI_API_KEY"] = "dummy-key-for-testing"
os.environ["GEMINI_KEY"] = "dummy-key-for-testing"

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """
    Ensure env vars are also set via monkeypatch for test isolation,
    although the global set above handles import-time requirements.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key-for-testing")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-testing")
    monkeypatch.setenv("GEMINI_KEY", "dummy-key-for-testing")
