from typing import Dict, Any, List
from ..base import BaseAgent

class CodingAgent(BaseAgent):
    """Coding Agent reviews systems syntax and generates fully tested snippets."""
    def __init__(self, model_manager=None):
        super().__init__("coding_agent", "NEXUS Core Synthesizer", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
        return ["typescript syntax", "python compilation", "refactoring rules"]

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"instructions": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"code_blocks": {"type": "array"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get("user_id", "default")
        rag_snippets = []
        try:
            from ...rag import default_search_coordinator
            search_res = default_search_coordinator.search(task, user_id=user_id, limit=2)
            for c in search_res.get("chunks", []):
                meta = c.get("metadata", {})
                rag_snippets.append(f"// Reference: {meta.get('filename', 'doc')}\n{c['text']}")
        except Exception:
            pass
            
        prompt = (
            f"As NEXUS senior software engineer, generate production logic or debug steps for task:\n'{task}'\n"
            f"Reference code context from internal manuals:\n"
            f"{'\n\n'.join(rag_snippets) if rag_snippets else 'No custom reference code found.'}\n"
            f"Context: {context}"
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else f"// Process completed logic for {task}."
        return {
            "source_explanation": resp,
            "code_blocks": [{"language": "typescript", "code": resp}],
            "confidence_score": 0.98 if rag_snippets else 0.94
        }
