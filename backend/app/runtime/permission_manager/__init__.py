import logging
from typing import Dict, Any, Optional, List
from ..event_manager import global_event_bus

logger = logging.getLogger("permission_manager")

class PermissionManager:
    def __init__(self):
        # Default policies for critical operations: "allow", "deny", or "ask"
        self._policies: Dict[str, str] = {
            "file_delete": "ask",
            "shell_execution": "ask",
            "launch_application": "allow",
            "read_clipboard": "allow",
            "take_screenshot": "allow",
            "payments": "deny",
            "bookings": "ask",
            "email_sending": "ask"
        }
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}

    def get_policies(self) -> Dict[str, str]:
        return self._policies

    def set_policy(self, action: str, policy: str) -> bool:
        if policy not in ["allow", "deny", "ask"]:
            return False
        self._policies[action] = policy
        global_event_bus.emit(
            "PolicyUpdated",
            "PermissionManager",
            {"action": action, "new_policy": policy}
        )
        return True

    def check_permission(self, action: str, user_id: str = "default", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        policy = self._policies.get(action, "ask")
        if policy == "allow":
            global_event_bus.emit(
                "PermissionGranted",
                "PermissionManager",
                {"action": action, "policy": "allow", "details": details},
                user_id=user_id
            )
            return {"granted": True, "mode": "automatic", "reason": f"Policy '{action}' is pre-approved."}
        
        if policy == "deny":
            global_event_bus.emit(
                "PermissionDenied",
                "PermissionManager",
                {"action": action, "policy": "deny", "details": details},
                user_id=user_id
            )
            return {"granted": False, "mode": "automatic", "reason": f"Policy '{action}' is strictly blocked for security."}

        # For "ask" mode, we will log a pending prompt requirement
        import uuid
        approval_id = f"appr-{str(uuid.uuid4())[:8]}"
        self._pending_approvals[approval_id] = {
            "id": approval_id,
            "action": action,
            "details": details or {},
            "user_id": user_id,
            "status": "pending"
        }
        
        global_event_bus.emit(
            "PermissionPrompted",
            "PermissionManager",
            {"action": action, "approval_id": approval_id, "details": details},
            user_id=user_id
        )

        return {
            "granted": False,
            "mode": "ask",
            "approval_id": approval_id,
            "reason": f"Policy for '{action}' requires user intervention approval."
        }

    def resolve_approval(self, approval_id: str, approved: bool, user_id: str = "default") -> bool:
        if approval_id not in self._pending_approvals:
            return False
        
        record = self._pending_approvals[approval_id]
        if record["status"] != "pending":
            return False
            
        record["status"] = "approved" if approved else "rejected"
        action = record["action"]
        
        event_name = "PermissionGranted" if approved else "PermissionDenied"
        global_event_bus.emit(
            event_name,
            "PermissionManager",
            {"action": action, "approval_id": approval_id, "details": record["details"], "mode": "interactive"},
            user_id=user_id
        )
        return True

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        return list(self._pending_approvals.values())

global_permission_manager = PermissionManager()
