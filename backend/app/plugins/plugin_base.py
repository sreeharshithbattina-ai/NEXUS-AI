from typing import Dict, Any, List

class NexusPluginBase:
    """Rigid skeletal base class representing a third-party OS customization module."""
    def __init__(self, name: str, version: str, required_permissions: List[str]):
        self.name = name
        self.version = version
        self.required_permissions = required_permissions
        self.enabled = False
        self.nexus_api_version = "^1.0.0"

    def on_load(self) -> bool:
        """Executed during operating system register cycles."""
        return True

    def on_session_start(self, user_session_id: str) -> None:
        """Triggers when operator creates active session workspace."""
        pass

    def on_intent_intercept(self, intent: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Intercepts, edits, or filters user intents before they are sent to the controller."""
        return parameters

    def on_unload(self) -> None:
        """Executed prior to un-mounting/purging active plugin cache."""
        pass
