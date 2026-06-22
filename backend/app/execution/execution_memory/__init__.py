import re
from typing import Dict, Any, List, Optional

class ExecutionMemory:
    """Provides session-scoped variables and parameter interpolation for workflow execution graphs."""
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def clear(self) -> None:
        self._store.clear()

    def set_step_output(self, step_id: str, output: Any) -> None:
        """Stores output from a specific completed step."""
        self._store[f"step_{step_id}_output"] = output

    def resolve_placeholders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Iterates over parameters and resolves string expressions like ${step_id.key}."""
        resolved = {}
        for k, v in params.items():
            if isinstance(v, str):
                resolved[k] = self._interpolate_string(v)
            elif isinstance(v, dict):
                resolved[k] = self.resolve_placeholders(v)
            elif isinstance(v, list):
                resolved[k] = [self._interpolate_string(item) if isinstance(item, str) else item for item in v]
            else:
                resolved[k] = v
        return resolved

    def _interpolate_string(self, text: str) -> Any:
        # Match pattern ${step-id.field-key}
        pattern = r"\$\{\s*([\w-]+)\.([\w_-]+)\s*\}"
        match = re.search(pattern, text)
        if not match:
            return text
            
        step_id = match.group(1)
        field_key = match.group(2)
        
        # Look up step output
        step_data = self._store.get(f"step_{step_id}_output")
        if step_data and isinstance(step_data, dict):
            val = step_data.get(field_key)
            if val is not None:
                # If the entire placeholder string was just the reference, return raw value (could be boolean, int etc)
                if text.strip() == match.group(0):
                    return val
                return text.replace(match.group(0), str(val))
                
        return text

global_execution_memory = ExecutionMemory()
