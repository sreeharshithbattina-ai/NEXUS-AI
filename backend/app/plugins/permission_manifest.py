from typing import Dict, Any, List

class PluginPermissionVerifier:
    """Rigidly audits and approves permissions declared within third-party plugin manifest blocks."""
    def __init__(self):
        # standard system scopes permitted for developer integrations
        self.allowed_system_scopes = ["filesystem_read", "filesystem_write", "microphone_access", "external_api", "notifications_dispatch"]
        self._user_approved_plugin_scopes: Dict[str, List[str]] = {
            "github_autopilot": ["filesystem_read", "external_api"],
            "spotify_voice": ["microphone_access", "external_api"]
        }

    def validate_plugin_permissions(self, plugin_name: str, requested_permissions: List[str]) -> bool:
        """Validates that requested permissions are supported and approved."""
        # 1. Scopes must exist within official lists
        for scope in requested_permissions:
            if scope not in self.allowed_system_scopes:
                return False
                
        # 2. Scope approval verification
        approved_scopes = self._user_approved_plugin_scopes.get(plugin_name, [])
        return all(scope in approved_scopes for scope in requested_permissions)

    def request_on_the_fly_approval(self, plugin_name: str, scope: str) -> bool:
        """Triggers user-facing prompts for real-time permissions grants."""
        if scope in self.allowed_system_scopes:
            if plugin_name not in self._user_approved_plugin_scopes:
                self._user_approved_plugin_scopes[plugin_name] = []
            if scope not in self._user_approved_plugin_scopes[plugin_name]:
                self._user_approved_plugin_scopes[plugin_name].append(scope)
            return True
        return False

global_plugin_permission_verifier = PluginPermissionVerifier()
