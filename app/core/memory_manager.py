# app/core/memory_manager.py
from typing import List, Dict, Any, Optional

class MemoryManager:
    """
    Lightweight MemoryManager stub to satisfy imports during tests.
    Extend this with real persistence/logic if needed.
    """
    def __init__(self):
        self._history: Dict[str, List[Dict[str, Any]]] = {}

    def add_message(self, user_id: str, role: str, text: str):
        self._history.setdefault(user_id, []).append({"role": role, "text": text})

    def get_recent_messages(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self._history.get(user_id, [])[-limit:]

    def clear(self, user_id: str):
        if user_id in self._history:
            del self._history[user_id]

    def get_last_viewed_product(self, user_id: str) -> Optional[Dict[str, Any]]:
        # used by some agents as a convenience; returning None is safe
        return None