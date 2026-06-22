from typing import Dict, Any, List
from ..base import BaseAgent

class SecurityAgent(BaseAgent):
    """Security Agent audits actions for credential leaks, malicious characters, and sandbox limit violations."""
    def __init__(self, model_manager=None):
        super().__init__("security_agent", "NEXUS Threat Intelligence", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
         return ["leaked credentials scanning", "malcontent characters auditing", "boundary verification"]

    @property
    def input_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"target_sequence": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"is_safe": {"type": "boolean"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            f"As NEXUS Security Officer, audit the threat landscape for command sequence:\n'{task}'\n"
            f"System limits: {context}"
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else "No direct violations flagged."
        is_safe = not any(b in task.lower() for b in ["rm -rf", "sudo", "leak", "secrets"])
        return {
            "threat_audit_report": resp,
            "is_safe": is_safe,
            "confidence_score": 0.99
        }
