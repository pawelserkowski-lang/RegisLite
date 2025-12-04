# Dokumentacja Techniczna Systemu Jules (RegisLite) v6.0.0

## 1. Wstęp

**Jules (RegisLite)** to zaawansowany system autonomicznej naprawy kodu z interfejsem WebSocket, działający w wersji 6.0.0 (Sentient Edition / CyberOmni). Aplikacja służy jako inteligentny agent deweloperski, zdolny do analizowania, debugowania i naprawiania kodu w czasie rzeczywistym.

Główne cechy systemu:
- **Autonomia**: Zdolność do samodzielnego podejmowania decyzji o naprawach (tryb `autonomous` vs `interactive`).
- **Multi-Model AI**: Integracja z Google Gemini (priorytet) oraz OpenAI GPT-4 (fallback).
- **Architektura Agentowa**: Wykorzystanie metodyki "Jules Extension Auditor v4.0" z podziałem na role (Architekt, Hacker, PM).
- **Interfejs czasu rzeczywistego**: Komunikacja przez WebSocket z nowoczesnym GUI "Cyber Green".

---

## 2. Architektura Systemu

System oparty jest na frameworku **FastAPI** i wykorzystuje architekturę asynchroniczną.

### Schemat Komponentów

```mermaid
graph TD
    User[Użytkownik / GUI] -->|WebSocket| WS[Endpoint WebSocket /ws/{id}]
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
2.  **`src/rtc/signaling.py`**: Zarządza logiką komunikacji. Odbiera surowe komendy (w tym komendę "Autonaprawa"), przekazuje je do analizy intencji (`classify_intent`) i deleguje wykonanie do `ToolExecutor`.
3.  **`src/ai/model_client.py`**: Klient AI obsługujący modele językowe.
    -   **Priorytetyzacja**: Najpierw próbuje użyć `Google Gemini` (taniej/szybciej), w przypadku błędu przełącza się na `OpenAI`.
    -   **Router Intencji**: Klasyfikuje zapytania użytkownika na komendy (Shell, Python) lub rozmowę (AI).
4.  **`src/config/env_config.py`**: Centralny menedżer konfiguracji. Wymusza priorytet zmiennych środowiskowych systemu (Windows ENV) nad plikiem `.env`.

---

## 3. Interfejs Użytkownika (GUI)

Aplikacja posiada interfejs webowy dostępny pod adresem głównym serwera.

- **Styl**: Cyber Green (Matrix/Terminal style).
- **Funkcjonalność**:
    - Upload projektów (.zip).
    - Terminal komend (WebSocket).
    - Przycisk **[ Autonaprawa ]**: Wysyła komendę "Przeprowadź pełną analizę i naprawę projektu." bezpośrednio przez kanał WebSocket, co uruchamia autonomiczną procedurę naprawczą.

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

### Uruchomienie

1.  **Setup**:
    Uruchom skrypt instalacyjny (Linux/Bash):
    ```bash
    ./setup.sh
    ```
    Skrypt utworzy wirtualne środowisko (`venv`), zainstaluje zależności i uruchomi testy.

2.  **Start Aplikacji**:
    Dostępne są dwie metody:
    - **Skrypt Startowy**: `./start_app.sh` (automatycznie aktywuje venv i uruchamia serwer).
    - **Skrót Pulpitowy**: `RegisLite.desktop` (można przenieść na pulpit).
    - **Bezpośrednio**: `python run.py`.

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
│   ├── static/             # Pliki frontend (dashboard.html)
│   └── main.py             # Entry point FastAPI
├── tests/                  # Testy jednostkowe i integracyjne
│   └── test_gui_integration.py # Testy E2E dla GUI (Playwright)
├── GEMINI.md               # Definicja zachowań agenta (System Prompt)
├── run.py                  # Skrypt uruchomieniowy (Python)
├── start_app.sh            # Skrypt uruchomieniowy (Bash wrapper)
└── RegisLite.desktop       # Skrót na pulpit
```

---

## 6. API Reference

### HTTP Endpoints

-   `GET /health`
    -   Zwraca status systemu.
-   `POST /upload`
    -   Przyjmuje plik `.zip`.
    -   Tworzy sesję.

### WebSocket Protocol

-   URL: `ws://localhost:8000/ws/{client_id}`
-   Komunikacja JSON.

**Autonaprawa:**
Wysłanie wiadomości tekstowej "Przeprowadź pełną analizę i naprawę projektu." inicjuje proces naprawy sterowany przez AI.

---

## 7. Testowanie

Projekt wykorzystuje `pytest` oraz `playwright` do testów integracyjnych GUI.

```bash
# Uruchomienie wszystkich testów
pytest tests/
```

Weryfikacja zmian w GUI wymaga uruchomienia skryptu `verify_theme.py` lub testów integracyjnych, które symulują interakcję użytkownika w przeglądarce.
