@echo off
chcp 65001 > nul
cd /d "%~dp0"
title RegisLite - LIVE DEBUG 🥟

echo.
echo ==============================================
echo   👁️  TRYB PODGLĄDU NA ŻYWO
echo   Logi lecą na ekran ORAZ do pliku server.log
echo ==============================================
echo.

:: Aktywacja środowiska
call venv\Scripts\activate.bat

:: Uruchomienie z podglądem (wymaga PowerShell do obsługi 'tee')
:: 2>&1 łączy błędy z normalnym tekstem, żeby wszystko trafiło do logu
powershell -Command "uvicorn app:app --reload --port 8000 2>&1 | Tee-Object -FilePath 'server.log'"

echo.
echo [🛑] Serwer zatrzymany.
pause