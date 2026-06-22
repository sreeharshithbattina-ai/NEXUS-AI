import copy
from typing import Dict, Any, List

class ConflictResolver:
    """Reconciles differences between diverging database registers on dynamic peer sync tracks."""
    def __init__(self):
        pass

    def reconcile_items(self, local_item: Dict[str, Any], remote_item: Dict[str, Any]) -> Dict[str, Any]:
        """Runs conflict reconciliation policies based on timestamp markers."""
        # Clean copy
        local = copy.deepcopy(local_item)
        remote = copy.deepcopy(remote_item)
        
        # Determine LWW (Last-Write-Wins)
        local_time = local.get("updated_at") or local.get("timestamp") or 0.0
        remote_time = remote.get("updated_at") or remote.get("timestamp") or 0.0
        
        if remote_time > local_time:
            # If both have preference settings, perform a structural dictionary merge
            if isinstance(local.get("settings"), dict) and isinstance(remote.get("settings"), dict):
                merged_settings = self.deep_merge(local["settings"], remote["settings"])
                item = remote
                item["settings"] = merged_settings
                item["resolved_via"] = "lww-deep-merge"
                return item
            
            remote["resolved_via"] = "lww-remote-wins"
            return remote
            
        # Local wins or equal
        if isinstance(local.get("settings"), dict) and isinstance(remote.get("settings"), dict):
            merged_settings = self.deep_merge(remote["settings"], local["settings"])
            item = local
            item["settings"] = merged_settings
            item["resolved_via"] = "lww-deep-merge"
            return item
            
        local["resolved_via"] = "lww-local-wins"
        return local

    def deep_merge(self, base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively matches dictionary trees, aligning differing settings leaf pairs."""
        merged = copy.deepcopy(base)
        for k, v in incoming.items():
            if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = self.deep_merge(merged[k], v)
            else:
                merged[k] = copy.deepcopy(v)
        return merged

global_conflict_resolver = ConflictResolver()
