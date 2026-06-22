from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseParser(ABC):
    """Abstract interface for extracting text content and structural nodes from files."""
    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Parses raw bytes and returns structured dictionary with:
        - raw_text: str
        - structure: List[Dict[str, Any]] (headings, paragraphs, headers)
        - metadata: Dict[str, Any]
        """
        pass

class BaseChunker(ABC):
    """Abstract interface for splitting raw text into smaller semantic passages."""
    @abstractmethod
    def chunk(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits text or structures into a list of chunk dictionaries:
        - id: str
        - text: str
        - parent_id: Optional[str]
        - metadata: Dict[str, Any] (headings, paragraph_idx, etc)
        """
        pass

class BaseEmbedder(ABC):
    """Abstract interface for creating vector embeddings of text passages."""
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generates embedding vector for a single text fragment."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a batch of text fragments."""
        pass

class BaseVectorStore(ABC):
    """Abstract interface for storing and executing similarity search over vector dimensions."""
    @abstractmethod
    def add_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> None:
        """Indexes vector chunks tied to parent document."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Removes all indexed chunks of document ID."""
        pass

    @abstractmethod
    def similarity_search(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Queries for top-K closest vectors matching conditions."""
        pass

class BaseRetriever(ABC):
    """Abstract interface for unified retrieval queries combining semantics and keywords."""
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Performs search and yields raw structured passages."""
        pass

class BaseReRanker(ABC):
    """Abstract interface for re-evaluating retrieved passages to optimize precision matching."""
    @abstractmethod
    def rerank(self, query: str, retrieved_chunks: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        """Rescores and slices the leading result passages."""
        pass
