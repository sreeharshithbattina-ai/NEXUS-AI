import logging
from typing import List, Dict, Any
from ..event_manager import global_event_bus

logger = logging.getLogger("startup_manager")

class StartupManager:
    def __init__(self):
        self._startup_items: List[Dict[str, Any]] = [
            {"id": "sys-terminal", "command": "echo 'Initializing Terminal Terminal Shell...'", "enabled": True},
            {"id": "sys-rag-refresh", "command": "python -m app.rag.reindex", "enabled": False}
        ]

    def register_startup_command(self, item_id: str, command: str, enabled: bool = True) -> Dict[str, Any]:
        item = {"id": item_id, "command": command, "enabled": enabled}
        # Avoid duplicate registering
        self._startup_items = [i for i in self._startup_items if i["id"] != item_id]
        self._startup_items.append(item)
        return item

    def get_startup_items(self) -> List[Dict[str, Any]]:
        return self._startup_items

    def execute_startup_sequence(self, executor_callback) -> Dict[str, Any]:
        """Runs enabled commands upon boot execution."""
        results = []
        for item in self._startup_items:
            if item["enabled"]:
                try:
                    res = executor_callback(item["command"])
                    results.append({"id": item["id"], "success": True, "output": res})
                except Exception as e:
                    results.append({"id": item["id"], "success": False, "error": str(e)})

        global_event_bus.emit(
            "StartupSequenceCompleted",
            "StartupManager",
            {"executed_count": len(results)}
        )
        return {"status": "success", "results": results}

global_startup_manager = StartupManager()
