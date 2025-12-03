Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "         Regis 4.1 – Launcher          " -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Przejście do folderu skryptu
Set-Location (Split-Path $MyInvocation.MyCommand.Path)

# ---------------------------------------------------------
# Sprawdzenie klucza API
# ---------------------------------------------------------
if (-not $env:OPENAI_API_KEY) {
    Write-Host "[!] UWAGA: Brak zmiennej OPENAI_API_KEY!" -ForegroundColor Red
    Write-Host "    Ustaw ją tak:" -ForegroundColor DarkYellow
    Write-Host "    setx OPENAI_API_KEY \"TWÓJ_KLUCZ\"" -ForegroundColor Gray
    Write-Host ""
}

# ---------------------------------------------------------
# Tworzenie środowiska venv
# ---------------------------------------------------------
if (!(Test-Path "./venv")) {
    Write-Host "[*] Tworzę środowisko virtualenv..." -ForegroundColor Cyan
    py -3 -m venv venv
}

# ---------------------------------------------------------
# Aktywacja środowiska
# ---------------------------------------------------------
Write-Host "[*] Aktywuję środowisko..." -ForegroundColor Cyan
. .\venv\Scripts\Activate.ps1

# ---------------------------------------------------------
# Instalacja zależności
# ---------------------------------------------------------
Write-Host "[*] Aktualizuję pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel

Write-Host "[*] Instaluję wymagane pakiety..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "   Regis działa na: http://localhost:8000"
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# ---------------------------------------------------------
# Start serwera
# ---------------------------------------------------------
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
