from .event_manager import global_event_bus
from .permission_manager import global_permission_manager
from .desktop_controller import global_desktop_controller
from .desktop_runtime import global_desktop_runtime
from .scheduler import global_scheduler
from .activity_monitor import global_activity_monitor
from .startup_manager import global_startup_manager

__all__ = [
    "global_event_bus",
    "global_permission_manager",
    "global_desktop_controller",
    "global_desktop_runtime",
    "global_scheduler",
    "global_activity_monitor",
    "global_startup_manager"
]
