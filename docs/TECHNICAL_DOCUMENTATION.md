# Dokumentacja Techniczna Systemu Jules (RegisLite) v5.0.0

## 1. Wstęp

**Jules (RegisLite)** to zaawansowany system autonomicznej naprawy kodu z interfejsem WebSocket, działający w wersji 5.0.0 (Sentient Edition). Aplikacja służy jako inteligentny agent deweloperski, zdolny do analizowania, debugowania i naprawiania kodu w czasie rzeczywistym.

Główne cechy systemu:
- **Autonomia**: Zdolność do samodzielnego podejmowania decyzji o naprawach (tryb `autonomous` vs `interactive`).
- **Multi-Model AI**: Integracja z Google Gemini (priorytet) oraz OpenAI GPT-4 (fallback).
- **Architektura Agentowa**: Wykorzystanie metodyki "Jules Extension Auditor v4.0" z podziałem na role (Architekt, Hacker, PM).
- **Interfejs czasu rzeczywistego**: Komunikacja przez WebSocket.

---

## 2. Architektura Systemu

System oparty jest na frameworku **FastAPI** i wykorzystuje architekturę asynchroniczną.

### Schemat Komponentów

```mermaid
graph TD
    User[Użytkownik / CLI] -->|WebSocket| WS[Endpoint WebSocket /ws/{id}]
    WS -->|Handshake| Signaling[src/rtc/signaling.py]
    Signaling -->|Analiza Intencji| Router[src/ai/model_client.py]
    Router -->|Decyzja| ToolExec[src/rtc/tool_executor.py]

    ToolExec -->|Shell| ShellTool[Bash Executor]
    ToolExec -->|Python| PyTool[Python REPL]
    ToolExec -->|File IO| FileTool[File Manager]
    ToolExec -->|AI Chat| AI[Gemini / OpenAI]

    ToolExec -->|Wynik| Signaling
    Signaling -->|JSON Response| WS
    WS --> User
```

### Kluczowe Moduły

1.  **`src/main.py`**: Punkt wejścia aplikacji. Konfiguruje serwer FastAPI, CORS, obsługę plików statycznych oraz endpointy HTTP (`/health`, `/upload`) i WebSocket.
2.  **`src/rtc/signaling.py`**: Zarządza logiką komunikacji. Odbiera surowe komendy, przekazuje je do analizy intencji (`classify_intent`) i deleguje wykonanie do `ToolExecutor`.
3.  **`src/ai/model_client.py`**: Klient AI obsługujący modele językowe.
    -   **Priorytetyzacja**: Najpierw próbuje użyć `Google Gemini` (taniej/szybciej), w przypadku błędu przełącza się na `OpenAI`.
    -   **Router Intencji**: Klasyfikuje zapytania użytkownika na komendy (Shell, Python) lub rozmowę (AI), używając regexów (Fast Path) lub LLM (Slow Path).
4.  **`src/config/env_config.py`**: Centralny menedżer konfiguracji. Wymusza priorytet zmiennych środowiskowych systemu (Windows ENV) nad plikiem `.env`.

---

## 3. Metodyka Agentowa (Jules Extension Auditor v4.0)

Projekt wykorzystuje specyficzną metodykę pracy agenta zdefiniowaną w pliku `GEMINI.md`. Jest to "Source of Truth" (SoT) dla zachowania AI.

### Skeleton-of-Thought (SoT) z Multi-Agent Debate

Proces rozwiązywania problemów przebiega w trzech fazach:

1.  **SKELETON (Szkielet)**: Natychmiastowe wygenerowanie planu działania, aby zminimalizować opóźnienie (latency).
2.  **DEBATA (Multi-Agent Debate)**: Wewnętrzna symulacja dyskusji między trzema personami:
    -   **Architekt (The Idealist)**: Dba o czystość kodu (Clean Code), wzorce projektowe.
    -   **Hacker (The Cynic)**: Szuka luk bezpieczeństwa, wycieków pamięci, błędów logicznych.
    -   **PM (The Pragmatist)**: Decyduje o priorytetach, kosztach i czasie naprawy (Time-to-fix).
3.  **ROZWIĄZANIA**: Generowanie finalnych, gotowych do wklejenia fragmentów kodu.

Zasada: **NO-INTERRUPTION MODE**. Agent nie dopytuje użytkownika o szczegóły, lecz zakłada najbardziej prawdopodobny scenariusz i działa.

---

## 4. Instalacja i Konfiguracja

### Wymagania
- Python 3.10+
- Klucze API: Google Gemini (`GEMINI_KEY`) i/lub OpenAI (`OPENAI_API_KEY`).

### Zmienne Środowiskowe
Konfiguracja zarządzana jest przez `src/config/env_config.py`.

Priorytety:
1.  **Windows Environment Variables** (System/User) - Najwyższy priorytet.
2.  **Plik `.env`** - Fallback dla środowiska deweloperskiego.

Kluczowe zmienne:
- `GEMINI_KEY`: Klucz API Google (Wymagany dla domyślnego trybu).
- `OPENAI_API_KEY`: Klucz API OpenAI (Fallback).
- `WORKSPACE_DIR`: Katalog roboczy dla sesji (domyślnie `./workspace`).
- `DEBUG`: Tryb debugowania (`True`/`False`).

### Uruchomienie

1.  **Setup**:
    Uruchom skrypt instalacyjny (Linux/Bash):
    ```bash
    ./setup.sh
    ```
    Skrypt utworzy wirtualne środowisko (`venv`), zainstaluje zależności z `requirements.txt` i uruchomi testy.

2.  **Start serwera**:
    ```bash
    python run.py
    ```
    Serwer wystartuje na `http://0.0.0.0:8000`.

---

## 5. Struktura Katalogów

```text
.
├── docs/                   # Dokumentacja projektu
├── src/                    # Kod źródłowy
│   ├── ai/                 # Logika AI (model_client, prompty)
│   ├── config/             # Konfiguracja (env_config)
│   ├── debugger/           # Narzędzia do autonomicznego debugowania
│   ├── rtc/                # Logika WebSocket i sterowanie narzędziami
│   ├── services/           # Narzędzia systemowe (file_tool, python_tool)
│   └── main.py             # Entry point FastAPI
├── tests/                  # Testy jednostkowe (pytest)
├── GEMINI.md               # Definicja zachowań agenta (System Prompt)
├── gemini-extension.json   # Konfiguracja rozszerzenia Gemini CLI
├── run.py                  # Skrypt uruchomieniowy
└── setup.sh                # Skrypt instalacyjny
```

---

## 6. API Reference

### HTTP Endpoints

-   `GET /health`
    -   Zwraca status systemu, tryb pracy i aktywny model.
    -   Przykład: `{"status": "operational", "mode": "async", "model": "gemini-1.5-flash"}`

-   `POST /upload`
    -   Przyjmuje plik `.zip` z kodem do analizy.
    -   Tworzy sesję i wypakowuje kod do `workspace/{session_id}`.

### WebSocket Protocol

-   URL: `ws://localhost:8000/ws/{client_id}`
-   Komunikacja JSON.

**Format wiadomości od serwera:**
```json
{
  "type": "log" | "progress" | "error",
  "content": "Treść wiadomości...",
  "meta": {
    "duration": "0.45s",
    "model": "gemini-1.5-flash"
  }
}
```

---

## 7. Rozwój i Debugowanie

### Dodawanie nowych narzędzi
Narzędzia znajdują się w `src/services/`. Aby dodać nowe narzędzie:
1.  Stwórz klasę/funkcję w `src/services/`.
2.  Zarejestruj ją w `src/rtc/tool_executor.py`.
3.  Zaktualizuj prompt routera w `src/ai/prompts.py` (jeśli wymagane).

### Testowanie
Używamy `pytest`.
```bash
pytest tests/
```
Testy obejmują:
- `tests/test_health.py`: Sprawdzenie endpointów API.
- `tests/test_ai.py`: Mockowane testy logiki AI.
- `tests/test_tools.py`: Testy narzędzi plikowych i systemowych.
