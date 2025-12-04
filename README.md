Nowa Struktura Projektu RegisLite

Projekt został zrefaktoryzowany do architektury modułowej.

Struktura katalogów

run.py - Skrypt startowy. Używaj go zamiast uvicorn app:app ....

src/ - Główny kod źródłowy aplikacji.

main.py - Punkt wejścia aplikacji (dawne app.py).

ai/, rtc/, debugger/, services/ - Moduły z logiką.

config/ - Konfiguracja i zmienne środowiskowe.

static/ - Pliki frontendowe (dashboard.html).

scripts/ - Narzędzia pomocnicze, skrypty naprawcze (fix_*.py), skrypty PowerShell.

docs/ - Logi błędów, notatki i stara dokumentacja.

Jak uruchomić?

Zainstaluj zależności (ponownie, bo usunęliśmy stary venv):

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt


Uruchom serwer:

python run.py


Aplikacja wstanie na porcie 8000.

Uwaga dotycząca importów

Jeśli będziesz tworzył nowe pliki w src/, używaj importów absolutnych, np.:
from src.services import file_tool zamiast import services.file_tool.