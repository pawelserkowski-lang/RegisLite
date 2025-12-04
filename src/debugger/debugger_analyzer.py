import os
from typing import List, Dict


def scan_project(base_path: str) -> List[Dict[str, str]]:
    """
    Skanuje projekt, ale OMIJA foldery systemowe i biblioteki.
    """
    result = []

    # Lista folderów do ignorowania (czarna lista)
    IGNORE_DIRS = {
        "node_modules", "venv", ".venv", ".git", "__pycache__",
        "dist", "build", "coverage", ".idea", ".vscode"
    }

    # Lista rozszerzeń do ignorowania (binarki, mapy, obrazki)
    IGNORE_EXT = {
        ".map", ".png", ".jpg", ".jpeg", ".gif", ".ico",
        ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin",
        ".lock", ".json", ".zip", ".tar", ".gz"
    }

    if not os.path.exists(base_path):
        return result

    for root, dirs, files in os.walk(base_path):
        # 1. Modyfikujemy 'dirs' in-place, żeby os.walk nie wchodził w śmieci
        # (to jest kluczowe dla wydajności!)
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for name in files:
            # 2. Ignorujemy pliki po rozszerzeniu
            _, ext = os.path.splitext(name)
            if ext.lower() in IGNORE_EXT:
                continue

            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, base_path)

            try:
                # Limit wielkości pojedynczego pliku (np. max 100KB), żeby nie zatkać AI
                if os.path.getsize(full_path) > 100 * 1024:
                    continue

                with open(full_path, "r", encoding="utf8") as f:
                    content = f.read()
                    result.append({"path": rel_path, "content": content})
            except Exception:
                # Ignorujemy pliki, których nie da się przeczytać (np. binarne)
                pass

    return result
