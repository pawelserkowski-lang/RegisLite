# debugger/analyzer.py
import os

def simple_scan(project_path: str):
    errors = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, encoding="utf-8") as f:
                        lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if "print(" in line and not line.strip().startswith("#"):
                            errors.append({
                                "file": os.path.relpath(path, project_path),
                                "line": i,
                                "message": "Znaleziono debug print() – klasyka polskiego debugowania"
                            })
                except:
                    pass
    return errors or [{"file": "README.md", "line": 1, "message": "Kod czysty jak łza! Nie ma błędy!"}]
