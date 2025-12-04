# services/file_tool.py
import os


def file_crud(action: str, args: str, base_path: str):
    full_path = os.path.join(base_path, args.split()[0]) if args else ""
    if action == "read":
        if os.path.exists(full_path):
            with open(full_path, "r") as f:
                content = f.read()
                return content[:500] + "..." if len(content) > 500 else content
        return "[ERROR] Plik nie istnieje"
    elif action == "write":
        content = args.split(" ", 1)[1] if " " in args else ""
        os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return "Zapisano!"
    elif action == "delete":
        if os.path.exists(full_path):
            os.remove(full_path)
            return "Usunięto!"
        return "[ERROR] Nie znaleziono"
    elif action == "list":
        return "\n".join(os.listdir(base_path))
    else:
        return "Komenda: read/write/delete/list path"
