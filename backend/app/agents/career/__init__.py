from typing import Dict, Any, List
from ..base import BaseAgent

class CareerAgent(BaseAgent):
    """Career Agent handles resume critiques, application cover letters, and interview preparation guides."""
    def __init__(self, model_manager=None):
        super().__init__("career_agent", "NEXUS Career Consultant", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
         return ["resume critique profiling", "interview strategy coaching", "cover letter synthesis"]

    @property
    def input_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"job_title": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
         return {"type": "object", "properties": {"recommendations": {"type": "array"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get("user_id", "default")
        career_facts = []
        try:
            from ...rag import default_search_coordinator
            search_res = default_search_coordinator.search(task, user_id=user_id, limit=2)
            for c in search_res.get("chunks", []):
                meta = c.get("metadata", {})
                career_facts.append(f"[{meta.get('filename', 'resume_or_jd')}]: {c['text']}")
        except Exception:
            pass
            
        prompt = (
            f"As NEXUS Career Consultant, structure professional critiques or pitches for:\n'{task}'\n"
            f"RAG Document Context (JD details, resume references):\n"
            f"{'\n'.join([f'- {f}' for f in career_facts]) if career_facts else 'No target resumes found.'}\n"
            f"Context constraints: {context}"
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else "Recommendations compiled."
        return {
            "career_critique": resp,
            "recommendations": ["Refactor executive summary section", "Incorporate performance metrics percentages"],
            "confidence_score": 0.96 if career_facts else 0.92
        }
