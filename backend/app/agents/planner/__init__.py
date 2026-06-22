from typing import Dict, Any, List
from ..base import BaseAgent

class PlannerAgent(BaseAgent):
    """Planner Agent parses incoming intents and generates staging tracks."""
    def __init__(self, model_manager=None):
        super().__init__("planner_agent", "NEXUS Planning Architect", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
        return ["intent deconstruction", "subtask estimation", "tool matching"]

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"intent": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"stages": {"type": "array"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            f"As NEXUS Planning Architect, partition user requested intent:\n'{task}'\n"
            f"Context: {context}\n"
            "Generate logical micro-stages."
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else f"Staging tracks processed for '{task}' successfully."
        return {
            "plan_metadata": resp,
            "stages": [{"stage_id": 1, "name": "Refine context", "description": task}],
            "confidence_score": 0.95
        }
