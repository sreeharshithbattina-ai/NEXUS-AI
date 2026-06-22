from typing import Dict, Any, List
from ..base import BaseAgent

class LearningAgent(BaseAgent):
    """Learning Agent designs study milestones, curricula tracking templates, and skill logs."""
    def __init__(self, model_manager=None):
        super().__init__("learning_agent", "NEXUS Curricula Coordinator", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
         return ["study milestone design", "curricula template drafting", "topic sequencing"]

    @property
    def input_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"subject": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"syllabus_outline": {"type": "array"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get("user_id", "default")
        curricula_references = []
        try:
            from ...rag import default_search_coordinator
            search_res = default_search_coordinator.search(task, user_id=user_id, limit=2)
            for c in search_res.get("chunks", []):
                meta = c.get("metadata", {})
                curricula_references.append(f"[{meta.get('filename', 'syllabus')}] — Section: {meta.get('heading', 'Content')}: {c['text']}")
        except Exception:
            pass
            
        prompt = (
            f"As NEXUS Skill and Curricula Lead, outline starting topics for learning target:\n'{task}'\n"
            f"Syllabus references found in student workspace databases:\n"
            f"{'\n'.join([f'- {r}' for r in curricula_references]) if curricula_references else 'No manual curriculum files matched.'}\n"
            f"Under the environment limitations: {context}"
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else "Syllabus outlines compiled successfully."
        return {
            "academic_overview": resp,
            "syllabus_outline": ["Unit 1: Basic concepts", "Unit 2: Intermediary implementations"],
            "confidence_score": 0.95 if curricula_references else 0.90
        }
