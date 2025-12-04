@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
:: --- MAGICZNA LINIJA NAPRAWCZA ---
cd /d "%~dp0"
:: ---------------------------------

title RegisLite Launcher 🥟 - Winget + Pip Edition

echo ========================================================
echo   🤖 RegisLite 4.5 - AUTO-SETUP
echo   (Winget: ON - Pip: ON - Pierogi: LOADING...)
echo ========================================================
echo.

:: --- KROK 1: KONTROLA PYTHONA (WINGET) ---
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [🔍 SYSTEM] Nie znaleziono Pythona.
    echo [🔧 WINGET] Rozpoczynam automatyczna instalacje Python 3.11...
    echo.
    
    :: Instalacja przez Winget
    winget install -e --id Python.Python.3.11 --scope machine --accept-package-agreements --accept-source-agreements
    
    if !errorlevel! neq 0 (
        echo.
        echo [💀 CRITICAL] Winget nie dal rady.
        echo              Zainstaluj Pythona recznie ze strony python.org.
        pause
        exit /b
    )

    echo.
    echo [✅ SYSTEM] Python zainstalowany!
    echo [🛑 RESTART] Wymagany restart tego skryptu, aby Windows "zobaczyl" nowy program.
    echo             Zamykam okno... Uruchom start.bat ponownie!
    pause
    exit
)

:: --- KROK 2: WIRTUALNE SRODOWISKO ---
if not exist "venv" (
    echo [📦 VENV] Tworze izolowane srodowisko...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [❌ ERROR] Blad tworzenia venv.
        pause
        exit /b
    )
)

:: Aktywacja
call venv\Scripts\activate.bat

:: --- KROK 3: ZARZADZANIE PAKIETAMI (PIP) ---
echo [🐍 PIP] Aktualizacja menedzera pakietow...
python -m pip install --upgrade pip setuptools wheel > nul 2>&1

echo [⬇️ PIP] Instalacja zaleznosci z requirements.txt...
pip install -r requirements.txt > install_log.txt 2>&1

if %errorlevel% neq 0 (
    echo [❌ ERROR] Cos poszlo nie tak z instalacja bibliotek.
    echo          Sprawdz plik install_log.txt
    type install_log.txt
    pause
    exit /b
)
echo [✅ PIP] Wszystkie biblioteki gotowe.

:: --- KROK 4: KONFIGURACJA .ENV ---
if not exist ".env" (
    echo [⚙️ CONFIG] Tworze plik .env...
    copy .env.example .env > nul
    echo.
    echo [❗ INFO] Otwieram .env w notatniku - wpisz tam swoj klucz OpenAI!
    notepad .env
)

:: --- KROK 5: START SERWERA ---
if not exist "workspace" mkdir workspace

echo.
echo ========================================================
echo   🚀 REGISLITE GOTOWY DO PRACY
echo   Panel WWW: http://localhost:8000
echo   Logi bledow: error_log.txt
echo ========================================================
echo.

:: Otworz przegladarke i uruchom serwer
start /min cmd /c "timeout /t 3 > nul && start http://localhost:8000"
uvicorn app:app --reload --port 8000 2>> error_log.txt

echo.
echo [🛑 STOP] Serwer zatrzymany.
pause