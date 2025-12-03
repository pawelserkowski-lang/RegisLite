import traceback
from typing import Dict, List

from ai.chatgpt_client import ask

PATCH_INSTRUCTIONS = """
Jesteś asystentem AI naprawiającym kod.
Zwróć poprawki TYLKO w następującym formacie (bez dodatkowego komentarza, bez wyjaśnień):
FILE: <ścieżka_pliku_od_workspace/project_w_dół_lub_pełna_ścieżka>
```python
<pełna, poprawiona treść pliku>
```
END_FILE

Zasady:
- Nie dodawaj komentarzy poza powyższym formatem.
- Jeśli plik nie istnieje, NIE twórz go — odpowiadaj tylko dla istniejących ścieżek.
- Upewnij się, że ścieżki są zgodne z aktualną strukturą projektu.
- Zwracaj pełną zawartość każdego zmienianego pliku.

Plan: najpierw wypisz krótki plan zmian w 1-3 punktach, potem przedstaw patch zgodnie z formatem.
"""


def _format_files(files: List[Dict[str, str]]) -> str:
    formatted = []
    for f in files:
        formatted.append(f"FILE: {f['path']}")
        formatted.append("```")
        formatted.append(f.get("content", ""))
        formatted.append("```")
    return "\n".join(formatted)


async def generate_patches(errors: str, files: List[Dict[str, str]]) -> str:
    """
    Buduje prompt dla modelu na podstawie wykrytych błędów i zawartości plików.
    Zwraca tekst patchy wygenerowany przez model lub opis błędu.
    """
    prompt = f"{PATCH_INSTRUCTIONS}\n\nBłędy: {errors}\n\nPliki:\n{_format_files(files)}"

    try:
        return await ask(prompt)
    except Exception:
        return f"LLM error: {traceback.format_exc()}"
