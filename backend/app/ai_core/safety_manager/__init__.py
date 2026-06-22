from typing import Dict, Any, Tuple, Optional

class SafetyManager:
    """
    Coordinates compliance audits on proposed tool calls or workflow actions.
    Gages risk levels and dynamically requests human approval blocks for critical sequences.
    """
    def __init__(self, override_allow_all: bool = False):
        self.override_allow_all = override_allow_all
        # Risk indicators
        self.gated_actions = [
            "payment", "purchase", "booking", "delete", "remove", 
            "terminal", "destructive", "email", "calendar"
        ]

    def assess_risk(self, target_type: str, action_details: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Assesses tool or action parameters.
        Returns Tuple: (requires_approval: bool, reason: str, approval_payload: Optional)
        """
        if self.override_allow_all:
            return False, "Override active; absolute trusted pathway.", None

        normalized_type = target_type.lower()
        
        # 1. Matches common gated action tags
        for trigger in self.gated_actions:
            if trigger in normalized_type:
                reason = f"Action type '{target_type}' involves high-risk operation '{trigger}'."
                approval_payload = {
                    "reason": reason,
                    "risk_level": "High" if trigger in ["payment", "purchase", "terminal", "delete"] else "Medium",
                    "requires_manual_confirmation": True,
                    "gated_operation": trigger,
                    "original_arguments": action_details
                }
                return True, reason, approval_payload

        # 2. Inspect inner parameters
        command = str(action_details.get("command", "")).lower()
        if command and any(bad in command for bad in ["rm", "sudo", "del", "format", "kill"]):
            reason = "Direct terminal instruction includes destructive triggers."
            return True, reason, {
                "reason": reason,
                "risk_level": "High",
                "requires_manual_confirmation": True,
                "gated_operation": "terminal",
                "original_arguments": action_details
            }

        action = str(action_details.get("action", "")).lower()
        if action in ["delete", "remove"]:
            reason = "File deletion trigger detected."
            return True, reason, {
                "reason": reason,
                "risk_level": "High",
                "requires_manual_confirmation": True,
                "gated_operation": "delete",
                "original_arguments": action_details
            }

        return False, "Trusted operation context confirmed.", None
