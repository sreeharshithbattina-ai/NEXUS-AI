import time
import logging
from typing import List, Dict, Any, Optional
from ..event_manager import global_event_bus

logger = logging.getLogger("activity_monitor")

class ActivityMonitor:
    def __init__(self):
        self._tracking_enabled: bool = False
        self._session_start_time: float = time.time()
        
        # Keep list of timeline ticks
        self._activities: List[Dict[str, Any]] = [
            {"timestamp": time.time() - 3600, "app": "Visual Studio Code", "category": "coding", "duration_sec": 1200},
            {"timestamp": time.time() - 2400, "app": "Slack", "category": "meeting", "duration_sec": 600},
            {"timestamp": time.time() - 1800, "app": "Chrome", "category": "browsing", "duration_sec": 900}
        ]

    def set_tracking(self, enabled: bool) -> bool:
        self._tracking_enabled = enabled
        global_event_bus.emit(
            "TrackingStateChanged",
            "ActivityMonitor",
            {"enabled": enabled}
        )
        return enabled

    def is_tracking_enabled(self) -> bool:
        return self._tracking_enabled

    def record_activity(self, app_name: str, category: str, duration_sec: int) -> None:
        """Appends interactive event ticks to current session log if enabled."""
        if not self._tracking_enabled:
            return

        activity = {
            "timestamp": time.time(),
            "app": app_name,
            "category": category,
            "duration_sec": duration_sec
        }
        self._activities.append(activity)
        global_event_bus.emit(
            "ActivityLogged",
            "ActivityMonitor",
            activity
        )

    def get_summary(self) -> Dict[str, Any]:
        """Provides activity reports securely only if the owner has requested tracking."""
        if not self._tracking_enabled:
            return {
                "tracking_status": "disabled",
                "message": "User activity tracking is currently disabled. Enable to inspect workflow stats.",
                "total_work_minutes": 0,
                "categories": {}
            }

        # Calculate durations safely
        categories: Dict[str, int] = {}
        apps: Dict[str, int] = {}
        total_sec = 0

        for act in self._activities:
            cat = act["category"]
            app = act["app"]
            dur = act["duration_sec"]
            
            categories[cat] = categories.get(cat, 0) + dur
            apps[app] = apps.get(app, 0) + dur
            total_sec += dur

        return {
            "tracking_status": "enabled",
            "total_work_minutes": round(total_sec / 60, 1),
            "idle_minutes": 4.5, # static/simulated idle time
            "categories_seconds": categories,
            "apps_seconds": apps,
            "productivity_score": 85.0 if total_sec > 0 else 0.0,
            "timeline": self._activities[-10:] # last 10 entries
        }

global_activity_monitor = ActivityMonitor()
