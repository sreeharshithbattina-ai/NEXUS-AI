import logging
from typing import List, Dict, Any, Optional
from ..interfaces import IClipboardManager
from ..event_manager import global_event_bus

logger = logging.getLogger("clipboard_manager")

class ClipboardManager(IClipboardManager):
    def __init__(self):
        self._current_content: str = "Welcome to NEXUS Desktop Workspace."
        self._history: List[str] = ["Welcome to NEXUS Desktop Workspace."]
        self._max_history = 50

    def read(self) -> str:
        # Check native system clipboard if pyperclip can import and is setup
        try:
            import pyperclip
            val = pyperclip.paste()
            if val and val != self._current_content:
                self.write(val, emit_event=False)
        except Exception:
            pass
        return self._current_content

    def write(self, data: str, emit_event: bool = True) -> bool:
        if not data:
            return False
            
        self._current_content = data
        if not self._history or self._history[-1] != data:
            self._history.append(data)
            if len(self._history) > self._max_history:
                self._history.pop(0)

        # Sync back to native system clipboard if GUI exists
        try:
            import pyperclip
            pyperclip.copy(data)
        except Exception:
            pass

        if emit_event:
            global_event_bus.emit(
                "ClipboardModified",
                "ClipboardManager",
                {"characters_count": len(data), "history_depth": len(self._history)}
            )
        return True

    def get_history(self) -> List[str]:
        return list(reversed(self._history))

    def clear_history(self) -> bool:
        self._history = [self._current_content]
        return True

global_clipboard_manager = ClipboardManager()
