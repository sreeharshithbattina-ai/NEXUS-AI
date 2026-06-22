import math
from typing import List, Dict, Any, Optional
from ..interfaces import BaseVectorStore


class MemoryVectorStore(BaseVectorStore):
    """
    High-performance in-memory vec engine supporting:
    - Cosine similarity matching
    - User-level tenant isolation
    - Multi-attribute metadata filtering
    - Exact deletion mechanics
    """
    def __init__(self):
        # Memory storage structured as:
        # { doc_id: [{ chunk_id, text, vector, metadata }] }
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def add_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> None:
        """Indexes text chunks along with precalculated embeddings."""
        if document_id not in self._store:
            self._store[document_id] = []
            
        for chunk in chunks:
            self._store[document_id].append({
                "id": chunk.get("id"),
                "text": chunk.get("text"),
                "vector": chunk.get("vector"),
                "parent_id": chunk.get("parent_id"),
                "metadata": chunk.get("metadata", {})
            })

    def delete_document(self, document_id: str) -> None:
        """Removes all indexed chunks tied to document ID."""
        if document_id in self._store:
            del self._store[document_id]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def similarity_search(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Queries for top-K matching vectors under exact filtering parameters."""
        candidates = []
        
        for doc_id, chunks in self._store.items():
            for chk in chunks:
                metadata = chk.get("metadata", {})
                
                # Check user_id workspace filtering first
                if filters and "user_id" in filters:
                    if metadata.get("user_id") != filters["user_id"]:
                        continue
                        
                # General metadata filter match checks
                matched = True
                if filters:
                    for k, v in filters.items():
                        if k == "user_id":
                            continue
                        if metadata.get(k) != v:
                            matched = False
                            break
                if not matched:
                    continue
                    
                score = self._cosine_similarity(query_vector, chk["vector"])
                candidates.append({
                    "id": chk["id"],
                    "document_id": doc_id,
                    "text": chk["text"],
                    "parent_id": chk["parent_id"],
                    "score": score,
                    "metadata": metadata
                })
                
        # Sort decreasing order by score
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_k]


# --- Future Storage Target Mock Interfaces ---

class FutureChromaDBStore(BaseVectorStore):
    """Abstraction layout of future ChromaDB adapter integration."""
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        
    def add_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> None:
        # chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        # collection = chroma_client.get_or_create_collection("nexus_rag")
        # collection.add(ids, embeddings, metadatas, documents)
        pass

    def delete_document(self, document_id: str) -> None:
        pass

    def similarity_search(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []


class FuturePostgreSQLVectorStore(BaseVectorStore):
    """Abstraction layout of future pgvector PostgreSQL database storage."""
    def __init__(self, db_connection_url: str):
        self.connection_url = db_connection_url

    def add_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> None:
        # INSERT INTO rag_chunks (chunk_id, doc_id, embedding, text, metadata)
        # VALUES (%s, %s, %s, %s, %s)
        pass

    def delete_document(self, document_id: str) -> None:
        pass

    def similarity_search(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # SELECT chunk_id, text, 1 - (embedding <=> %s) AS similarity FROM rag_chunks
        # WHERE user_id = %s ORDER BY similarity DESC LIMIT %s
        return []


class FutureFAISSStore(BaseVectorStore):
    """Abstraction layout of future FAISS indexing library integration."""
    def __init__(self, index_file: str):
         self.index_file = index_file

    def add_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> None:
         # index = faiss.IndexFlatIP(dimension)
         # index.add(np_embeddings)
         pass

    def delete_document(self, document_id: str) -> None:
         pass

    def similarity_search(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
         return []


# Global Singleton Vector Store serving the active thread pool
global_vector_store = MemoryVectorStore()
