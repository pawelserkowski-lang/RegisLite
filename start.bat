@echo off
setlocal
title Instalator Jules (Python 3.10+)
color 0B

echo ==========================================
echo      JULES INSTALLER & UPDATER
echo ==========================================

:: 1. Sprawdzenie Pythona (prosty check)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Python nie jest zainstalowany lub nie ma go w PATH.
    echo Zainstaluj Python 3.10+ i zaznacz "Add to PATH".
    pause
    exit /b
)

:: 2. Klonowanie lub Aktualizacja
if exist "jules" (
    echo [INFO] Folder 'jules' znaleziony. Aktualizuje repozytorium...
    cd jules
    git pull
    if %errorlevel% neq 0 goto :error
) else (
    echo [INFO] Klonuje repozytorium julescd do folderu 'jules'...
    git clone https://github.com/gemini-cli-extensions/julescd jules
    cd jules
    if %errorlevel% neq 0 goto :error
)

:: 3. Tworzenie VENV (jesli nie istnieje)
if not exist "venv" (
    echo [INFO] Tworze wirtualne srodowisko (venv)...
    python -m venv venv
    if %errorlevel% neq 0 goto :error
) else (
    echo [INFO] Venv juz istnieje.
)

:: 4. Instalacja Zaleznosci
echo [INFO] Instaluje/Aktualizuje zaleznosci z requirements.txt...
call venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% neq 0 goto :error

echo.
echo ==========================================
echo [SUKCES] Instalacja zakonczona!
echo ==========================================
echo.
echo PAMIETAJ:
echo 1. Ustaw klucz API: set OPENAI_API_KEY=sk-....
echo 2. Lub dodaj go do zmiennych srodowiskowych Windows.
echo.
echo Aby uruchomic, wpisz w konsoli (bedac w folderze jules):
echo python main.py (lub inna komende startowa z dokumentacji)
echo.
pause
exit /b

:error
color 0C
echo.
echo [BLAD] Wystapil blad podczas instalacji. Sprawdz komunikaty powyzej.
pause
exit /b