@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: --- MAGICZNA LINIJA (Ustawia folder roboczy tam gdzie leży plik) ---
cd /d "%~dp0"
:: -------------------------------------------------------------------

title RegisLite Launcher 🥟 - Wersja Ostateczna

echo ========================================================
echo   🤖 RegisLite 4.5 - AUTO-SETUP
echo   (Winget: ON - Pip: ON - Websockets: FIXING...)
echo ========================================================
echo.

:: --- KROK 1: KONTROLA PYTHONA ---
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [🔍 SYSTEM] Nie znaleziono Pythona.
    echo [🔧 WINGET] Instaluje Python 3.11...
    winget install -e --id Python.Python.3.11 --scope machine --accept-package-agreements --accept-source-agreements
    if !errorlevel! neq 0 (
        echo [💀 CRITICAL] Winget nie dal rady. Zainstaluj Pythona recznie.
        pause
        exit /b
    )
    echo [🛑 RESTART] Zrestartuj skrypt!
    pause
    exit
)

:: --- KROK 2: WIRTUALNE SRODOWISKO ---
if not exist "venv" (
    echo [📦 VENV] Tworze venv...
    python -m venv venv
)

call venv\Scripts\activate.bat

:: --- KROK 3: ZALEZNOSCI (AUTO-FIX) ---
echo [🐍 PIP] Aktualizacja pakietow...
python -m pip install --upgrade pip setuptools wheel > nul 2>&1

:: Fix requests/websockets
findstr /i "requests" requirements.txt >nul 2>&1
if %errorlevel% neq 0 echo requests>> requirements.txt
findstr /i "websockets" requirements.txt >nul 2>&1
if %errorlevel% neq 0 echo websockets>> requirements.txt

echo [⬇️ PIP] Instalacja bibliotek...
pip install -r requirements.txt > install_log.txt 2>&1
pip install requests websockets > nul 2>&1

:: --- KROK 4: KONFIGURACJA .ENV ---
if not exist ".env" copy .env.example .env > nul

:: --- KROK 5: START SERWERA ---
if not exist "workspace" mkdir workspace

echo.
echo ========================================================
echo   🚀 REGISLITE URUCHOMIONY
echo   Panel WWW: http://localhost:8000
echo ========================================================
echo.

start /min cmd /c "timeout /t 3 > nul && start http://localhost:8000"
uvicorn app:app --reload --port 8000 2>> error_log.txt

pause