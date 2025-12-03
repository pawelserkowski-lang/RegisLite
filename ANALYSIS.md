# Analiza RegisLite (w kontekście wymagań z promptu Jules)

## Faza 1: Kontekst i architektura rozszerzenia

### Manifest rozszerzenia
- **Status:** W repozytorium brak pliku `gemini-extension.json`; aplikacja to serwer FastAPI uruchamiany lokalnie (`app.py`).
- **Rekomendacja:** Dodać manifest rozszerzenia opisujący punkt wejścia, uprawnienia i bufory kontekstu dla Gemini CLI, aby ułatwić ładowanie i konfigurację.

**Uzasadnienie (Dlaczego?)**
- Brak manifestu uniemożliwia standardową rejestrację rozszerzenia i konfigurację flag optymalizacyjnych (prefetch, prewarm, cache) w ekosystemie Gemini CLI.

**Kroki Wdrożenia (Jak?)**
1. Utworzyć `gemini-extension.json` z polami `name`, `version`, `entrypoint` (np. skrypt uruchamiający FastAPI), `permissions` i sekcją `optimization` (cache, lazyLoad).
2. Dołączyć opis parametrów / URL-i webhooków oraz sekcję bezpieczeństwa (wymagane zmienne środowiskowe, ograniczenia sieciowe).

### Prompt systemowy i kontekst agentów
- **Status:** Instrukcje dla modelu generującego poprawki znajdują się w `debugger/debugger_fix.py` i są szczątkowe (przerywają się po deklaracji formatu pliku).
- **Rekomendacja:** Doprecyzować prompt, aby wymagał planu zmian, walidacji ścieżek, ograniczeń dot. plików binarnych oraz twardych reguł stylu.

**Uzasadnienie (Dlaczego?)**
- Obecny prompt nie narzuca metodologii pracy ani kontroli spójności; agent może wprowadzać halucynacje lub modyfikować niewłaściwe pliki.

**Kroki Wdrożenia (Jak?)**
1. Rozszerzyć `PATCH_INSTRUCTIONS` o kroki: (a) generuj listę zmian przed edycją, (b) aktualizuj wyłącznie istniejące pliki tekstowe, (c) weryfikuj kontekst ścieżek względem `workspace/project`.
2. Wymusić format odpowiedzi z sekcjami „Plan”, „Patch”, „Testy do uruchomienia”.

### Optymalizacja poleceń slash / interakcji
- **Status:** UI (`static/index.html`) wymaga sekwencji: wybór pliku → Upload → Start Debug. Parametry (np. model, liczba iteracji) są zaszyte na stałe.
- **Rekomendacja:** Zgrupować parametry w jednym formularzu (model, maks. iteracje, flaga „tylko analiza”) i wysyłać jednym żądaniem.

**Uzasadnienie (Dlaczego?)**
- Redukuje liczbę rund-tripów i eliminuje niejednoznaczność konfiguracji debuggera.

**Kroki Wdrożenia (Jak?)**
1. W `static/index.html` dodać pola konfiguracyjne i wysyłać je jako JSON w `/start_debug` (np. `iterations`, `dryRun`).
2. W `app.py` przyjmować parametry w endpointzie i przekazywać do `start_debug_loop`.

## Faza 2: Logika, async i debugowanie

### Przepływ kontroli i obsługa błędów
- **Wejście główne:** FastAPI w `app.py` udostępnia `/upload_zip` i `/start_debug`; pętla debuggera w `debugger/debugger_loop.py` steruje kolejnymi iteracjami.
- **Luki:** Brak obsługi wyjątków przy IO (`zipfile`, `shutil`), brak walidacji formatu ZIP, brak limitu rozmiaru; w `ask` (klient OpenAI) wywołania synchroniczne blokują pętlę i brak retry/backoff.

**Uzasadnienie (Dlaczego?)**
- Niespójne błędy mogą przerwać pętlę lub zwrócić surowe wyjątki do klienta, a blokujące wywołania hamują współbieżność serwera.

**Kroki Wdrożenia (Jak?)**
1. Dodać `try/except` z mapowaniem na HTTP statusy w `/upload_zip` i `/start_debug`; walidować typ MIME i rozmiar pliku.
2. W `ai/chatgpt_client.ask` użyć `httpx.AsyncClient` z timeoutem, retry (exponential backoff) i klarownymi kodami błędów.

### Minimalizacja tokenów i kosztów
- **Ryzyka:** `ask` każdorazowo wysyła pełny prompt bez buforowania; brak ograniczenia długości kontekstu; pętla debuggera może odpalać do 10 pełnych rund nawet gdy brak zmian.

**Uzasadnienie (Dlaczego?)**
- Powtarzalne zapytania i pełny kontekst zwiększają zużycie tokenów.

**Kroki Wdrożenia (Jak?)**
1. Wprowadzić cache odpowiedzi dla identycznych zapytań na poziomie iteracji (hash promptu + wersja plików).
2. Dodawać skrócony diff (pliki z `FIXME`) zamiast pełnej listy plików; limitować iteracje gdy brak nowych zmian.

### Wąskie gardła i race conditions
- **Edge case 1:** Równoległe wywołania `/upload_zip` mogą usuwać katalog `workspace/project` podczas trwającej pętli debuggera.
- **Edge case 2:** `apply_patches` tworzy kopie `.bak` bez blokady; równoległe zapisy nadpiszą się.
- **Edge case 3:** Brak synchronizacji między startem debuggera a trwającym uploadem – może czytać niekompletny projekt.

**Uzasadnienie (Dlaczego?)**
- Operacje IO wykonywane równolegle mogą prowadzić do uszkodzenia stanu projektu i niespójnych logów.

**Kroki Wdrożenia (Jak?)**
1. Dodać blokadę plikową / asyncio.Lock obejmującą `/upload_zip` i `/start_debug`.
2. W `apply_patches` stosować tymczasowe pliki i atomowy rename; zabezpieczyć tworzenie backupów per transakcja.
3. W `start_debug_loop` sprawdzać sygnał „projekt w trakcie uploadu” i opóźniać start do zakończenia.

### Hierarchia błędów i raportowanie
- **Propozycja klas:** `ApiError`, `ValidationError`, `AgentError`, `SystemError` dziedziczące z `HTTPException` lub własnej bazy.

**Uzasadnienie (Dlaczego?)**
- Standaryzuje komunikaty i ułatwia mapowanie na kody HTTP oraz front-endowe alerty.

**Kroki Wdrożenia (Jak?)**
1. Utworzyć moduł `errors.py` z hierarchią i helperem `to_http_response` zwracającym {code, message, hint}.
2. Zawijać kluczowe ścieżki (`upload_zip`, `start_debug`, `ask`) i zwracać przyjazne komunikaty (np. „Plik ZIP przekracza limit 20 MB – spróbuj mniejszy”).

## Faza 3: Refaktoryzacja i testowalność

### Modularność i SoC
- **Problem:** Logika uploadu, debugowania i AI wymieszana w `app.py`; prompt i logika patchowania rozproszone.

**Kroki Wdrożenia (Jak?)**
1. Wydziel moduł `services/upload.py` (walidacja ZIP, ekstrakcja, blokady) i `services/debugger.py` (pętla, harmonogram, limit iteracji).
2. Oddziel klienta AI do `ai/client.py` z interfejsem i implementacją OpenAI; umożliwi to mockowanie.
3. Przenieś operacje plikowe patchera do klasy `PatchApplier` z zależnościami wstrzykiwanymi (ścieżki, strategia backupu).

### Standardy kodu, linting, nazewnictwo
- **Naruszenia (przykłady w stylu PEP 8):**
  1. Brak pustej linii na początku `debugger/debugger_patcher.py` i obecność zbędnych nagłówków `---`/`###` pochodzących z dokumentacji.
  2. Funkcja `ask` używa globalnego `OPENAI_API_KEY` bez stałej pisanej capslockiem i bez walidacji typu (PEP 8: stałe modułowe + guard). 
  3. Importy w `app.py` nie są posortowane; brak grupowania standard/lib/third-party/local.
  4. Brak adnotacji typów zwracanych w `home` i `start_debug` w `app.py`.
  5. Literały ścieżek (`"workspace"`, `"workspace/project"`) zduplikowane zamiast stałych.

**Kroki Wdrożenia (Jak?)**
1. Dodać `ruff` / `flake8` z konfiguracją PEP 8, `isort` do sortowania importów, `mypy` dla statycznych typów.
2. Ustandaryzować nazwy: `ask` → `query_chatgpt_async`, `start_debug` (endpoint) → `start_debug_endpoint`, `start_debug_loop` → `run_debug_loop`, `apply_patches` → `apply_patch_batch`, `signal_ping` → `ping_signal`.

### Testowalność (krytyczne ścieżki)
- **Ścieżki:** (1) upload + ekstrakcja ZIP, (2) iteracyjna pętla debuggera z wykrywaniem `FIXME`, (3) wywołanie AI i aplikacja patchy.

**Kroki Wdrożenia (Jak?)**
1. Utworzyć interfejs `LLMClient` i mock w testach (zwraca kontrolowane patchy / błędy).
2. Dla `/upload_zip`: użyć `TestClient` FastAPI i `tempfile.TemporaryDirectory`; weryfikować walidację MIME/limitów i strukturę katalogów.
3. Dla debuggera: podstawić fixture z projektem zawierającym `FIXME`, mock `start_debug_loop` tak, by zwracał deterministyczne logi; sprawdzać liczbę iteracji.
4. Dla `apply_patches`: testy idempotencji, konfliktów i backupów; użyć `tmp_path` oraz równoległych zapisów z `ThreadPoolExecutor` do wykrycia race conditions.

### Dokumentacja i onboarding
- **Status:** `README.md` jest minimalne (tylko tytuł). Brak instrukcji uruchomienia, wymagań środowiskowych, procesu „Review and Merge”.

**Kroki Wdrożenia (Jak?)**
1. Rozszerzyć README o: instalację (Python 3.11, `pip install -r requirements.txt`), uruchomienie (`uvicorn app:app --reload`), opis endpointów i przepływ upload→debug.
2. Dodać sekcję „Review and Merge”: jak generować logi debuggera, jak oceniać patchy, kto zatwierdza zmiany.
3. Dostarczyć przykładowy ZIP testowy i scenariusz „start w 5 minut”.
