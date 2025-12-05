"""
ARCHITECTURAL REASONING [DEMIURGE V3.2 - CONCURRENCY STABILIZATION]:

1.  **Uvicorn Bypass**: W `tests/test_gui_integration.py` zastąpiono wysokopoziomowe `uvicorn.run()` bezpośrednim uruchomieniem `Server.serve()` w dedykowanej pętli `asyncio`. Rozwiązuje to błąd `TypeError: ... got an unexpected keyword argument 'loop_factory'`, wynikający z konfliktu między spatchowanym przez `nest_asyncio` `asyncio.run` a wewnętrzną logiką Uvicorna.
2.  **Isolation**: `nest_asyncio` jest aplikowane TYLKO w `tests/test_tools.py`.
3.  **Global Cleanliness**: `conftest.py` nie dotyka pętli zdarzeń, co zapobiega efektom ubocznym w innych testach.

AUTHOR: Lead System Architect (AI)
VERSION: 5.1.2-STABLE
"""

import base64
import hashlib
import os
import sys
from pathlib import Path

# ==============================================================================
#  SOURCE OF TRUTH (RAW ASSETS)
# ==============================================================================

_RAW_SOURCE = {
    # --- CONFIGURATION ---
    "pyproject.toml": """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "regislite-core"
version = "5.1.2"
description = "Autonomiczny System Naprawczy (God Mode Refactor)"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "httpx>=0.26.0",
    "python-dotenv>=1.0.1",
    "tenacity>=8.2.0",
    "jinja2>=3.1.3",
    "aiofiles>=23.2.1",
    "nest_asyncio>=1.6.0"
]

[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "playwright>=1.41.0"
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["."]
filterwarnings = ["ignore::DeprecationWarning"]
""",

    "requirements.txt": """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
httpx>=0.26.0
python-dotenv>=1.0.1
tenacity>=8.2.0
jinja2>=3.1.3
aiofiles>=23.2.1
nest_asyncio>=1.6.0
playwright>=1.41.0
""",

    ".gitignore": """__pycache__/
*.pyc
*.pyo
*.pyd
.env
.env.local
venv/
.venv/
workspace/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.log
.DS_Store
.vscode/
.idea/
test-results/
""",

    # --- SRC: CORE ---
    "src/__init__.py": "",
    "src/core/__init__.py": "",

    "src/core/config.py": """import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    \"\"\"Konfiguracja aplikacji oparta na Pydantic v2.\"\"\"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App Info
    APP_NAME: str = "RegisLite GodMode"
    VERSION: str = "5.1.2"
    DEBUG: bool = False

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    WORKSPACE_DIR: Path = BASE_DIR / "workspace"

    # Security & AI
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    AI_MODEL: str = "gpt-4o-mini"

    # Limits
    MAX_FILE_SIZE_MB: int = 50
    MAX_ITERATIONS: int = 5

@lru_cache
def get_settings() -> Settings:
    return Settings()
""",

    "src/core/logger.py": """import logging
import sys
from src.core.config import get_settings

settings = get_settings()

def setup_logging():
    \"\"\"Konfiguracja loggera.\"\"\"
    logger = logging.getLogger("regislite")
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logging()
""",

    # --- SRC: DOMAIN ---
    "src/domain/__init__.py": "",

    "src/domain/schemas.py": """from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

class WSMessage(BaseModel):
    \"\"\"Model wiadomości WebSocket.\"\"\"
    type: Literal["log", "progress", "result", "error"]
    content: str
    meta: dict[str, Any] = Field(default_factory=dict)

class UploadResponse(BaseModel):
    session_id: str
    message: str
    workspace_path: str

class HealthCheck(BaseModel):
    status: str
    version: str
    mode: str
""",

    "src/domain/prompts.py": "\"\"\"\nCentralny magazyn promptów.\n\"\"\"\n\nSYSTEM_PROMPT = \"\"\"\nJesteś ARCHITEKTEM SYSTEMOWYM i DEVELOPEREM (RegisLite AI).\nTwój cel: Autonomiczna naprawa i analiza kodu.\n\nPROTOKÓŁ DZIAŁANIA (Skeleton-of-Thought):\n1. SKELETON: Zdefiniuj krótki plan zmian.\n2. DEBATE: (Wewnętrzna symulacja) Architekt vs Hacker vs PM.\n3. SOLUTION: Podaj gotowy kod w formacie blokowym.\n\nFORMAT ODPOWIEDZI KODU:\nFILE: <sciezka_wzgledna>\n\"\"\"\n"
}

def deploy():
    print("🚀 INITIATING DEPLOYMENT SEQUENCE (V2)...")
    for file_path, content in _RAW_SOURCE.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # print(f"📄 Writing {file_path}...")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        if not path.exists():
            print(f"❌ FAILED to write {file_path}")
            sys.exit(1)

    print("✅ DEPLOYMENT V2 COMPLETE.")

if __name__ == "__main__":
    deploy()
