README.md – Regis 4.0 Debugger Edition (Monolith)

Dokumentacja Techniczna + Przewodnik Rozwojowy

🧠 1. Wprowadzenie

Regis 4.0 Debugger Edition jest lokalnym, samodzielnym środowiskiem AI do:

analizy projektów programistycznych

wykrywania błędów

generowania łat programistycznych

automatycznej korekcji plików

debugowania wieloetapowego

integracji z modelami OpenAI

wykonywania kodu lokalnego (python + shell)

manipulowania plikami lokalnymi

obsługi ZIP (upload → extract → analyze → fix)

tworzenia pętli naprawczej aż do pełnej poprawności

To forma lokalnego „AI Copilot Debugger” — działa offline dla kodu, a interakcja z OpenAI jest tylko przy analizie i generowaniu łatek.

🧱 2. Architektura

Projekt ma strukturę monolityczną (jedna przestrzeń kodowa, pełna kontrola nad wszystkim):

Regis/
 ├── app.py
 ├── signaling.py
 ├── dashboard.html
 ├── chatgpt_client.py
 ├── python_tool.py
 ├── shell_tool.py
 ├── exec_tool.py
 ├── file_tool.py
 ├── debugger_analyzer.py
 ├── debugger_fix.py
 ├── debugger_patcher.py
 ├── debugger_loop.py
 ├── workspace/
 │    ├── project/
 │    ├── output_fixed/
 │    └── backups/
 ├── requirements.txt
 ├── run.ps1
 └── README.md   ← (TEN PLIK)

⚙️ 3. Moduły i ich funkcje
3.1 app.py – główny serwer

uruchamia FastAPI

renderuje GUI

obsługuje upload ZIP

wywołuje debug loop

3.2 signaling.py – warstwa komend

Obsługuje komunikaty terminala:

Komenda	Funkcja
ai:	zapytania do ChatGPT
aifix:	AI fix (Codex-like)
aismart:	auto-mode
py:	uruchamianie kodu Python
sh:	komendy systemowe
run:	uruchamianie procesów
file:*	operacje plikowe
brak prefixu	auto eval/exec

To „mózg interakcji”.

3.3 chatgpt_client.py – integracja OpenAI

Obsługuje modele:

gpt-4.1

gpt-4.1-mini

o3-mini

Tryby:

Funkcja	Zastosowanie
ask()	zwykły tekst
codex_fix()	analiza kodu / poprawki
smart()	wykrywanie kodu / auto-tryb
3.4 python_tool.py / shell_tool.py / exec_tool.py

Zapewniają:

evaluation kodu

wykonywanie procedur

uruchamianie aplikacji

integrację systemową

3.5 file_tool.py – operacje na plikach

Obsługuje:

listowanie

odczyt

zapis

kopiowanie

usuwanie

tworzenie katalogów

🧠 4. System Debuggera (Debugger Engine)

To serce całego systemu: AI Debug Loop.

Składa się z modułów:

4.1 debugger_analyzer.py

Odpowiada za:

rekursywne skanowanie projektu

pobieranie treści plików

filtrowanie tylko istotnych formatów

raportowanie struktur

4.2 debugger_fix.py

Zadanie:

generować łatki diff

wysyłać błędy do ChatGPT

interpretować odpowiedź

4.3 debugger_patcher.py

Zadanie:

parsować diff

stosować zmiany

tworzyć backupy

zabezpieczać integralność

Backupy trafiają do:

workspace/backups/

4.4 debugger_loop.py – pętla debuggera

Najważniejszy element.

Pseudokod:

for pass in 0..9:
    zeskanuj projekt
    znajdź błędy (heurystyka lub AST)
    jeśli brak błędów → koniec
    wygeneruj łatki (ChatGPT)
    nałóż łatki


W razie błędu:

zapisuje log

nie przerywa bez powodu

zatrzymuje się dopiero gdy projekt jest „czysty”

Wynik trafia do GUI.

📂 5. Workspace – środowisko projektów

Folder:

workspace/
    project/       ← projekt wejściowy
    output_fixed/  ← projekt po naprawie
    backups/       ← kopie bezpieczeństwa


Podczas debugowania:

pliki z project/ są analizowane

laki stosowane w miejscu

na końcu mogą zostać przeniesione do output_fixed/

🖥️ 6. Interfejs użytkownika (dashboard.html)

UI zawiera:

wybór pliku ZIP

przycisk „Upload ZIP”

przycisk „Start Debug Loop”

panel logów

terminal WebRTC

Czyli pełne sterowanie agentem.

💬 7. Jak działa komunikacja z OpenAI?

Każdy etap debugowania używa modelu:

gpt-4.1
lub
o3-mini (kod)


Model generuje:

opis błędów

plan działania

łatki diff

Każda iteracja pętli:

errors → GPT → diff → patch → scan → repeat


To imitacja profesjonalnych narzędzi typu:

GitHub Copilot

OpenAI Developer Tools

IntelliJ AI Assistant

Ale działa lokalnie.

🛰️ 8. Jak rozwijać projekt

Sekcja najważniejsza dla przyszłych wersji.

8.1 Dodanie AST-analyzera

Możemy dodać:

wykrywanie błędnych importów

wykrywanie błędnych wywołań funkcji

sprawdzanie brakujących argumentów

wykrywanie nieużywanych zmiennych

8.2 Dodanie generatora testów

AI może generować:

testy jednostkowe

testy integracyjne

dane testowe

coverage

8.3 Dodanie AI Refactoring Engine

Możemy:

przepisywać projekt na OOP

wprowadzać typowanie

usuwać code-smells

implementować SOLID

generować strukturę folderów

8.4 Dodanie Continuous Debugging

Agent:

wykrywa zmiany plików

automatycznie debugguje

sam się zapętla

8.5 Dodanie WebRTC Media Stream

Możemy rozszerzyć o:

stream audio

stream video

live coding

🔮 9. Roadmapa Regis 5.0+ (propozycja)
Wersja	Funkcje
5.0	AST + analiza typów + pełny test generator
5.1	AI refactor engine
5.2	live debugging w przeglądarce
5.3	integracja z Git (diff, push, branches)
5.4	pluginy rozszerzające komendy
6.0	pełne IDE AI (edytor kodu + chat)
7.0	multi-agent debugging (kotwice logiczne)
8.0	obsługa projektów w C/C++/Go/TS/Java
⚠️ 10. Ograniczenia

Regis 4.0 nie jest:

pełnym interpreterem

sandboxem

środowiskiem CI/CD

Jest za to:

inteligentnym asystentem AI

lokalnym debuggerem

narzędziem do refaktoru

silnikiem patchowania projektów

💡 11. Pomysły przyszłościowe

Auto-moduł „AI Commit Message”

Auto-opis zmian

Eksport zmian jako PR

Integracja ze Slack/Discord

Tworzenie dokumentacji automatycznie

🏁 12. Podsumowanie

Regis 4.0 Debugger Edition to:

lokalny debug AI

pełna analiza projektów

AI patch engine

obsługa ZIP

pętla naprawcza

terminal i GUI

integracja OpenAI

możliwość pełnej rozbudowy

To fundament do budowy:

własnego IDE

własnego CI/CD

własnego AI Copilota

własnego systemu do analizy dowolnych repozytoriów