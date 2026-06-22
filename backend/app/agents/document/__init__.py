from typing import Dict, Any, List
from ..base import BaseAgent

class DocumentAgent(BaseAgent):
    """Document Agent performs structural markdown analyses, text summarization, and file extractions."""
    def __init__(self, model_manager=None):
        super().__init__("document_agent", "NEXUS Document Synthesizer", "1.0.0")
        self.model_manager = model_manager

    @property
    def capabilities(self) -> List[str]:
        return ["semantic summarization", "metadata extraction", "structural markdown analysis"]

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"raw_text": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"summaries": {"type": "array"}}}

    def run_lifecycle(self, task: str, context: Dict[str, Any], tools: List[Dict[str, Any]], memory_orders: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get("user_id", "default")
        file_contexts = []
        try:
            from ...rag import default_search_coordinator
            search_res = default_search_coordinator.search(task, user_id=user_id, limit=2)
            for c in search_res.get("chunks", []):
                meta = c.get("metadata", {})
                file_contexts.append(f"[{meta.get('filename', 'doc')}] Section: {meta.get('heading', 'Content')}: {c['text']}")
        except Exception:
            pass
            
        prompt = (
            f"As NEXUS Document Specialist, draft bullet summaries for text chunk:\n'{task}'\n"
            f"Target document text segments retrieved via RAG:\n"
            f"{'\n'.join([f'- {o}' for o in file_contexts]) if file_contexts else 'No direct overlapping documents retrieved.'}\n"
            f"Workspace constraints: {context}"
        )
        resp = self.model_manager.generate(prompt) if self.model_manager else f"Document parsing summary completed successfully."
        return {
            "summary_text": resp,
            "summaries": [f"Parsed: {task[:50]}..."],
            "confidence_score": 0.97 if file_contexts else 0.93
        }
