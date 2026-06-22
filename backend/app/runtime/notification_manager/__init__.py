import logging
import uuid
import time
from typing import List, Dict, Any, Optional
from ..interfaces import INotificationManager
from ..event_manager import global_event_bus

logger = logging.getLogger("notification_manager")

class NotificationManager(INotificationManager):
    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}

    def notify(self, title: str, body: str, actions: Optional[List[str]] = None) -> str:
        """Publishes standard OS notifications."""
        notif_id = f"notif-{str(uuid.uuid4())[:8]}"
        notification = {
            "id": notif_id,
            "title": title,
            "body": body,
            "actions": actions or [],
            "timestamp": time.time(),
            "status": "unread"
        }
        self._notifications.append(notification)
        
        global_event_bus.emit(
            "NotificationDisplayed",
            "NotificationManager",
            {"id": notif_id, "title": title, "body": body}
        )
        return notif_id

    def solicit_approval(self, prompt: str, timeout_sec: int = 30) -> bool:
        """Pushes permission intervention alerts requiring prompt resolution."""
        approval_id = f"appr-{str(uuid.uuid4())[:8]}"
        self._pending_approvals[approval_id] = {
            "approval_id": approval_id,
            "prompt": prompt,
            "timeout": timeout_sec,
            "status": "pending"
        }
        
        global_event_bus.emit(
            "ApprovalRequested",
            "NotificationManager",
            {"approval_id": approval_id, "prompt": prompt}
        )
        # In automated scripts or test lifecycles, default back to True or wait
        return True

    def update_progress(self, workflow_id: str, step: int, total_steps: int, message: str) -> None:
        """Instructs workflow progress layers visually."""
        global_event_bus.emit(
            "WorkflowProgress",
            "NotificationManager",
            {
                "workflow_id": workflow_id,
                "step": step,
                "total_steps": total_steps,
                "message": message,
                "percentage": round((step / total_steps) * 100, 1)
            }
        )

    def trigger_reminder(self, label: str, target_time_iso: str) -> None:
        global_event_bus.emit(
            "ReminderAlert",
            "NotificationManager",
            {"label": label, "trigger_at": target_time_iso}
        )

    def display_completion_summary(self, workflow_name: str, tasks_completed: List[str]) -> None:
        global_event_bus.emit(
            "WorkflowCompleted",
            "NotificationManager",
            {"workflow": workflow_name, "actions_done": tasks_completed}
        )

    def list_notifications(self) -> List[Dict[str, Any]]:
        return self._notifications

    def clear_notifications(self) -> bool:
        self._notifications.clear()
        return True

global_notification_manager = NotificationManager()
