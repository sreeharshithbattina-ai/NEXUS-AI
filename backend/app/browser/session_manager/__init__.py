import json
from typing import Dict, Any, List, Optional

class SessionManager:
    """Isolates and serializes browser cookie stores and local histories per-operator workspace."""
    def __init__(self):
        self._user_sessions: Dict[str, List[Dict[str, Any]]] = {}

    def save_session(self, user_id: str, cookies: List[Dict[str, Any]]) -> bool:
        self._user_sessions[user_id] = cookies
        return True

    def load_session(self, user_id: str) -> List[Dict[str, Any]]:
        return self._user_sessions.get(user_id, [])

    def clear_session(self, user_id: str) -> None:
        if user_id in self._user_sessions:
            del self._user_sessions[user_id]

global_session_manager = SessionManager()
