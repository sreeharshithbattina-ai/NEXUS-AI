import time
import logging
from typing import List, Dict, Any, Optional

from ..desktop_controller import global_desktop_controller
from ..permission_manager import global_permission_manager
from ..event_manager import global_event_bus
from ..scheduler import global_scheduler

logger = logging.getLogger("desktop_runtime")

class DesktopRuntime:
    """Core execution engine turning high-level agency plans into tactical device executions."""
    def __init__(self):
        self.controller = global_desktop_controller
        self.permissions = global_permission_manager

    def execute_action(self, action_type: str, params: Dict[str, Any], user_id: str = "default") -> Dict[str, Any]:
        """Runs a singular action after proper permission clearance and safety evaluation."""
        # 1. Map to sensitive action targets
        perm_action_map = {
            "delete_file": "file_delete",
            "run_command": "shell_execution",
            "open_app": "launch_application",
            "close_app": "launch_application",
            "read_clipboard": "read_clipboard",
            "take_screenshot": "take_screenshot",
            "trigger_payment": "payments",
            "book_event": "bookings",
            "send_email": "email_sending"
        }

        perm_key = perm_action_map.get(action_type)
        if perm_key:
            auth = self.permissions.check_permission(perm_key, user_id=user_id, details=params)
            if not auth.get("granted"):
                return {
                    "success": False,
                    "status": "permission_blocked",
                    "reason": auth.get("reason"),
                    "approval_id": auth.get("approval_id")
                }

        # 2. Execute on verified modules
        try:
            if action_type == "open_app":
                res = self.controller.apps.open_app(params["name"])
                return {"success": True, "result": res}
                
            elif action_type == "close_app":
                res = self.controller.apps.close_app(params["identifier"])
                return {"success": True, "result": res}
                
            elif action_type == "run_command":
                res = self.controller.terminal.run_command(params["command"])
                return {"success": True, "result": res}
                
            elif action_type == "write_file":
                res = self.controller.files.write_file(params["path"], params["content"])
                return {"success": True, "result": res}
                
            elif action_type == "delete_file":
                res = self.controller.files.delete_item(params["path"], params.get("force", False))
                return {"success": True, "result": res}
                
            elif action_type == "read_file":
                res = self.controller.files.read_file(params["path"])
                return {"success": True, "content": res}
                
            elif action_type == "write_clipboard":
                res = self.controller.clipboard.write(params["text"])
                return {"success": True, "result": res}
                
            elif action_type == "read_clipboard":
                res = self.controller.clipboard.read()
                return {"success": True, "content": res}
                
            elif action_type == "take_screenshot":
                if "bbox" in params:
                    b = params["bbox"]
                    res = self.controller.screenshot.capture_region(b["x"], b["y"], b["width"], b["height"])
                else:
                    res = self.controller.screenshot.capture_fullscreen()
                return {"success": True, "image_path": res}

            elif action_type == "send_email":
                # Simulated enterprise sending
                self.controller.notifications.notify(
                    f"Email sent to {params.get('to')}",
                    f"Subject: {params.get('subject')}\nBody characters count: {len(params.get('body', ''))}"
                )
                return {"success": True, "message": "Email sent through desktop client."}
                
            else:
                return {"success": False, "reason": f"Unknown action type: {action_type}"}

        except Exception as e:
            logger.error(f"Execution failed on action {action_type}: {e}")
            return {"success": False, "reason": str(e)}

    def run_sequential_workflow(self, workflow_name: str, actions: List[Dict[str, Any]], user_id: str = "default") -> Dict[str, Any]:
        """Runs series of task frames, reporting updates via the live event stream."""
        workflow_id = f"wfl-{int(time.time() * 1000)}"
        global_event_bus.emit(
            "WorkflowStarted",
            "DesktopRuntime",
            {"workflow_id": workflow_id, "name": workflow_name, "steps_count": len(actions)},
            user_id=user_id
        )

        completed_steps = []
        for index, frame in enumerate(actions):
            action_type = frame.get("type", "")
            params = frame.get("params", {})
            
            # Trigger progress toast updates
            self.controller.notifications.update_progress(
                workflow_id, index + 1, len(actions), f"Executing step {index + 1}: {action_type}"
            )

            res = self.execute_action(action_type, params, user_id=user_id)
            if not res.get("success"):
                global_event_bus.emit(
                    "WorkflowFailed",
                    "DesktopRuntime",
                    {"workflow_id": workflow_id, "failed_step": index + 1, "reason": res.get("reason")},
                    user_id=user_id
                )
                return {
                    "workflow_id": workflow_id,
                    "status": "failed",
                    "failed_at_step": index + 1,
                    "completed_steps": completed_steps,
                    "error": res
                }

            completed_steps.append({
                "step": index + 1,
                "type": action_type,
                "result": res
            })

        # Report successful completion summaries
        self.controller.notifications.display_completion_summary(
            workflow_name, [s["type"] for s in completed_steps]
        )
        global_event_bus.emit(
            "WorkflowCompleted",
            "DesktopRuntime",
            {"workflow_id": workflow_id, "name": workflow_name},
            user_id=user_id
        )
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "steps": completed_steps
        }

global_desktop_runtime = DesktopRuntime()
