from typing import List, Dict, Any, Optional
from ..interfaces import BaseReRanker


class LexicalMatcherReRanker(BaseReRanker):
    """
    Reranks documents by computing Longest Common Subsequence (LCS)
    distance between query strings and passage chunks, guaranteeing
    maximum strict grammatical matches rank first.
    """
    def _lcs_ratio(self, s1: str, s2: str) -> float:
        s1, s2 = s1.lower(), s2.lower()
        m, n = len(s1), len(s2)
        if m == 0 or n == 0:
            return 0.0
            
        # Standard dynamic programming LCS size finder
        dp = [0] * (n + 1)
        for i in range(1, m + 1):
            prev = 0
            for j in range(1, n + 1):
                temp = dp[j]
                if s1[i-1] == s2[j-1]:
                    dp[j] = prev + 1
                else:
                    dp[j] = max(dp[j], dp[j-1])
                prev = temp
                
        return dp[n] / m

    def rerank(self, query: str, retrieved_chunks: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        reranked = []
        for chk in retrieved_chunks:
            ratio = self._lcs_ratio(query, chk["text"])
            score_copy = dict(chk)
            # Mix initial retriever score with lexical similarity ratio
            score_copy["rerank_score"] = 0.5 * chk.get("score", 0.5) + 0.5 * ratio
            score_copy["score"] = score_copy["rerank_score"]
            reranked.append(score_copy)
            
        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:top_n]


class CoherenceLLMReRanker(BaseReRanker):
    """
    Leverages the system's LLM model pool to score the direct relevance/helpfulness
    of a passage chunk to the provided query.
    """
    def __init__(self, model_manager: Any):
        self.model_manager = model_manager

    def rerank(self, query: str, retrieved_chunks: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        if not retrieved_chunks:
            return []
            
        reranked = []
        for chk in retrieved_chunks:
            # We construct a light-weight query checking prompt
            prompt = (
                "You are an assistant evaluating search results coherence. "
                "Analyze how relevant the following Document Passage is to the given User Query.\n"
                f"Query: {query}\n"
                f"Passage: {chk['text']}\n"
                "Respond with a single float rating strictly between 0.0 (totally irrelevant) and 1.0 (highly relevant, contains exact answer). "
                "Do not write any text, introduction, or reasoning. Output only the pure float value (e.g. 0.85)."
            )
            
            try:
                raw_res = self.model_manager.generate(prompt)
                # Parse float value safely
                score = float(raw_res.strip())
                if not (0.0 <= score <= 1.0):
                    score = 0.5
            except Exception:
                score = 0.5 # fallback score
                
            score_copy = dict(chk)
            score_copy["rerank_score"] = score
            score_copy["score"] = score
            reranked.append(score_copy)
            
        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:top_n]


class PassthroughReRanker(BaseReRanker):
    """Fallback re-ranker returning items as-is."""
    def rerank(self, query: str, retrieved_chunks: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        return retrieved_chunks[:top_n]


def get_reranker_provider(strategy: str = "lexical", model_manager: Optional[Any] = None) -> BaseReRanker:
    strategy_clean = strategy.lower().strip()
    if strategy_clean == "coherence" and model_manager is not None:
        return CoherenceLLMReRanker(model_manager=model_manager)
    elif strategy_clean == "lexical":
        return LexicalMatcherReRanker()
    return PassthroughReRanker()
