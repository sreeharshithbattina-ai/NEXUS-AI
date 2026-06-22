from typing import Dict, Any, List, Optional
import uuid
import time
from ..interfaces import IApprovalManager
from ...runtime.permission_manager import global_permission_manager
from ...runtime.event_manager import global_event_bus

class ApprovalManager(IApprovalManager):
    """Integrates checking of sensitive activities with the PermissionManager to pause execution gates."""
    def __init__(self):
        self._active_tickets: Dict[str, Dict[str, Any]] = {}

    def requires_approval(self, action_type: str, params: Dict[str, Any]) -> bool:
        """Determines if the step-action falls in any of the six critical human-in-the-loop categories."""
        action_lower = action_type.lower()
        
        # 1. Money
        if "pay" in action_lower or "price" in action_lower or "purchase" in action_lower or "money" in action_lower or action_lower == "payments":
            return True
            
        # 2. Bookings
        if "book" in action_lower or "reservation" in action_lower or "schedule_job" in action_lower or action_lower == "bookings":
            return True
            
        # 3. File Deletion
        if "delete" in action_lower or "purge" in action_lower or "remove" in action_lower or action_lower == "file_delete":
            return True
            
        # 4. Terminal Commands
        if "command" in action_lower or "run_command" in action_lower or "shell" in action_lower or action_lower == "shell_execution":
            cmd = str(params.get("command", "")).lower()
            # If command attempts to execute administrative changes
            if any(term in cmd for term in ["rm", "sudo", "install", "format", "kill", "sh", "bash"]):
                return True
            
        # 5. Personal Information
        if "personal_info" in action_lower or "profile_update" in action_lower:
            return True
        # Inspect params for confidential keywords
        param_str = str(params).lower()
        if any(term in param_str for term in ["password", "secret", "cvv", "credit_card", "ssn", "private_key"]):
            return True

        # 6. External Communications
        if "email" in action_lower or "send" in action_lower or "post_api" in action_lower or action_lower == "email_sending":
            return True

        return False

    def suspend_for_approval(self, workflow_id: str, step_id: str, prompt: str) -> str:
        """Saves a placeholder ticket to halt loop flows until explicit operator resolution occurs."""
        ticket_id = f"appr-{str(uuid.uuid4())[:8]}"
        self._active_tickets[ticket_id] = {
            "id": ticket_id,
            "workflow_id": workflow_id,
            "step_id": step_id,
            "prompt": prompt,
            "status": "pending",
            "timestamp": time.time()
        }
        
        # Emits warning event to front dashboard
        global_event_bus.emit(
            "ApprovalRequested",
            "ApprovalManager",
            {"approval_id": ticket_id, "prompt": prompt, "workflow_id": workflow_id, "step_id": step_id}
        )
        return ticket_id

    def resolve_approval(self, approval_id: str, approved: bool) -> bool:
        """Resolves the suspended ticket and aligns status in global permission managers."""
        if approval_id in self._active_tickets:
            ticket = self._active_tickets[approval_id]
            ticket["status"] = "approved" if approved else "rejected"
            ticket["resolved_at"] = time.time()
            
            global_event_bus.emit(
                "ApprovalResolved",
                "ApprovalManager",
                {"approval_id": approval_id, "approved": approved, "workflow_id": ticket.get("workflow_id")}
            )
            return True
        
        # Falls back to query core permission manager
        return global_permission_manager.resolve_approval(approval_id, approved)

    def get_pending(self) -> List[Dict[str, Any]]:
        return [t for t in self._active_tickets.values() if t["status"] == "pending"]

global_approval_manager = ApprovalManager()
