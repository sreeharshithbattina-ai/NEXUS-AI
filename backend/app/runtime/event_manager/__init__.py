import time
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime

class RuntimeEvent:
    def __init__(self, event_type: str, source: str, payload: Dict[str, Any], user_id: str):
        self.id = f"ev-{int(time.time() * 1000)}"
        self.timestamp = datetime.utcnow().isoformat()
        self.type = event_type
        self.source = source
        self.payload = payload
        self.user_id = user_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "type": self.type,
            "source": self.source,
            "payload": self.payload,
            "userId": self.user_id
        }

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[RuntimeEvent], None]]] = {}
        self._history: List[RuntimeEvent] = []
        self._max_history = 200

    def subscribe(self, event_type: str, callback: Callable[[RuntimeEvent], None]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def emit(self, event_type: str, source: str, payload: Dict[str, Any], user_id: str = "default") -> RuntimeEvent:
        event = RuntimeEvent(event_type, source, payload, user_id)
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        # Notify direct subscribers
        for callback in self._listeners.get(event_type, []):
            try:
                callback(event)
            except Exception:
                pass

        # Notify wildcard list listeners if configured
        for callback in self._listeners.get("*", []):
            try:
                callback(event)
            except Exception:
                pass

        return event

    def get_history(self, limit: int = 50, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        filtered = self._history
        if user_id:
            filtered = [e for e in filtered if e.user_id == user_id]
        return [e.to_dict() for e in reversed(filtered[-limit:])]

    def clear(self):
        self._history.clear()

global_event_bus = EventBus()
