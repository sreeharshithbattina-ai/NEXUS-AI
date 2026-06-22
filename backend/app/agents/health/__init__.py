from typing import Dict, Any, List
from ..base import BaseAgent

class HealthAgent(BaseAgent):
    """Health Agent coordinates wellness logs and habit notifications (strictly avoids clinical diagnoses)."""
    def __init__(self, model_manager=None):
        super().__init__("health_agent", "NEXUS Lifestyle Consultant", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
         return ["wellness logging help", "hydration reminders", "posture habits checks"]

    @property
    def input_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"habits": {"type": "array"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"health_indicators": {"type": "array"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            f"As NEXUS Wellness Assistant, detail a generic fitness plan for:\n'{task}'\n"
            f"Active lifestyle bounds: {context}\n"
            "Safety Warning: Strictly avoid providing medical warnings, prescriptive advice or diagnostic claims."
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else "Wellness guide updated."
        return {
            "wellness_plan": resp,
            "health_indicators": ["Ideal sleeping schedule matches: 8 hours", "General steps goal: 10,000 steps"],
            "disclaimer": "This is lifestyle scheduling advice. Consult professional physicians for critical medical needs.",
            "confidence_score": 0.95
        }
