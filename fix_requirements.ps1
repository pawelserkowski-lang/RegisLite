Write-Host "=== Regis REQUIREMENTS REPAIR ===" -ForegroundColor Cyan

Set-Location (Split-Path $MyInvocation.MyCommand.Path)

# Nadpisz poprawną wersją
@"
fastapi
uvicorn
requests
python-multipart
"@ | Set-Content "requirements.txt" -Encoding UTF8

Write-Host "[*] Naprawiono requirements.txt" -ForegroundColor Green

# Aktywuj venv
if (Test-Path "venv") {
    . .\venv\Scripts\Activate.ps1
}

# Wyczyść cache pip
pip cache purge

# Instalacja zależności
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn requests python-multipart

Write-Host "[OK] Wszystkie pakiety zainstalowane." -ForegroundColor Green
