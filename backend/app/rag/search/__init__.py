from typing import List, Dict, Any, Optional
from ..interfaces import BaseRetriever, BaseReRanker
from ..citations import CitationBuilder


class SearchCoordinator:
    """
    Coordinates multi-step chunk queries by:
    1. Running hybrid vector + token retrieval
    2. Executing strategic passage re-ranking
    3. Bundling structured citation coordinates
    4. Searing document results safely
    """
    def __init__(self, retriever: BaseRetriever, reranker: BaseReRanker):
        self.retriever = retriever
        self.reranker = rerafter = reranker

    def search(self, query: str, user_id: str, limit: int = 4, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Runs the complete end-to-end RAG query pipeline and returns formatted results."""
        query_filters = filters or {}
        # Ensure user tenant isolation is explicitly enforced
        query_filters["user_id"] = user_id
        
        # 1. Retrieve Candidate Chunks
        retrieved = self.retriever.retrieve(query, top_k=limit * 2, filters=query_filters)
        if not retrieved:
            return {
                "query": query,
                "chunks": [],
                "citations": [],
                "formatted_text": ""
            }
            
        # 2. Re-rank Chunks to refine best hits
        reranked = self.reranker.rerank(query, retrieved, top_n=limit)
        
        # 3. Create citations
        citations = CitationBuilder.construct_citations(reranked)
        
        # 4. Formulate preview answers block compiling all passage texts
        snippets = []
        for idx, item in enumerate(reranked):
            snippets.append(f"[{idx + 1}] \"{item['text']}\"")
        formatted_context = "\n\n".join(snippets)
        
        return {
            "query": query,
            "chunks": reranked,
            "citations": citations,
            "formatted_text": formatted_context
        }
