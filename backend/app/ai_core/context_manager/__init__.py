from typing import Dict, Any, List, Optional
import json

class ContextManager:
    """
    Assembles compilation matrices containing conversation histories, semantic memories,
    retrieved context documents (RAG), and system settings.
    """
    def __init__(self):
        pass

    def build_context(self, 
                      user_id: str,
                      messages: List[Dict[str, Any]], 
                      memories: List[Dict[str, Any]], 
                      documents: List[Dict[str, Any]], 
                      active_tasks: List[Dict[str, Any]],
                      system_instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Assembles all discrete system states into an unified system context matrix.
        """
        # Formulate formatted conversation trace
        chat_repr = []
        for msg in messages[-8:]: # last 8 turns
            role = msg.get("role", "user")
            content = msg.get("content", "")
            chat_repr.append(f"{role.capitalize()}: {content}")
        chat_str = "\n".join(chat_repr)

        # Formulate memory items representation
        mem_repr = []
        for mem in memories:
            content = mem.get("content", "")
            category = mem.get("category", "Preference")
            mem_repr.append(f"[{category}] {content}")
        mem_str = "; ".join(mem_repr) if mem_repr else "No active target preferences indexed."

        # Formulate documents representation (RAG context integration)
        doc_repr = []
        for doc in documents:
            title = doc.get("title", "Document")
            content_snippet = doc.get("content", "")[:350]
            doc_repr.append(f"Document '{title}': {content_snippet}...")
            
        # Automatically pull in-depth semantic chunks from global RAG store matching user intent
        rag_passages = []
        if messages:
            last_msg = messages[-1].get("content", "")
            if last_msg:
                try:
                    from ...rag import default_search_coordinator
                    # Pull up to 3 best coherence matches
                    search_results = default_search_coordinator.search(last_msg, user_id=user_id, limit=3)
                    for idx, chunk in enumerate(search_results.get("chunks", [])):
                        c_meta = chunk.get("metadata", {})
                        section = c_meta.get("heading", "General")
                        filename = c_meta.get("filename", "Context Doc")
                        rag_passages.append(
                            f"RAG Chunk {idx+1} [Source: {filename} > Section: {section}] (Confidence: {chunk.get('score', 0.9):.2f}):\n"
                            f"\"{chunk['text']}\""
                        )
                except Exception:
                    pass
                    
        if rag_passages:
            doc_repr.append("\n---\n".join(rag_passages))
            
        doc_str = "\n\n".join(doc_repr) if doc_repr else "No relevant documents retrieved."

        # Formulate current active task matrix representation
        task_repr = []
        for t in active_tasks:
            name = t.get("name", "Task")
            status = t.get("status", "pending")
            task_repr.append(f"Task '{name}' ({status})")
        task_str = ", ".join(task_repr) if task_repr else "Idle queue."

        # Construct final unified prompt injection dictionary
        return {
            "user_id": user_id,
            "conversation_history": chat_str,
            "semantic_memories": mem_str,
            "rag_context": doc_str,
            "active_tasks": task_str,
            "instructions": system_instructions or "Help the user manage tasks safely."
        }

    def assemble_prompt_with_context(self, prompt_template: str, context: Dict[str, Any], user_intent: str) -> str:
        """Helper to inject constructed context directly into template placeholders."""
        res = prompt_template
        res = res.replace("{{context}}", json.dumps(context))
        res = res.replace("{{memories}}", context.get("semantic_memories", ""))
        res = res.replace("{{documents}}", context.get("rag_context", ""))
        res = res.replace("{{user_intent}}", user_intent)
        return res
+
```
