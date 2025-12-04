# Jules (RegisLite)

Autonomiczny system naprawy kodu i debugowania wspierany przez agenta AI (Gemini/OpenAI).
Zaprojektowany jako rozszerzenie do Gemini CLI, ale działający również jako samodzielny serwer WebSocket.

## 📚 Dokumentacja Techniczna

Pełna dokumentacja techniczna znajduje się w pliku [docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md).

Obejmuje ona:
*   Szczegółowy opis architektury systemu.
*   Metodykę Agentową (Skeleton-of-Thought + Multi-Agent Debate).
*   Kompletny przewodnik konfiguracji.
*   API Reference (HTTP & WebSocket).

## 🚀 Szybki Start

### Wymagania
* Python 3.10+
* Klucz API OpenAI (`OPENAI_API_KEY`)

### Instalacja i Uruchomienie

1.  **Sklonuj repozytorium i wejdź do katalogu:**
    ```bash
    git clone https://github.com/gemini-cli-extensions/jules
    cd jules
    ```

2.  **Stwórz wirtualne środowisko i zainstaluj zależności:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Skonfiguruj zmienne środowiskowe:**
    Stwórz plik `.env` (na bazie `.env.example`):
    ```ini
    OPENAI_API_KEY=sk-twoj-klucz
    WORKSPACE_DIR=workspace
    ```

4.  **Uruchom serwer:**
    ```bash
    python run.py
    ```
    Serwer wystartuje na `http://localhost:8000`.

## 🛠️ Workflow: Review and Merge

Jules używa modelu "Plan -> Weryfikacja -> Wykonanie".

1.  **Upload Projektu**:
    Wyślij plik `.zip` z kodem na endpoint `/upload` lub użyj dashboardu.
2.  **Start Sesji**:
    Połącz się przez WebSocket (`ws://localhost:8000/ws/{session_id}`).
3.  **Interakcja**:
    *   Opisz problem (np. "Napraw błąd w pliku X").
    *   Jules przedstawi **Plan Działania**.
4.  **Zatwierdzenie i Wykonanie**:
    *   Jules samodzielnie weryfikuje pliki.
    *   Wprowadza zmiany.
    *   Uruchamia testy (jeśli poprosisz).
5.  **Review**:
    *   Sprawdź zmienione pliki w katalogu `workspace/{session_id}`.

## 🏗️ Architektura

Projekt został zrefaktoryzowany do modułowej struktury (Separation of Concerns):

*   `src/ai/`: Logika AI, klient OpenAI, Prompty.
*   `src/rtc/`: Obsługa WebSocket, zarządzanie sesją (`SessionManager`), wykonywanie narzędzi (`ToolExecutor`).
*   `src/config/`: Konfiguracja i definicje błędów (`errors.py`).
*   `tests/`: Testy jednostkowe i integracyjne.

### Główne komponenty:
*   **Signaling**: Router WebSocket.
*   **Intent Classifier**: Szybki router (Regex + LLM Fallback) decydujący o użyciu narzędzia (`sh`, `py`, `file`, `ai`).
*   **Tool Executor**: Bezpieczne wykonywanie komend i operacji na plikach.

## 🧪 Testowanie

Uruchom testy za pomocą `pytest`:
```bash
python -m pytest tests/
```
