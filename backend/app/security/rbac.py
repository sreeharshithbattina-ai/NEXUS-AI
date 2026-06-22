from enum import Enum
from typing import Dict, Any, List

class AccessRole(str, Enum):
    GUEST = "Guest"
    OPERATOR = "Operator"
    KERNEL_ADMIN = "KernelAdmin"

class RBACManager:
    """Enforces dynamic rule limits over sensitive kernel/system operational tasks."""
    def __init__(self):
        self._role_permissions = {
            AccessRole.GUEST: [
                "read_logs", "list_processes", "view_metrics"
            ],
            AccessRole.OPERATOR: [
                "read_logs", "list_processes", "view_metrics",
                "voice_input", "browser_navigate", "local_embeddings",
                "request_transcribe", "pair_device", "submit_delegation", "manage_plugin"
            ],
            AccessRole.KERNEL_ADMIN: [
                "read_logs", "list_processes", "view_metrics",
                "voice_input", "browser_navigate", "local_embeddings",
                "request_transcribe", "pair_device", "submit_delegation", "manage_plugin",
                "delete_logs", "kill_process", "admin_shell", "configure_secrets"
            ]
        }

    def has_clearance(self, role: AccessRole, required_action: str) -> bool:
        """Determines if the given role contains scope authorization."""
        permissions = self._role_permissions.get(role, [])
        return required_action in permissions

global_rbac_manager = RBACManager()
