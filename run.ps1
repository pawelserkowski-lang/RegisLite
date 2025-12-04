# run.ps1
Write-Host "RegisLite 4.0 STARTUJE!" -ForegroundColor Cyan
uvicorn app:app --reload --port 8000
Start-Process "http://localhost:8000"
