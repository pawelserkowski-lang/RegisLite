
---

### 7.4 `Regis/debugger/debugger_patcher.py`

```python
import os
import shutil
from typing import List


def apply_patches(patch_text: str) -> List[str]:
    """
    Oczekuje patch_text w formacie:

    FILE: relative/path.py
    ```python
    <nowa treść>
    ```
    END_FILE

    Zwraca listę zmodyfikowanych plików.
    """

    if not patch_text:
        return []

    lines = patch_text.splitlines()
    current_file = None
    buffer = []
    in_code = False
    modified_files: List[str] = []

    for line in lines:
        # Nowy blok pliku
        if line.startswith("FILE:"):
            # flush poprzedniego jeśli jakiś był
            if current_file and buffer:
                _write_file(current_file, "\n".join(buffer))
                modified_files.append(current_file)
                buffer = []

            current_file = line[len("FILE:"):].strip()
            in_code = False
            continue

        # przełącznik kodu ```...```
        if line.strip().startswith("```"):
            in_code = not in_code
            continue

        # koniec bloku pliku
        if line.strip() == "END_FILE":
            if current_file and buffer:
                _write_file(current_file, "\n".join(buffer))
                modified_files.append(current_file)
            current_file = None
            buffer = []
            in_code = False
            continue

        # linia kodu
        if in_code and current_file:
            buffer.append(line)

    # flush na końcu, gdyby model nie domknął END_FILE
    if current_file and buffer:
        _write_file(current_file, "\n".join(buffer))
        modified_files.append(current_file)

    return modified_files


def _write_file(relative_path: str, content: str) -> None:
    """
    Zapisuje content do pliku w workspace/project, robiąc backup jeśli plik istnieje.
    """
    base = "workspace/project"

    # jeśli model podał już pełną ścieżkę z "workspace/project", używamy jej
    if relative_path.startswith(base):
        full_path = relative_path
    else:
        full_path = os.path.join(base, relative_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if os.path.exists(full_path):
        backup_path = full_path + ".bak"
        shutil.copy(full_path, backup_path)

    with open(full_path, "w", encoding="utf8") as f:
        f.write(content)
