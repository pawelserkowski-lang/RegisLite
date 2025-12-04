# config/env_config.py
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    REGISLITE ENVIRONMENT CONFIGURATION                       ║
║                                                                              ║
║  ZASADA NADRZĘDNA: WSZYSTKIE KLUCZE API ZAWSZE Z WINDOWS ENV VARS!         ║
║                                                                              ║
║  Hierarchia źródeł (w kolejności priorytetu):                               ║
║  1. Windows Environment Variables (System/User)                             ║
║  2. .env file (fallback dla developmentu)                                   ║
║  3. Raise ValueError jeśli brak klucza WYMAGANEGO                           ║
║                                                                              ║
║  Użycie:                                                                     ║
║    from config.env_config import get_api_key, Config                        ║
║    openai_key = get_api_key("OPENAI_API_KEY", required=True)               ║
║    # lub:                                                                    ║
║    config = Config()                                                         ║
║    openai_key = config.OPENAI_API_KEY                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# KROK 1: Załaduj .env jako fallback
# ══════════════════════════════════════════════════════════════════════════════

# Znajdź .env w root projektu
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=False)  # override=False = Windows ENV ma priorytet!
    logger.info(f"✓ Załadowano .env z: {ENV_FILE}")
else:
    logger.warning(f"⚠ Brak pliku .env w: {ENV_FILE}")


# ══════════════════════════════════════════════════════════════════════════════
# KROK 2: Funkcja pobierająca klucze (GŁÓWNA LOGIKA)
# ══════════════════════════════════════════════════════════════════════════════

def get_api_key(
    key_name: str,
    required: bool = True,
    default: Optional[str] = None,
    description: str = ""
) -> Optional[str]:
    """
    Pobiera klucz API z Windows Environment Variables.

    ZASADA: ZAWSZE najpierw Windows ENV, potem .env, na końcu default.

    Args:
        key_name: Nazwa zmiennej środowiskowej (np. "OPENAI_API_KEY")
        required: Czy klucz jest wymagany? (ValueError jeśli brak)
        default: Wartość domyślna (jeśli nie required)
        description: Opis do błędu (pomocne dla użytkownika)

    Returns:
        Wartość klucza lub None

    Raises:
        ValueError: Jeśli required=True i klucz nie istnieje

    Examples:
        >>> openai = get_api_key("OPENAI_API_KEY", required=True)
        >>> github = get_api_key("GITHUB_TOKEN", required=False, default="")
    """
    # Sprawdź Windows Environment (priorytet #1)
    value = os.environ.get(key_name)

    if value:
        source = "Windows ENV" if key_name not in os.environ else "ENV VAR"
        logger.info(f"✓ [{key_name}] załadowany z: {source}")
        return value

    # Sprawdź .env (priorytet #2 - już załadowany przez load_dotenv)
    value = os.getenv(key_name)
    if value:
        logger.info(f"✓ [{key_name}] załadowany z: .env file")
        return value

    # Użyj default (priorytet #3)
    if default is not None:
        logger.warning(f"⚠ [{key_name}] używam wartości domyślnej")
        return default

    # Brak klucza - error jeśli required
    if required:
        error_msg = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         BRAK WYMAGANEGO KLUCZA API!                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Klucz: {key_name}
{f'Opis: {description}' if description else ''}

JAK NAPRAWIĆ:

Opcja 1 - Windows Environment Variables (ZALECANE):
  1. Otwórz PowerShell jako Administrator:
     setx {key_name} "twoj-klucz-tutaj" /M

  2. Lub przez GUI:
     Win+R → sysdm.cpl → Advanced → Environment Variables
     Dodaj nową zmienną: {key_name} = twoj-klucz

  3. RESTART terminala/IDE po dodaniu!

Opcja 2 - Plik .env (development):
  Utwórz/edytuj plik .env w katalogu projektu:
  {key_name}=twoj-klucz-tutaj

WAŻNE: Windows ENV ma ZAWSZE priorytet nad .env!
"""
        logger.error(error_msg)
        raise ValueError(f"Brak wymaganego klucza: {key_name}")

    logger.warning(f"⚠ [{key_name}] brak wartości (opcjonalny klucz)")
    return None


# ══════════════════════════════════════════════════════════════════════════════
# KROK 3: Klasa Config (wygodny interface)
# ══════════════════════════════════════════════════════════════════════════════

class Config:
    """
    Centralna konfiguracja RegisLite.

    WSZYSTKIE klucze API są pobierane z Windows Environment Variables!

    Usage:
        config = Config()
        print(config.OPENAI_API_KEY)
        print(config.DEBUG)
    """

    def __init__(self):
        """Inicjalizacja - ładuje wszystkie klucze przy starcie."""
        logger.info("=" * 80)
        logger.info("🔧 REGISLITE CONFIG - Ładowanie konfiguracji...")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════════
        # API KEYS (ZAWSZE Z WINDOWS ENV!)
        # ═══════════════════════════════════════════════════════════

        self.OPENAI_API_KEY = get_api_key(
            "OPENAI_API_KEY",
            required=True,
            description="Klucz do OpenAI API (GPT-4/o3-mini)"
        )

        # Przyszłe integracje (opcjonalne)
        self.ANTHROPIC_API_KEY = get_api_key(
            "ANTHROPIC_API_KEY",
            required=False,
            description="Klucz do Anthropic Claude (opcjonalny)"
        )

        self.GITHUB_TOKEN = get_api_key(
            "GITHUB_TOKEN",
            required=False,
            description="GitHub Personal Access Token (opcjonalny)"
        )

        self.GOOGLE_API_KEY = get_api_key(
            "GOOGLE_API_KEY",
            required=False,
            description="Google Cloud API Key (opcjonalny)"
        )

        # ═══════════════════════════════════════════════════════════
        # APP SETTINGS (z env vars lub defaults)
        # ═══════════════════════════════════════════════════════════

        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
        self.MAX_ZIP_SIZE_MB = int(os.getenv("MAX_ZIP_SIZE_MB", "50"))
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.SHELL_TIMEOUT = int(os.getenv("SHELL_TIMEOUT", "30"))

        # ═══════════════════════════════════════════════════════════
        # PATHS
        # ═══════════════════════════════════════════════════════════

        self.WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "workspace"))
        self.BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "workspace/backups"))

        # Utwórz foldery jeśli nie istnieją
        self.WORKSPACE_DIR.mkdir(exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("✅ Konfiguracja załadowana pomyślnie!")
        logger.info("=" * 80)
        self._print_summary()

    def _print_summary(self):
        """Wyświetl podsumowanie konfiguracji."""
        logger.info("\n📋 PODSUMOWANIE KONFIGURACJI:")
        logger.info(f"   OpenAI Key: {'✓ SET' if self.OPENAI_API_KEY else '✗ MISSING'}")
        logger.info(
            f"   Anthropic Key: {'✓ SET' if self.ANTHROPIC_API_KEY else '○ Optional'}"
        )
        logger.info(
            f"   GitHub Token: {'✓ SET' if self.GITHUB_TOKEN else '○ Optional'}"
        )
        logger.info(f"   Debug Mode: {self.DEBUG}")
        logger.info(f"   Max Iterations: {self.MAX_ITERATIONS}")
        logger.info(f"   OpenAI Model: {self.OPENAI_MODEL}")
        logger.info(f"   Workspace: {self.WORKSPACE_DIR}")
        logger.info("")

    def to_dict(self) -> Dict[str, Any]:
        """Eksportuj config jako dict (bez sekretów!)."""
        return {
            "has_openai_key": bool(self.OPENAI_API_KEY),
            "has_anthropic_key": bool(self.ANTHROPIC_API_KEY),
            "has_github_token": bool(self.GITHUB_TOKEN),
            "debug": self.DEBUG,
            "max_iterations": self.MAX_ITERATIONS,
            "max_zip_size_mb": self.MAX_ZIP_SIZE_MB,
            "openai_model": self.OPENAI_MODEL,
            "shell_timeout": self.SHELL_TIMEOUT,
            "workspace_dir": str(self.WORKSPACE_DIR),
        }

    def validate(self) -> bool:
        """
        Waliduj czy wszystkie WYMAGANE klucze są ustawione.

        Returns:
            True jeśli config jest poprawny

        Raises:
            ValueError jeśli brakuje wymaganych kluczy
        """
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY jest wymagany!")

        if self.MAX_ITERATIONS < 1:
            raise ValueError("MAX_ITERATIONS musi być >= 1")

        if self.MAX_ZIP_SIZE_MB < 1:
            raise ValueError("MAX_ZIP_SIZE_MB musi być >= 1")

        logger.info("✅ Walidacja konfiguracji: OK")
        return True


# ══════════════════════════════════════════════════════════════════════════════
# KROK 4: Singleton Instance (lazy loading)
# ══════════════════════════════════════════════════════════════════════════════

_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Pobierz globalną instancję Config (singleton).

    Returns:
        Config instance

    Example:
        >>> from config.env_config import get_config
        >>> config = get_config()
        >>> print(config.OPENAI_API_KEY)
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


# ══════════════════════════════════════════════════════════════════════════════
# KROK 5: Helper do ustawiania Windows ENV (dla convenience)
# ══════════════════════════════════════════════════════════════════════════════

def set_windows_env(key: str, value: str, user_level: bool = True) -> bool:
    """
    Ustaw Windows Environment Variable programowo.

    Args:
        key: Nazwa zmiennej
        value: Wartość
        user_level: True = User, False = System (wymaga admin)

    Returns:
        True jeśli sukces

    Note:
        Wymaga restartu aplikacji/terminala po ustawieniu!
    """
    import subprocess

    scope = "User" if user_level else "Machine"

    try:
        cmd = f'setx {key} "{value}" {"" if user_level else "/M"}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"✓ Ustawiono {key} w Windows ENV ({scope})")
            logger.warning("⚠ RESTART wymagany! Uruchom ponownie terminal/aplikację")
            return True
        else:
            logger.error(f"✗ Błąd: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"✗ Nie udało się ustawić {key}: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# KROK 6: Utility do wyświetlania wszystkich ENV vars
# ══════════════════════════════════════════════════════════════════════════════

def list_env_vars(filter_prefix: str = "") -> Dict[str, str]:
    """
    Listuj wszystkie zmienne środowiskowe (filtrowane opcjonalnie).

    Args:
        filter_prefix: Pokaż tylko zmienne zaczynające się od tego prefiksu

    Returns:
        Dict z nazwami i wartościami

    Example:
        >>> list_env_vars("OPENAI")  # Pokaż wszystkie OPENAI_*
    """
    env_vars = {}
    for key, value in os.environ.items():
        if not filter_prefix or key.startswith(filter_prefix):
            # Ukryj sekrety (pokaż tylko pierwsze 10 znaków)
            if any(secret in key.upper() for secret in [
                "KEY", "TOKEN", "SECRET", "PASSWORD"
            ]):
                display_value = value[:10] + "..." if len(value) > 10 else value
            else:
                display_value = value
            env_vars[key] = display_value

    return env_vars


# ══════════════════════════════════════════════════════════════════════════════
# CLI Tool dla debugowania
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI tool do testowania konfiguracji."""
    import argparse

    parser = argparse.ArgumentParser(description="RegisLite Config Manager")
    parser.add_argument("--test", action="store_true", help="Testuj konfigurację")
    parser.add_argument(
        "--list",
        type=str,
        nargs="?",
        const="",
        help="Listuj ENV vars (opcjonalny prefix)"
    )
    parser.add_argument(
        "--set",
        type=str,
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Ustaw Windows ENV var"
    )

    args = parser.parse_args()

    if args.test:
        print("\n🧪 TESTOWANIE KONFIGURACJI...\n")
        try:
            config = Config()
            config.validate()
            print("\n✅ Konfiguracja POPRAWNA!")
            print("\n📊 Szczegóły:")
            for key, val in config.to_dict().items():
                print(f"   {key}: {val}")
        except Exception as e:
            print(f"\n❌ BŁĄD: {e}")
            sys.exit(1)

    elif args.list is not None:
        print(f"\n📋 Zmienne środowiskowe (prefix: '{args.list}'):\n")
        env_vars = list_env_vars(args.list)
        for key, val in sorted(env_vars.items()):
            print(f"   {key} = {val}")

    elif args.set:
        key, value = args.set
        print(f"\n🔧 Ustawiam {key}...")
        if set_windows_env(key, value):
            print("✅ Sukces! Pamiętaj o restarcie terminala!")
        else:
            print("❌ Błąd podczas ustawiania")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
