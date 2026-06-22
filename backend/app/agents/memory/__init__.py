from typing import Dict, Any, List
from ..base import BaseAgent

class MemoryAgent(BaseAgent):
    """Memory Agent reviews task traces to summarize and serialize declarative facts."""
    def __init__(self, model_manager=None):
        super().__init__("memory_agent", "NEXUS Memory Registrar", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
        return ["context recall", "semantic compression", "preference categorization"]

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"interaction_logs": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"extracted_preferences": {"type": "array"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            f"As NEXUS Memory Registrar, extract core facts or behavioral preference indices from this sequence:\n'{task}'\n"
            f"Active Workspace Context: {context}"
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else f"Preferences reviewed for: '{task}'."
        return {
            "summary": resp,
            "extracted_preferences": [{"category": "Preference", "fact": f"Extracted from {task[:30]}"}],
            "confidence_score": 0.95
        }
