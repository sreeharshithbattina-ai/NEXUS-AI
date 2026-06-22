import logging
from typing import Dict, Any, List, Optional

from ..application_manager import global_application_manager
from ..filesystem_manager import global_filesystem_manager
from ..terminal_manager import global_terminal_manager
from ..process_manager import global_process_manager
from ..clipboard_manager import global_clipboard_manager
from ..screenshot_manager import global_screenshot_manager
from ..notification_manager import global_notification_manager
from ..event_manager import global_event_bus

logger = logging.getLogger("desktop_controller")

class DesktopController:
    """Consolidated orchestration center for every physical aspect of the desktop environment."""
    def __init__(self):
        self.apps = global_application_manager
        self.files = global_filesystem_manager
        self.terminal = global_terminal_manager
        self.processes = global_process_manager
        self.clipboard = global_clipboard_manager
        self.screenshot = global_screenshot_manager
        self.notifications = global_notification_manager

    def get_aggregated_state(self) -> Dict[str, Any]:
        """Provides cohesive snapshot of the entire computer interface state."""
        return {
            "active_window": self.apps.get_active_window(),
            "clipboard_snippet": self.clipboard.read()[:100],
            "metrics": self.processes.get_system_metrics(),
            "notifications_unread": len(self.notifications.list_notifications()),
            "running_programs_count": len(self.apps.list_running_apps())
        }

global_desktop_controller = DesktopController()
