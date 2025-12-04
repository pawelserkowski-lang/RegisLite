# run.ps1
Write-Host "RegisLite STARTUJE!" -ForegroundColor Cyan
uvicorn app:app --reload --port 8000
Start-Process "http://localhost:8000"
