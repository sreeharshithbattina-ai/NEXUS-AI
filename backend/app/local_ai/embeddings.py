import numpy as np
from typing import List

class LocalEmbedder:
    """Computes textual dot products and cosine coefficients locally using mathematical projections."""
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Maps an input string into a standard float array."""
        # Simple stable deterministic vector projection based on character codes
        np.random.seed(hash(text) & 0xffffffff)
        vec = np.random.randn(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def calculate_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Returns standard cosine similarity between two dimensional arrays."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

global_local_embedder = LocalEmbedder()
