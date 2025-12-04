import os
import shutil
from typing import List


def apply_patches(patch_text: str, base_path: str) -> List[str]:
    """
    Aplikuje zmiany w plikach wewnątrz base_path.
    """
    if not patch_text:
        return []

    lines = patch_text.splitlines()
    current_file = None
    buffer = []
    in_code = False
    modified_files: List[str] = []

    for line in lines:
        if line.startswith("FILE:"):
            if current_file and buffer:
                _write_file(current_file, "\n".join(buffer), base_path)
                modified_files.append(current_file)
                buffer = []

            # Usuń ewentualne prefiksy ścieżek, jeśli AI zwariuje
            raw_path = line[len("FILE:"):].strip()
            current_file = raw_path.replace("workspace/project/", "").strip("/")

            in_code = False
            continue

        if line.strip().startswith("```"):
            in_code = not in_code
            continue

        if line.strip() == "END_FILE":
            if current_file and buffer:
                _write_file(current_file, "\n".join(buffer), base_path)
                modified_files.append(current_file)
            current_file = None
            buffer = []
            in_code = False
            continue

        if in_code and current_file:
            buffer.append(line)

    if current_file and buffer:
        _write_file(current_file, "\n".join(buffer), base_path)
        modified_files.append(current_file)

    return modified_files


def _write_file(rel_path: str, content: str, base_dir: str) -> None:
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if os.path.exists(full_path):
        shutil.copy(full_path, full_path + ".bak")

    with open(full_path, "w", encoding="utf8") as f:
        f.write(content)
