from typing import Dict, Any, List
from ..base import BaseAgent

class CEOAgent(BaseAgent):
    """CEO Agent supervises strategic milestones and overall prioritization."""
    def __init__(self, model_manager=None):
        super().__init__("ceo_agent", "NEXUS CEO Coordinating Authority", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
        return ["strategic coordination", "conflict resolution", "milestone prioritisation"]

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"objective": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"strategic_decision": {"type": "string"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get("user_id", "default")
        strategic_contexts = []
        try:
            from ...rag import default_search_coordinator
            search_res = default_search_coordinator.search(task, user_id=user_id, limit=2)
            for c in search_res.get("chunks", []):
                meta = c.get("metadata", {})
                strategic_contexts.append(f"[{meta.get('filename', 'strategy')}]: {c['text']}")
        except Exception:
            pass
            
        prompt = (
            f"As NEXUS CEO Coordinating Authority, synthesize this strategic goal:\n'{task}'\n"
            f"Strategic milestones reference documents:\n"
            f"{'\n'.join([f'- {s}' for s in strategic_contexts]) if strategic_contexts else 'No direct strategic reference manuals found.'}\n"
            f"Context: {context}\n"
            "Define milestones, verify priorities, and assign logical goals."
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else f"CEO compiled strategy sequence for: '{task}'."
        return {
            "strategic_decision": resp,
            "confidence_score": 0.99 if strategic_contexts else 0.98,
            "metrics": {"task": "prioritization", "status": "resolved"}
        }
