Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      RegisLite -> GitHub Launcher        " -ForegroundColor Yellow
Write-Host "      Target: pawelserkowski-lang         " -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 0. Konfiguracja "na sztywno" dla Twojego projektu
$TargetRepoUrl = "https://github.com/pawelserkowski-lang/RegisLite.git"

# 1. Sprawdź czy Git jest zainstalowany
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[!] BŁĄD: Nie widzę 'git' w systemie. Zainstaluj Git for Windows!" -ForegroundColor Red
    exit
}

# 2. Inicjalizacja (jeśli trzeba)
if (!(Test-Path ".git")) {
    Write-Host "[*] Inicjuję nowe repozytorium Git..." -ForegroundColor Green
    git init
} else {
    Write-Host "[*] Repozytorium Git już istnieje lokalnie." -ForegroundColor Gray
}

# 3. Dodawanie plików
Write-Host "[*] Dodaję wszystkie pliki (git add .)..." -ForegroundColor Green
git add .

# 4. Commit
# Możesz tu zmienić wiadomość, jeśli robisz coś innego niż refactor
$commitMsg = "RegisLite Update: Auto-sync via PowerShell Launcher"
Write-Host "[*] Tworzę commita: $commitMsg" -ForegroundColor Green
git commit -m $commitMsg

# 5. Konfiguracja Zdalna (Remote) - TERAZ Z AUTOMATEM
$currentRemote = git remote get-url origin 2>$null

if (!$currentRemote) {
    Write-Host ""
    Write-Host "[*] Brak zdalnego repozytorium. Ustawiam RegisLite..." -ForegroundColor Yellow
    
    # Używamy Twojego linku zdefiniowanego na górze
    git remote add origin $TargetRepoUrl
    Write-Host "[+] Ustawiono origin na: $TargetRepoUrl" -ForegroundColor Green

} else {
    # Sprawdzamy, czy obecny remote to ten właściwy, czy jakiś "obcy"
    if ($currentRemote -eq $TargetRepoUrl) {
        Write-Host "[*] Zdalne repozytorium poprawnie ustawione na RegisLite." -ForegroundColor Gray
    } else {
        Write-Host "[!] UWAGA: Remote wskazuje na inny adres: $currentRemote" -ForegroundColor Red
        Write-Host "    Czy na pewno chcesz wysłać pliki tam, a nie do RegisLite?" -ForegroundColor Yellow
        $decision = Read-Host "    Wpisz 'T' aby kontynuować z OBECNYM adresem, lub cokolwiek innego by przerwać"
        if ($decision -ne 'T') { exit }
    }
}

# 6. Push
Write-Host "[*] Upewniam się, że branch to 'main'..." -ForegroundColor Green
git branch -M main

Write-Host "[*] WYPYCHANIE NA GITHUB (git push)..." -ForegroundColor Yellow
# Dodajemy obsługę błędu, bo jeśli repozytorium nie jest puste, zwykły push może zostać odrzucony
git push -u origin main 2>&1 | Tee-Object -Variable PushOutput

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUKCES! Kod wylądował w RegisLite." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ BŁĄD PUSHA! GitHub odrzucił pliki." -ForegroundColor Red
    Write-Host "   Możliwa przyczyna: Zdalne repozytorium ma zmiany, których nie masz u siebie."
    Write-Host "   Rozwiązanie: Spróbuj najpierw 'git pull origin main' ręcznie." -ForegroundColor Yellow
}