import time
from typing import List, Dict, Any
from .embeddings import global_local_embedder

class LocalDocIndex:
    """Retains text passages locally, embedding them for custom offline similarity searches."""
    def __init__(self):
        self._chunks: List[Dict[str, Any]] = []

    def clear(self) -> None:
        self._chunks.clear()

    def add_document(self, doc_id: str, text: str, tags: List[str] = None) -> None:
        """Converts strings to chunks, indexing them locally."""
        vector = global_local_embedder.embed_text(text)
        self._chunks.append({
            "doc_id": doc_id,
            "text": text,
            "tags": tags or [],
            "vector": vector,
            "timestamp": time.time()
        })

    def search(self, query: str, limit: int = 2) -> List[Dict[str, Any]]:
        """Calculates cosine similarity on queries against each of our local text weights."""
        query_vector = global_local_embedder.embed_text(query)
        scored_matches = []
        
        for chk in self._chunks:
            similarity = global_local_embedder.calculate_similarity(query_vector, chk["vector"])
            scored_matches.append((similarity, chk))
            
        # Sort descending
        scored_matches.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, chk in scored_matches[:limit]:
            results.append({
                "doc_id": chk["doc_id"],
                "text": chk["text"],
                "tags": chk["tags"],
                "similarity": round(score, 3)
            })
        return results

global_local_doc_index = LocalDocIndex()
