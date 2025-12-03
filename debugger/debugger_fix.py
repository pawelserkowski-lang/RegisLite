import traceback
from typing import List, Dict
from ai.chatgpt_client import ask

PATCH_INSTRUCTIONS = """
Jesteś asystentem AI naprawiającym kod.

Zwróć poprawki TYLKO w następującym formacie (bez dodatkowego komentarza, bez wyjaśnień):

FILE: <ścieżka_pliku_od_workspace/project_w_dół_lub_pełna_ścieżka>
```python
<pełna, poprawiona treść pliku>
