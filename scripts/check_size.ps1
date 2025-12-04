# check_size.ps1
$limit = 50MB
Write-Host "🔍 Skanowanie w poszukiwaniu grubasów (>50MB)..." -ForegroundColor Cyan

# Pobiera wszystkie pliki, pomijając .git
$files = Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch "\\.git\\" }

$found = $false
foreach ($file in $files) {
    if ($file.Length -gt $limit) {
        # Sprawdź czy plik jest ignorowany przez git
        $isIgnored = git check-ignore "$($file.FullName)"
        
        if (-not $isIgnored) {
            Write-Host "❌ ALARM: '$($file.Name)' waży $([math]::round($file.Length / 1MB, 2)) MB!" -ForegroundColor Red
            Write-Host "   -> Dodaj go do .gitignore!" -ForegroundColor Yellow
            $found = $true
        }
    }
}

if (-not $found) {
    Write-Host "✅ Czysto! Brak wielkich plików do wysłania." -ForegroundColor Green
}