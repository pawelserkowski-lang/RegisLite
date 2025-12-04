# 🔐 RegisLite - Przewodnik Ustawiania Windows Environment Variables

 ZASADA NADRZĘDNA Wszystkie klucze API ZAWSZE z Windows Environment Variables!

---

## 📋 Spis Treści

1. [Czym są Environment Variables](#czym-są-environment-variables)
2. [Dlaczego Windows ENV  .env](#dlaczego-windows-env--env)
3. [Metoda 1 PowerShell (Szybka)](#metoda-1-powershell-szybka)
4. [Metoda 2 GUI (Wizualna)](#metoda-2-gui-wizualna)
5. [Metoda 3 Python Helper (Automatyczna)](#metoda-3-python-helper-automatyczna)
6. [Weryfikacja](#weryfikacja)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Czym są Environment Variables

Environment Variables (zmienne środowiskowe) to globalne ustawienia systemu Windows, które są dostępne dla wszystkich aplikacji. To jak sejf na hasła w Twoim komputerze.

Przykład
```
Nazwa OPENAI_API_KEY
Wartość sk-proj-abc123xyz...
```

Każda aplikacja może odczytać tę zmienną, ale nie zobaczy jej w kodzie źródłowym (bezpieczeństwo!).

---

## Dlaczego Windows ENV  .env

 Aspekt  Windows ENV  .env File 
--------------------------------
 Bezpieczeństwo  ✅ Nie w repozytorium  ⚠️ Łatwo commitnąć przez pomyłkę 
 Trwałość  ✅ Raz ustawione = zawsze działa  ❌ Trzeba kopiować między projektami 
 Współdzielenie  ✅ Wszystkie projekty  ❌ Tylko jeden projekt 
 Production  ✅ Standardowe podejście  ❌ Nie dla produkcji 
 Git  ✅ Nie ma problemu  ⚠️ Trzeba pamiętać o .gitignore 

### 🎯 Hierarchia RegisLite
```
1. Windows Environment Variables (PRIORYTET!)
   ↓ (jeśli nie ma)
2. .env file (fallback development)
   ↓ (jeśli nie ma)
3. ValueError (aplikacja się nie uruchomi)
```

---

## Metoda 1 PowerShell (Szybka) ⚡

### Krok 1 Otwórz PowerShell jako Administrator

```powershell
# Kliknij prawym na Start → Windows PowerShell (Admin)
# Lub Win+X → Windows PowerShell (Admin)
```

### Krok 2 Ustaw zmienną

```powershell
# Dla pojedynczego użytkownika (ZALECANE)
setx OPENAI_API_KEY sk-proj-twoj-klucz-tutaj

# Dla całego systemu (wymaga admin)
setx OPENAI_API_KEY sk-proj-twoj-klucz-tutaj M
```

### Krok 3 Sprawdź czy działa

```powershell
# W NOWYM oknie PowerShell (zamknij stare i otwórz nowe!)
echo $envOPENAI_API_KEY
```

Oczekiwany output
```
sk-proj-twoj-klucz-tutaj
```

### ⚠️ WAŻNE!
- RESTART terminalaIDE po ustawieniu!
- Stare terminale nie zobaczą nowej zmiennej
- Może trzeba zrestartować całe IDE (VS Code, PyCharm, etc.)

---

## Metoda 2 GUI (Wizualna) 🖱️

### Krok 1 Otwórz System Properties

Opcja A - Skrót
```
Win + R → wpisz sysdm.cpl → Enter
```

Opcja B - Ustawienia
```
Start → Ustawienia → System → Informacje o systemie → 
Zaawansowane ustawienia systemu
```

### Krok 2 Environment Variables

![System Properties](httpsi.imgur.complaceholder.png)

1. W oknie System Properties → zakładka Advanced
2. Kliknij Environment Variables... na dole

### Krok 3 Dodaj nową zmienną

![Environment Variables](httpsi.imgur.complaceholder2.png)

#### Dla Twojego użytkownika (ZALECANE)
1. W sekcji User variables for [TwojaNazwa]
2. Kliknij New...
3. Wypełnij
   - Variable name `OPENAI_API_KEY`
   - Variable value `sk-proj-twoj-klucz-tutaj`
4. Kliknij OK → OK → OK

#### Dla całego systemu (opcjonalnie)
1. W sekcji System variables (wymaga admin!)
2. Kliknij New...
3. Wypełnij jak wyżej
4. OK → OK → OK

### Krok 4 Restart

RESTART
- Zamknij WSZYSTKIE terminale
- Zamknij IDE (VS Code, PyCharm, etc.)
- Opcjonalnie restart komputera (100% pewności)

### Krok 5 Sprawdź

Otwórz nowy PowerShell
```powershell
echo $envOPENAI_API_KEY
```

---

## Metoda 3 Python Helper (Automatyczna) 🐍

RegisLite ma wbudowany helper do ustawiania ENV vars!

### Krok 1 Użyj komendy

```powershell
# Uruchom jako Administrator!
python -m config.env_config --set OPENAI_API_KEY sk-proj-twoj-klucz
```

### Krok 2 Restart terminala

```powershell
# Zamknij i otwórz nowy terminal
```

### Krok 3 Weryfikuj

```powershell
python -m config.env_config --test
```

Oczekiwany output
```
🧪 TESTOWANIE KONFIGURACJI...

✓ [OPENAI_API_KEY] załadowany z Windows ENV
✅ Konfiguracja POPRAWNA!
```

---

## Weryfikacja ✅

### Test 1 PowerShell

```powershell
echo $envOPENAI_API_KEY
# Powinno pokazać klucz (sk-proj-...)
```

### Test 2 Python

```python
import os
print(os.getenv(OPENAI_API_KEY))
# Powinno pokazać klucz
```

### Test 3 RegisLite Config Tool

```powershell
python -m config.env_config --test
```

Prawidłowy output
```
════════════════════════════════════════════════════════════════════
🔧 REGISLITE CONFIG - Ładowanie konfiguracji...
════════════════════════════════════════════════════════════════════
✓ [OPENAI_API_KEY] załadowany z Windows ENV
════════════════════════════════════════════════════════════════════
✅ Konfiguracja załadowana pomyślnie!
════════════════════════════════════════════════════════════════════

📋 PODSUMOWANIE KONFIGURACJI
   OpenAI Key ✓ SET
   Anthropic Key ○ Optional
   GitHub Token ○ Optional
   Debug Mode True
   Max Iterations 10
   OpenAI Model gpt-4o-mini
   Workspace workspace

✅ Walidacja konfiguracji OK
```

### Test 4 Lista wszystkich ENV vars

```powershell
python -m config.env_config --list OPENAI
```

Output
```
📋 Zmienne środowiskowe (prefix 'OPENAI')

   OPENAI_API_KEY = sk-proj-ab...
   OPENAI_MODEL = gpt-4o-mini
```

---

## Troubleshooting 🔧

### Problem 1 Brak klucza OPENAI_API_KEY

Symptom
```
ValueError Brak wymaganego klucza OPENAI_API_KEY
```

Rozwiązanie
1. Sprawdź czy klucz jest ustawiony
   ```powershell
   echo $envOPENAI_API_KEY
   ```
2. Jeśli pusty → ustaw metodą 1, 2 lub 3
3. RESTART terminala!

---

### Problem 2 Zmienną ustawiłem, ale dalej nie działa

Przyczyny
- ❌ Nie zrestartowałeś terminala
- ❌ Używasz starego terminala (przed ustawieniem)
- ❌ IDE cache'uje stare ENV vars

Rozwiązanie
```powershell
# 1. Zamknij WSZYSTKIE okna terminala
# 2. Zamknij IDE (VS Code, PyCharm, etc.)
# 3. Otwórz nowy terminal
# 4. Sprawdź
echo $envOPENAI_API_KEY

# Jeśli dalej pusty → restart komputera
```

---

### Problem 3 Klucz widać w PowerShell, ale nie w Python

Rozwiązanie
```python
# Test
import os
import sys

print(Python version, sys.version)
print(OPENAI_API_KEY, os.environ.get(OPENAI_API_KEY, BRAK))

# Jeśli BRAK
# 1. Sprawdź czy Python uruchomiony z tego samego terminala
# 2. Zrestartuj IDE
# 3. Użyj python -m config.env_config --test
```

---

### Problem 4 setx Access Denied

Przyczyna
Próba ustawienia system variable (`M`) bez uprawnień admin.

Rozwiązanie
```powershell
# Opcja A Użyj bez M (tylko dla użytkownika)
setx OPENAI_API_KEY sk-proj-klucz

# Opcja B Uruchom PowerShell jako Admin
# Kliknij prawym na Start → PowerShell (Admin)
setx OPENAI_API_KEY sk-proj-klucz M
```

---

### Problem 5 RegisLite używa .env zamiast Windows ENV

Diagnoza
```powershell
python -m config.env_config --test
```

Jeśli pokazuje
```
✓ [OPENAI_API_KEY] załadowany z .env file
```

Przyczyna
Windows ENV nie jest ustawiony lub ma pustą wartość.

Rozwiązanie
1. Usuń `OPENAI_API_KEY` z `.env` (opcjonalnie)
2. Ustaw w Windows ENV (metoda 123)
3. Restart terminala
4. Testuj ponownie

---

## FAQ ❓

### Q Czy mogę używać .env zamiast Windows ENV

A Technicznie tak (fallback), ale nie zalecane
- ❌ Mniej bezpieczne (łatwo commitnąć do git)
- ❌ Nie działa globalnie
- ❌ Nie jest standardem produkcyjnym

Wyjątek Developmenttesting gdy często zmieniasz klucze.

---

### Q Jak ustawić wiele kluczy na raz

PowerShell
```powershell
setx OPENAI_API_KEY sk-proj-klucz1
setx ANTHROPIC_API_KEY sk-ant-klucz2
setx GITHUB_TOKEN ghp_klucz3
```

Python Helper
```powershell
python -m config.env_config --set OPENAI_API_KEY sk-proj-klucz1
python -m config.env_config --set ANTHROPIC_API_KEY sk-ant-klucz2
```

---

### Q Jak usunąć klucz

PowerShell
```powershell
# User level
[Environment]SetEnvironmentVariable(OPENAI_API_KEY, $null, User)

# System level (jako Admin)
[Environment]SetEnvironmentVariable(OPENAI_API_KEY, $null, Machine)
```

GUI
1. Win+R → `sysdm.cpl`
2. Advanced → Environment Variables
3. Zaznacz zmienną → Delete

---

### Q Czy klucz jest bezpieczny w Windows ENV

A Tak, o ile
- ✅ Twój komputer ma hasłoPIN
- ✅ Nie udostępniasz konta innym
- ✅ Nie instalujesz podejrzanych aplikacji

Bonus Windows ENV nie trafia do Git!

---

### Q Czy muszę restartować komputer

A Nie zawsze
- ✅ Restart terminala = wystarczy w 90% przypadków
- ✅ Restart IDE = pomaga gdy terminal OK, ale IDE nie widzi
- ⚠️ Restart komputera = tylko gdy powyższe nie działa

---

### Q Gdzie przechowywane są Windows ENV vars

A W rejestrze Windows
- User `HKEY_CURRENT_USEREnvironment`
- System `HKEY_LOCAL_MACHINESYSTEMCurrentControlSetControlSession ManagerEnvironment`

Możesz zobaczyć
```powershell
# Win+R → regedit → przejdź do ścieżki powyżej
```

---

## 📚 Dodatkowe Zasoby

- [Microsoft Docs - Environment Variables](httpsdocs.microsoft.comen-uswindowswin32procthreadenvironment-variables)
- [12-Factor App - Config](https12factor.netconfig)
- [OWASP - Secure Configuration](httpsowasp.orgwww-project-secure-coding-practices-quick-reference-guide)

---

## 🎯 Checklist dla Nowych Użytkowników

Przed uruchomieniem RegisLite

- [ ] Zdobyłem klucz OpenAI z httpsplatform.openai.com
- [ ] Ustawiłem `OPENAI_API_KEY` w Windows ENV (metoda 123)
- [ ] Zrestartowałem terminal
- [ ] Sprawdziłem `echo $envOPENAI_API_KEY` pokazuje klucz
- [ ] Testowałem `python -m config.env_config --test` → ✅ OK
- [ ] Uruchomiłem `.run.ps1` → aplikacja startuje bez błędów

---

## 🥟 Podsumowanie

ZASADA ZŁOTA
```
WSZYSTKIE klucze API → Windows Environment Variables!
.env tylko jako fallback dla development!
ZAWSZE restart terminala po ustawieniu!
```

Metody (wybierz jedną)
1. 🚀 PowerShell `setx OPENAI_API_KEY klucz`
2. 🖱️ GUI Win+R → sysdm.cpl → Environment Variables
3. 🐍 Python `python -m config.env_config --set OPENAI_API_KEY klucz`

Weryfikacja
```powershell
python -m config.env_config --test
```

Gotowe! 🎉

---

div align=center

Made with 🔐 for RegisLite

[← Powrót do README](README.md)  [Dokumentacja Config →](configREADME.md)

div