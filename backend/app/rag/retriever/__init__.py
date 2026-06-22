import re
from typing import List, Dict, Any, Optional
from ..interfaces import BaseRetriever, BaseEmbedder, BaseVectorStore


class HybridRetriever(BaseRetriever):
    """
    Enterprise-grade Hybrid Retriever implementing:
    - Cosine Vector Semantics Search
    - Pure keyword token frequency (TF-IDF keyword score) search
    - Reciprocal Rank weight-sum scoring
    - Exact Metadata filter sweeps
    """
    def __init__(self, vector_store: BaseVectorStore, embedder: BaseEmbedder, semantic_weight: float = 0.6, keyword_weight: float = 0.4):
        self.vector_store = vector_store
        self.embedder = embedder
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

    def _keyword_relevance_score(self, query: str, text: str) -> float:
        """Computes a frequency-based score for query terms in a chunk text."""
        query_words = set(re.findall(r"\w+", query.lower()))
        if not query_words:
            return 0.0
            
        text_words = re.findall(r"\w+", text.lower())
        if not text_words:
            return 0.0
            
        # Standard Term Frequency matching
        match_count = sum(1 for w in text_words if w in query_words)
        # Term Frequency normalized by chunk length
        tf = match_count / len(text_words)
        
        # Unique word overlap percentage
        unique_matches = sum(1 for w in query_words if w in text_words)
        coverage = unique_matches / len(query_words)
        
        return 0.7 * coverage + 0.3 * tf

    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # 1. Fetch semantic scores
        query_embedding = self.embedder.embed_text(query)
        # Retrieve slightly more than top_k from vector search to allow hybrid ranking
        semantic_candidates = self.vector_store.similarity_search(query_embedding, top_k=top_k * 3, filters=filters)
        
        # 2. Score, normalize, and merge
        merged_candidates = []
        for cand in semantic_candidates:
            text = cand["text"]
            semantic_score = cand["score"]
            # Convert (-1 to 1) Cosine similarity to (0 to 1) range
            normalized_semantic = (semantic_score + 1) / 2
            
            # calculate keyword overlap score
            keyword_score = self._keyword_relevance_score(query, text)
            
            # Weight aggregation
            hybrid_score = (self.semantic_weight * normalized_semantic) + (self.keyword_weight * keyword_score)
            
            # Add hybrid score back inside candid state dictionary
            cand_copy = dict(cand)
            cand_copy["semantic_score"] = semantic_score
            cand_copy["keyword_score"] = keyword_score
            cand_copy["score"] = hybrid_score # update final rank score
            merged_candidates.append(cand_copy)
            
        # Re-sort descendingly
        merged_candidates.sort(key=lambda x: x["score"], reverse=True)
        return merged_candidates[:top_k]
