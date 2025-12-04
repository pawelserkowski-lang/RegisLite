from collections import defaultdict
from typing import List, Dict


class SessionManager:
    """
    Zarządza pamięcią sesji (historią czatu).
    """
    def __init__(self, max_history: int = 20):
        # W przyszłości można to zmienić na Redis/SQLite
        self._memory: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.max_history = max_history

    def add_message(self, session_id: str, role: str, content: str):
        self._memory[session_id].append({"role": role, "content": content})
        self._prune_history(session_id)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self._memory[session_id]

    def _prune_history(self, session_id: str):
        if len(self._memory[session_id]) > self.max_history:
            self._memory[session_id] = self._memory[session_id][-self.max_history:]
            # Opcjonalnie: można tu dodać logikę podsumowywania (summarization)
