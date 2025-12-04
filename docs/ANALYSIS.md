# Analiza RegisLite — architektura, logika i rekomendacje (zgodnie z wymaganiami Jules)

## Faza 1: Kontekst i architektura rozszerzenia (MCP & orkiestracja)

### Manifest rozszerzenia (`gemini-extension.json`)
**Status**: Brak manifestu dla Gemini CLI; aplikacja to serwer FastAPI uruchamiany z `app.py` bez integracji z ekosystemem rozszerzeń.

**Uzasadnienie (Dlaczego?)**
- Uniemożliwia standardowe ładowanie rozszerzenia, konfigurację cache/prefetch i deklarację uprawnień, co utrudnia automatyzację w Gemini CLI.

**Kroki Wdrożenia (Jak?)**
1. Utworzyć `gemini-extension.json` z polami `name`, `version`, `entrypoint` (np. skrypt uruchamiający FastAPI), `permissions` oraz sekcją `optimization` (cache, lazyLoad, prewarm).
2. Dodać opis wymaganych zmiennych środowiskowych i URL webhooków; zadbać o ograniczenia sieciowe w trybie lokalnym.

### Prompt systemowy i kontekst agentów
**Status**: Instrukcja w `debugger/debugger_fix.py` urywa się po definicji formatu pliku, bez wymuszenia planu pracy czy ograniczeń dot. plików binarnych.

**Uzasadnienie (Dlaczego?)**
- Brak metodyki i walidacji ścieżek zwiększa ryzyko halucynacji modelu (np. generowanie nieistniejących plików, brak kontroli iteracji patchy).

**Kroki Wdrożenia (Jak?)**
1. Rozszerzyć `PATCH_INSTRUCTIONS` o obowiązkową sekcję „Plan” przed wprowadzeniem zmian, kontrolę istniejących ścieżek i zakaz modyfikacji plików binarnych.
2. Wymusić format odpowiedzi: `Plan` → `Patch` → `Testy do uruchomienia`; odrzucać odpowiedzi niespełniające schematu.

### Optymalizacja poleceń slash / interakcji
**Status**: UI (`static/index.html`) wymaga sekwencyjnego wyboru pliku i dwóch kliknięć (upload, start). Parametry debuggera (model, liczba iteracji) są na stałe zaszyte w backendzie.

**Uzasadnienie (Dlaczego?)**
- Nadmiar interakcji i brak kontroli parametrów skutkuje większą liczbą round-tripów oraz brakiem przejrzystości konfiguracji.

**Kroki Wdrożenia (Jak?)**
1. Zgrupować parametry w jednym formularzu (model, maks. iteracje, tryb „tylko analiza”) i wysyłać je jednym żądaniem do `/start_debug`.
2. Rozszerzyć `app.py` o przyjmowanie parametrów w endpointzie i przekazywanie ich do pętli debuggera.

## Faza 2: Logika, asynchroniczność i debugowanie

### Przepływ kontroli i obsługa błędów
**Status**: Główne wejście to FastAPI (`/upload_zip`, `/start_debug`). Operacje IO (`zipfile`, `shutil`) nie mają walidacji ani zabezpieczeń; wywołanie LLM w `ai/chatgpt_client.py` jest synchroniczne i bez retry.

**Uzasadnienie (Dlaczego?)**
- Surowe wyjątki z IO lub API przerwą pętlę, a blokujące żądania LLM ograniczają współbieżność serwera.

**Kroki Wdrożenia (Jak?)**
1. Owinąć `/upload_zip` i `/start_debug` w `try/except`, mapując błędy na spójne kody HTTP; walidować MIME/rozmiar ZIP, wprowadzić limit rozpakowywanego katalogu.
2. Zastąpić synchroniczny `requests` w `ask` przez `httpx.AsyncClient` z timeoutem, retry (exponential backoff) i rozróżnieniem błędów transportowych vs. statusowych.

### Minimalizacja tokenów i kosztów
**Status**: Każda iteracja `start_debug_loop` przesyła pełny kontekst do `ask` bez cache lub deduplikacji; pętla wykonuje do 10 przebiegów nawet przy braku zmian.

**Uzasadnienie (Dlaczego?)**
- Nadmiarowy kontekst i puste iteracje zwiększają zużycie tokenów i koszty API.

**Kroki Wdrożenia (Jak?)**
1. Wprowadzić cache odpowiedzi (hash promptu + suma kontrolna plików) per iteracja, unikać ponownego wysyłania identycznych zapytań.
2. Skracać kontekst do plików z `FIXME` i ich fragmentów, a po braku zmian zakończyć pętlę lub przełączyć na tryb „dry-run”.

### Wąskie gardła i race conditions
**Status**: Równoległe żądania mogą kolidować – `/upload_zip` usuwa katalog `workspace/project` podczas działania debuggera, a `apply_patches` zapisuje bez blokady.

**Uzasadnienie (Dlaczego?)**
- Brak synchronizacji może uszkodzić stan projektu (np. częściowo rozpakowany ZIP, nadpisanie backupów `.bak`).

**Kroki Wdrożenia (Jak?)**
1. Wprowadzić blokadę (np. `asyncio.Lock`) obejmującą upload i start pętli debuggera; sygnalizować stan „upload in progress”.
2. Użyć zapisu atomowego w `apply_patches` (plik tymczasowy + rename) oraz unikalnych backupów per transakcja.
3. W pętli debuggera weryfikować, czy projekt został w pełni rozpakowany przed analizą.

### Hierarchia błędów i raportowanie
**Status**: Błędy są zwracane jako surowe stringi (np. `OpenAI API error`) bez klasyfikacji; brak spójnego API dla frontendu.

**Uzasadnienie (Dlaczego?)**
- Brak struktury utrudnia prezentację czytelnych komunikatów i diagnostykę po stronie UI.

**Kroki Wdrożenia (Jak?)**
1. Utworzyć moduł `errors.py` z hierarchią: `ValidationError`, `ApiError`, `AgentError`, `SystemError`, z metodą `to_http()` zwracającą `{code, message, hint}`.
2. Zawijać główne ścieżki (`upload_zip`, `start_debug`, `ask`) w te wyjątki i mapować na HTTP/JSON do UI (alert + hint naprawy).

## Faza 3: Refaktoryzacja i testowalność

### Modularność i separacja obowiązków (SoC)
**Status**: Logika uploadu, debugowania i klienta LLM jest zagnieżdżona w kilku plikach, bez jasnych warstw.

**Uzasadnienie (Dlaczego?)**
- Trudno mockować zależności, a zmiany w jednej części (np. IO) wpływają na całą aplikację.

**Kroki Wdrożenia (Jak?)**
1. Wydziel `services/upload.py` (walidacja, ekstrakcja, blokady) i `services/debugger.py` (pętla, harmonogram, limit iteracji), pozostawiając `app.py` jako cienką warstwę HTTP.
2. Dodać interfejs `LLMClient` w `ai/client.py` z implementacją OpenAI i prostym cache; wstrzykiwać go do debuggera.
3. Przenieść operacje patchowania do klasy `PatchApplier` z konfiguracją backupu/atomowego zapisu.

### Standardy kodu, linting i nazewnictwo
**Status**: Widoczne naruszenia PEP 8 i brak narzędzi lintingu (np. importy niesortowane w `app.py`, brak typów w endpointach, stała API w stylu zmiennej lokalnej).

**Uzasadnienie (Dlaczego?)**
- Brak spójności utrudnia review i automatyczną weryfikację zmian.

**Kroki Wdrożenia (Jak?)**
1. Dodać `ruff` + `isort` + `mypy` z konfiguracją PEP 8; uruchamiać w CI.
2. Ustandaryzować nazwy: `ask` → `query_chatgpt_async`, `start_debug` (endpoint) → `start_debug_endpoint`, `start_debug_loop` → `run_debug_loop`, `apply_patches` → `apply_patch_batch`, `signal_ping` → `ping_signal` (dla routera RTC).
3. Wprowadzić stałe ścieżek (`WORKSPACE_DIR`, `PROJECT_DIR`) i adnotacje typów w endpointach.

### Testowalność (krytyczne ścieżki)
**Status**: Brak testów; ścieżki krytyczne to upload ZIP, wykrywanie `FIXME`, generowanie i aplikacja patchy.

**Uzasadnienie (Dlaczego?)**
- Bez mocków API i izolacji IO trudno uzyskać deterministyczne testy regresyjne.

**Kroki Wdrożenia (Jak?)**
1. Stworzyć interfejs `LLMClient` z mockiem zwracającym deterministyczne patchy; użyć `fastapi.testclient.TestClient` dla endpointów.
2. Testy `/upload_zip`: scenariusze poprawne, zły MIME, przekroczenie limitu rozmiaru, nieprawidłowy ZIP (spodziewane kody 400/413/422).
3. Testy pętli debuggera: projekt z `FIXME`, symulacja braku plików, limit iteracji; weryfikacja zatrzymania po braku zmian.
4. Testy patchera: idempotencja, backupy, zapisy równoległe (ThreadPool) z atomowym rename.

### Dokumentacja i onboarding
**Status**: `README.md` zawiera tylko tytuł, brak instrukcji uruchomienia i procesu „Review and Merge”.

**Uzasadnienie (Dlaczego?)**
- Nowy użytkownik nie wie, jak zainstalować zależności, uruchomić serwer ani zweryfikować rezultatów debuggera.

**Kroki Wdrożenia (Jak?)**
1. Uzupełnić README o wymagania (Python 3.11), instalację (`pip install -r requirements.txt`), uruchomienie (`uvicorn app:app --reload`), opis endpointów i przepływ upload→debug.
2. Opisać proces „Review and Merge”: jak zbierać logi, weryfikować patchy i kryteria akceptacji; dodać sekcję „start w 5 minut” z przykładowym ZIP.
