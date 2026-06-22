from .hardware import global_hardware_detector
from .ollama import global_ollama_client
from .embeddings import global_local_embedder
from .router import global_hybrid_llm_router
from .document_index import global_local_doc_index

__all__ = [
    "global_hardware_detector",
    "global_ollama_client",
    "global_local_embedder",
    "global_hybrid_llm_router",
    "global_local_doc_index"
]
