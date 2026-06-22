from typing import Dict, Any, List
from ..base import BaseAgent

class TravelAgent(BaseAgent):
    """Travel Agent coordinates destination guidelines, hotel lookups, and travel routing paths."""
    def __init__(self, model_manager=None):
        super().__init__("travel_agent", "NEXUS Travel Consultant", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
         return ["itinerary generation", "hotel lookup routing", "destination guidelines collation"]

    @property
    def input_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"destination": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"itinerary": {"type": "array"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            f"As NEXUS Travel Coordinator, draft customized destination checkpoints to:\n'{task}'\n"
            f"Context: {context}"
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else f"Trip itinerary formulated for {task}."
        return {
            "travel_analysis": resp,
            "itinerary": [f"Day 1: Arrive {task}", "Day 2: Explore primary spots"],
            "confidence_score": 0.91
        }
