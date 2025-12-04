@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: --- MAGICZNA LINIJA (Ustawia folder roboczy tam gdzie leży plik) ---
cd /d "%~dp0"
:: -------------------------------------------------------------------

title RegisLite Launcher 🥟 - Wersja Ostateczna

echo ========================================================
echo   🤖 RegisLite 4.5 - AUTO-SETUP
echo   (Winget: ON - Pip: ON - Requests: FIXING...)
echo ========================================================
echo.

:: --- KROK 1: KONTROLA PYTHONA (WINGET) ---
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [🔍 SYSTEM] Nie znaleziono Pythona.
    echo [🔧 WINGET] Rozpoczynam automatyczna instalacje Python 3.11...
    echo.
    winget install -e --id Python.Python.3.11 --scope machine --accept-package-agreements --accept-source-agreements
    
    if !errorlevel! neq 0 (
        echo.
        echo [💀 CRITICAL] Winget nie dal rady. Zainstaluj Pythona recznie.
        pause
        exit /b
    )
    echo.
    echo [✅ SYSTEM] Python zainstalowany! Zrestartuj ten skrypt!
    pause
    exit
)

:: --- KROK 2: WIRTUALNE SRODOWISKO ---
if not exist "venv" (
    echo [📦 VENV] Tworze izolowane srodowisko...
    python -m venv venv
)

call venv\Scripts\activate.bat

:: --- KROK 3: ZARZADZANIE PAKIETAMI (PIP + FIX) ---
echo [🐍 PIP] Aktualizacja menedzera pakietow...
python -m pip install --upgrade pip setuptools wheel > nul 2>&1

:: --- [🔧 AUTO-FIX] DLA REQUESTS ---
:: Sprawdzamy czy requests jest w pliku, jak nie to dopisujemy
findstr /i "requests" requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [🔧 FIX] Wykryto brak 'requests' w requirements.txt. Naprawiam...
    echo requests>> requirements.txt
)
:: ----------------------------------

echo [⬇️ PIP] Instalacja zaleznosci...
pip install -r requirements.txt > install_log.txt 2>&1

:: Dla pewnosci instalujemy requests recznie, gdyby pip marudzil
pip install requests > nul 2>&1

if %errorlevel% neq 0 (
    echo [❌ ERROR] Blad instalacji. Sprawdz install_log.txt
    type install_log.txt
    pause
    exit /b
)
echo [✅ PIP] Biblioteki gotowe.

:: --- KROK 4: KONFIGURACJA .ENV ---
if not exist ".env" (
    echo [⚙️ CONFIG] Tworze plik .env...
    copy .env.example .env > nul
    echo.
    echo [❗ INFO] Otwieram .env - wpisz tam swoj klucz API!
    notepad .env
)

:: --- KROK 5: START SERWERA ---
if not exist "workspace" mkdir workspace

echo.
echo ========================================================
echo   🚀 REGISLITE URUCHOMIONY
echo   Panel WWW: http://localhost:8000
echo   (Bledy leca do error_log.txt)
echo ========================================================
echo.

start /min cmd /c "timeout /t 3 > nul && start http://localhost:8000"
uvicorn app:app --reload --port 8000 2>> error_log.txt

echo.
echo [🛑 STOP] Serwer zatrzymany.
pause