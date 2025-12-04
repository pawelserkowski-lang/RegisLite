# 🤖 RegisLite 4.5 - Polski AI Debugger

> **Lokalny agent AI do automatycznego debugowania i naprawiania kodu** 🥟

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📖 Spis Treści

- [🎯 Czym jest RegisLite?](#-czym-jest-regislite)
- [✨ Funkcje](#-funkcje)
- [🚀 Quick Start](#-quick-start)
- [📦 Architektura](#-architektura)
- [💻 Jak używać](#-jak-używać)
- [🔧 Konfiguracja](#-konfiguracja)
- [🧪 Rozwój](#-rozwój)
- [📝 Roadmapa](#-roadmapa)

---

## 🎯 Czym jest RegisLite?

RegisLite to **lokalny debugger AI**, który:
- 🔍 **Skanuje** projekty Python w poszukiwaniu błędów
- 🤖 **Używa GPT-4** do generowania poprawek
- ✅ **Automatycznie naprawia** kod
- 💾 **Tworzy backupy** przed zmianami
- 🔁 **Iteruje** aż do pełnej poprawności
- 💬 **Terminal WebSocket** z komendami `ai:`, `py:`, `sh:`, `file:`

**To jak ChatGPT dla Twojego kodu - tylko lepsze, bo naprawia go automatycznie!** 😎

---

## ✨ Funkcje

### 🎯 Core Features
- ✅ **Upload projektów** jako ZIP
- 🔍 **Automatyczne skanowanie** w poszukiwaniu błędów/FIXME
- 🤖 **AI-powered patching** (GPT-4/o3-mini)
- 📝 **Unified diff** format dla zmian
- 💾 **Automatyczne backupy** (`.bak` files)
- 🔁 **Pętla debugowania** (max 10 iteracji)

### 💻 Terminal WebSocket
- 🧠 `ai:prompt` - Zapytaj ChatGPT o cokolwiek
- 🐍 `py:code` - Wykonaj kod Python (sandboxed)
- 🖥️ `sh:command` - Uruchom komendy shell
- 📁 `file:action path` - Operacje na plikach (read/write/delete/list)

### 🔒 Bezpieczeństwo
- 🛡️ **Sandboxed Python execution** (AST validation)
- 📏 **Limit rozmiaru ZIP** (50MB)
- 🔐 **Environment variables** dla API keys
- ⏱️ **Timeout** dla shell commands (30s)

---

## 🚀 Quick Start

### 1️⃣ Wymagania

```bash
Python 3.11+
pip (package manager)
OpenAI API Key
```

### 2️⃣ Instalacja

```bash
# Sklonuj repo
git clone https://github.com/pawelserkowski-lang/RegisLite.git
cd RegisLite

# Utwórz virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Zainstaluj zależności
pip install -r requirements.txt
```

### 3️⃣ Konfiguracja

```bash
# Skopiuj przykładowy config
cp .env.example .env

# Edytuj .env i dodaj swój klucz OpenAI
# OPENAI_API_KEY=sk-proj-twoj-klucz-tutaj
```

### 4️⃣ Uruchomienie

```powershell
# Sposób 1: Użyj gotowego skryptu
.\run.ps1

# Sposób 2: Manualnie
uvicorn app:app --reload --port 8000
```

Otwórz przeglądarkę: **http://localhost:8000** 🎉

---

## 📦 Architektura

```
RegisLite/
├── app.py                      # 🚀 Główny serwer FastAPI
├── ai/
│   └── chatgpt_client.py      # 🤖 Klient OpenAI API
├── debugger/
│   ├── debugger_analyzer.py   # 🔍 Skanowanie projektu
│   ├── debugger_fix.py        # 🛠️ Generowanie patchy
│   ├── debugger_patcher.py    # ✂️ Aplikowanie zmian
│   └── debugger_loop.py       # 🔁 Główna pętla debuggera
├── rtc/
│   └── signaling.py           # 💬 WebSocket command handler
├── services/
│   ├── python_tool.py         # 🐍 Safe Python execution
│   └── file_tool.py           # 📁 File operations
├── static/
│   └── dashboard.html         # 🎨 UI (one-page app)
└── workspace/                  # 💾 Runtime data (sessions)
```

### 🔄 Przepływ Danych

```
1. Upload ZIP → /upload
   ↓
2. Extract → workspace/{session_id}/project/
   ↓
3. Start Debug → /debug/{session_id}
   ↓
4. Debug Loop (max 10x):
   - Skanuj pliki (FIXME detection)
   - Jeśli błędy → Generate patches (GPT)
   - Apply patches (with backups)
   - Repeat
   ↓
5. Output → workspace/{session_id}/output_fixed/
```

---

## 💻 Jak używać

### 📤 Upload i Debug

1. **Wybierz ZIP** z projektem Python
2. Kliknij **Upload ZIP**
3. Poczekaj na potwierdzenie sesji
4. Kliknij **Start Debug**
5. Obserwuj logi w czasie rzeczywistym
6. Pobierz naprawiony projekt z `workspace/{session}/output_fixed/`

### 💬 Terminal Interaktywny

Po uploadzie ZIP możesz używać terminala WebSocket:

```bash
# Zapytaj AI
ai:napisz funkcję do sortowania listy słowników

# Wykonaj Python
py:print([x**2 for x in range(10)])

# Uruchom shell
sh:dir
sh:git status

# Operacje na plikach
file:list .
file:read main.py
file:write test.txt Hello World!
file:delete temp.txt
```

---

## 🔧 Konfiguracja

### Environment Variables (`.env`)

```bash
# OpenAI API (WYMAGANE)
OPENAI_API_KEY=sk-proj-your-key-here

# Debug mode (opcjonalne)
DEBUG=True

# Max iterations (domyślnie 10)
MAX_ITERATIONS=10

# Model (gpt-4o-mini | gpt-4.1 | o3-mini)
OPENAI_MODEL=gpt-4o-mini
```

### Dostosowanie Debuggera

Edytuj `debugger/debugger_loop.py`:

```python
# Zmień heurystykę wykrywania błędów
errors = [f["path"] for f in files if "FIXME" in f["content"]]

# Dodaj własne reguły, np:
# - AST parsing
# - linting (pylint/flake8)
# - security checks
```

---

## 🧪 Rozwój

### 🏗️ Struktura dla Developerów

```python
# Dodaj nowy tool do terminala
# rtc/signaling.py

elif cmd.startswith("mytool:"):
    args = cmd[7:]
    result = my_custom_tool(args)
    return f"MyTool: {result}"
```

### 🧪 Testy (TODO)

```bash
# Uruchom testy (gdy zostaną dodane)
pytest tests/

# Coverage
pytest --cov=. tests/
```

### 📊 Health Check

```bash
curl http://localhost:8000/health

# Response:
{
  "status": "ok",
  "openai_configured": true,
  "workspace_exists": true,
  "version": "4.5-fixed"
}
```

---

## 📝 Roadmapa

### ✅ Zrobione (v4.5)
- ✅ Upload ZIP
- ✅ Auto-debug loop
- ✅ WebSocket terminal
- ✅ Safe Python exec
- ✅ File operations
- ✅ Backups

### 🚧 W Planach (v5.0)

#### 🎯 Core Improvements
- [ ] **AST-based error detection** (zamiast heurystyki)
- [ ] **Async GPT calls** (httpx zamiast requests)
- [ ] **Response caching** (Redis/SQLite)
- [ ] **Rate limiting** (max requests/min)
- [ ] **Session persistence** (SQLite DB)

#### 🧪 Testing & Quality
- [ ] **Unit tests** (pytest)
- [ ] **Integration tests** (TestClient)
- [ ] **Coverage >80%**
- [ ] **Type hints** (mypy validation)
- [ ] **Linting** (ruff + black)

#### 🎨 UI/UX
- [ ] **Real-time progress** (SSE/WebSocket)
- [ ] **Syntax highlighting** (CodeMirror)
- [ ] **Diff viewer** (before/after)
- [ ] **Download fixed ZIP**
- [ ] **History** (past sessions)

#### 🚀 Advanced Features
- [ ] **Multi-language support** (JS, Go, Java)
- [ ] **Git integration** (auto-commit, branches)
- [ ] **Plugin system** (custom tools)
- [ ] **Team features** (shared sessions)
- [ ] **Cloud deployment** (Docker, K8s)

### 🌟 Wizja (v6.0+)
- 🧠 **Multi-agent debugging** (specialized agents)
- 🔗 **CI/CD integration** (GitHub Actions)
- 📊 **Analytics dashboard** (metrics, insights)
- 🤝 **Collaboration** (real-time multi-user)
- 🌍 **SaaS version** (hosted service)

---

## 🐛 Known Issues

1. **WebSocket disconnect** - Odśwież stronę i wgraj ZIP ponownie
2. **Large ZIPs timeout** - Limit to 50MB, podziel projekt na mniejsze części
3. **GPT rate limits** - Dodaj retry logic lub użyj mniejszego modelu

---

## 🤝 Contributing

Chcesz pomóc? Super! 🎉

1. Fork repo
2. Utwórz branch (`git checkout -b feature/amazing-feature`)
3. Commit zmiany (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Otwórz Pull Request

**Guidelines:**
- Zachowaj PEP 8
- Dodaj testy do nowych funkcji
- Zaktualizuj README jeśli trzeba
- Bądź miły w komentarzach 😊

---

## 📜 License

MIT License - patrz [LICENSE](LICENSE)

**TL;DR:** Rób co chcesz, tylko zostaw credit! 😎

---

## 🙏 Credits

Stworzone z ❤️ i ☕ przez **@pawelserkowski-lang**

Technologie:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [OpenAI](https://openai.com/) - GPT models
- [Uvicorn](https://www.uvicorn.org/) - ASGI server
- Mnóstwo pierogów 🥟

---

## 📞 Kontakt

- 🐙 GitHub: [@pawelserkowski-lang](https://github.com/pawelserkowski-lang)
- 💬 Issues: [GitHub Issues](https://github.com/pawelserkowski-lang/RegisLite/issues)

---

## 🥟 Fun Fact

Ten projekt powstał po nocnej sesji kodowania zasilanej pierogami i kawą. Każdy commit to dowód, że polskie pierogi dają programistyczną inspirację! 🇵🇱

**Zbudujmy razem przyszłość AI-powered development!** 🚀

---

<div align="center">
  
### ⭐ Jeśli lubisz RegisLite, zostaw gwiazdkę! ⭐

**Made with 🥟 in Poland**

</div>