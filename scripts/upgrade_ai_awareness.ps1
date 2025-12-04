Write-Host "=== RegisLite SELF-AWARENESS UPDATE (Pancerny) ===" -ForegroundColor Cyan
Set-Location (Split-Path $MyInvocation.MyCommand.Path)

# Budujemy kod Pythona jako listę linii - to jest odporne na formatowanie czatu
$lines = @(
    'import traceback',
    'import sys',
    'import platform',
    'import os',
    'from typing import Dict, List',
    'from ai.chatgpt_client import ask',
    '',
    '# --- DYNAMICZNA DETEKCJA ŚRODOWISKA ---',
    '# AI dowie się o systemie w momencie uruchomienia',
    'PYTHON_VER = f"{sys.version_info.major}.{sys.version_info.minor}"',
    'OS_SYSTEM = platform.system()',
    'OS_RELEASE = platform.release()',
    'OS_NAME = f"{OS_SYSTEM} {OS_RELEASE}"',
    'PATH_SEP = os.sep',
    '',
    'PATCH_INSTRUCTIONS = f"""',
    'Jesteś Starszym Inżynierem Oprogramowania (Senior Python Dev).',
    '',
    '[[ TWOJE ŚRODOWISKO ]]',
    '- System: {OS_NAME}',
    '- Python: {PYTHON_VER}',
    '- Separator ścieżek: \'{PATH_SEP}\' (Używaj go w instrukcjach FILE)',
    '- Internet: TAK (Dostępny)',
    '- Uprawnienia: Pełny dostęp do plików w workspace/project',
    '',
    '[[ TWOJE ZADANIE ]]',
    'Napraw błędy w kodzie lub przeprowadź audyt.',
    'Dostosuj sugestie (np. komendy terminala) do systemu {OS_SYSTEM}.',
    '',
    '[[ FORMAT ODPOWIEDZI ]]',
    'Zwróć TYLKO kod w blokach. Bez wstępów.',
    '',
    'FILE: sciezka{PATH_SEP}do{PATH_SEP}pliku.py',
    '```python',
    '<nowa_tresc>',
    '```',
    'END_FILE',
    '',
    'Jeśli kod jest poprawny: NO_CHANGES_NEEDED',
    '"""',
    '',
    'def _format_files(files: List[Dict[str, str]]) -> str:',
    '    formatted = []',
    '    # Limit plików dla kontekstu (max 20)',
    '    for f in files[:20]: ',
    '        path = f["path"]',
    '        content = f.get("content", "")',
    '        if len(content) > 30000:',
    '            content = f"<PLIK ZA DUŻY - {len(content)} znaków - TREŚĆ POMINIĘTA>"',
    '        formatted.append(f"=== PLIK: {path} ===\n{content}\n")',
    '    return "\n".join(formatted)',
    '',
    'async def generate_patches(errors: str, files: List[Dict[str, str]]) -> str:',
    '    files_str = _format_files(files)',
    '    ',
    '    # Dodajemy nagłówek techniczny',
    '    header = f"SYSTEM: {OS_NAME} | Python {PYTHON_VER} | CWD: {os.getcwd()}"',
    '    ',
    '    prompt = f"{PATCH_INSTRUCTIONS}\n\n[{header}]\n\nZADANIE/BŁĘDY:\n{errors}\n\nPLIKI:\n{files_str}"',
    '',
    '    try:',
    '        return await ask(prompt)',
    '    except Exception as e:',
    '        return f"LLM error: {traceback.format_exc()}"'
)

# Zapisujemy do pliku, łącząc linie znakiem nowej linii
$content = $lines -join "`n"
$content | Set-Content "debugger/debugger_fix.py" -Encoding UTF8

Write-Host "[OK] debugger_fix.py został zaktualizowany." -ForegroundColor Green
Write-Host "     AI będzie teraz świadome systemu: $([System.Environment]::OSVersion)" -ForegroundColor Gray
Write-Host "`n📢 Pamiętaj o restarcie start.bat!" -ForegroundColor Yellow