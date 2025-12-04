import traceback
import sys
import platform
import os
from typing import Dict, List
from ai.chatgpt_client import ask

# Wykrywanie srodowiska
PYTHON_VER = f'{sys.version_info.major}.{sys.version_info.minor}'
OS_NAME = f'{platform.system()} {platform.release()}'
PATH_SEP = os.sep

# Instrukcje Promptu (uzywamy potrojnych cudzyslowow w zmiennej)
PATCH_INSTRUCTIONS = """
Jesteś Starszym Inżynierem (Senior Python Dev).

[[ TWOJE ŚRODOWISKO ]]
- System: {OS_NAME}
- Python: {PYTHON_VER}
- Separator: '{PATH_SEP}'
- Dostęp: PEŁNY

[[ ZADANIE ]]
Napraw błędy lub zrób audyt. Zwróć kod w blokach:

FILE: sciezka{PATH_SEP}plik.py
```python
<kod>
```
END_FILE

Jeśli OK: NO_CHANGES_NEEDED
"""

def _format_files(files: List[Dict[str, str]]) -> str:
    formatted = []
    for f in files[:20]:
        path = f['path']
        content = f.get('content', '')
        if len(content) > 30000: content = '<ZA DUŻY>'
        formatted.append(f'=== PLIK: {path} ===\n{content}\n')
    return '\n'.join(formatted)

async def generate_patches(errors: str, files: List[Dict[str, str]]) -> str:
    files_str = _format_files(files)
    header = f'SYSTEM: {OS_NAME} | CWD: {os.getcwd()}'
    prompt = f'{PATCH_INSTRUCTIONS}\n[{header}]\nZADANIE:\n{errors}\nPLIKI:\n{files_str}'
    try:
        return await ask(prompt)
    except Exception as e:
        return f'LLM error: {traceback.format_exc()}'