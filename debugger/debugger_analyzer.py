import os
from typing import List, Dict


def scan_project() -> List[Dict[str, str]]:
    """
    Skanuje workspace/project i zwraca listę:
    { 'path': ścieżka, 'content': zawartość }
    """
    base = "workspace/project"
    result = []

    if not os.path.exists(base):
        return result

    for root, _, files in os.walk(base):
        for name in files:
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf8") as f:
                    content = f.read()
            except Exception:
                content = ""
            result.append({"path": path, "content": content})

    return result
