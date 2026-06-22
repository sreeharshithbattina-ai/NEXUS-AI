import semver
from typing import Dict, Any, List, Type
from .plugin_base import NexusPluginBase
from .permission_manifest import global_plugin_permission_verifier

class PluginManager:
    """Oversees dynamic third-party package loads, checking version rules and intercepts."""
    def __init__(self):
        self._loaded_plugins: Dict[str, NexusPluginBase] = {}
        self.kernel_api_version = "1.2.0"

    def register_plugin(self, plugin: NexusPluginBase) -> Dict[str, Any]:
        """Loads and initializes a valid custom plugin wrapper."""
        # 1. Version compatibility assertion
        # Simple wildcard checks (e.g., ^1.0.0 represents major version matching)
        if not plugin.nexus_api_version.startswith("^1."):
            return {"success": False, "reason": "Incompatible API version boundary"}
            
        # 2. Permissions validation
        has_clearance = global_plugin_permission_verifier.validate_plugin_permissions(
            plugin.name, plugin.required_permissions
        )
        if not has_clearance:
            return {
                "success": False, 
                "reason": "Missing security consent for requested scopes",
                "missing_scopes": plugin.required_permissions
            }
            
        # 3. Instantiate plugin
        success = plugin.on_load()
        if success:
            plugin.enabled = True
            self._loaded_plugins[plugin.name] = plugin
            return {"success": True, "plugin_name": plugin.name, "status": "active"}
            
        return {"success": False, "reason": "on_load() setup handler failed"}

    def unload_plugin(self, plugin_name: str) -> bool:
        if plugin_name in self._loaded_plugins:
            plugin = self._loaded_plugins[plugin_name]
            plugin.on_unload()
            plugin.enabled = False
            del self._loaded_plugins[plugin_name]
            return True
        return False

    def trigger_intercepts(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Runs user commands sequentially across loaded plugins to adjust execution steps."""
        current_params = params
        for name, p in self._loaded_plugins.items():
            if p.enabled:
                current_params = p.on_intent_intercept(intent, current_params)
        return current_params

    def list_installed_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": p.name,
                "version": p.version,
                "enabled": p.enabled,
                "permissions": p.required_permissions,
                "api_compatibility": p.nexus_api_version
            } for p in self._loaded_plugins.values()
        ]

global_plugin_manager = PluginManager()
