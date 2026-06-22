from .interfaces import (
    BaseParser,
    BaseChunker,
    BaseEmbedder,
    BaseVectorStore,
    BaseRetriever,
    BaseReRanker
)
from .parsers import DocumentParserRegistry
from .chunking import RAGChunker
from .embeddings import get_embedding_provider, LocalProjectionEmbedder
from .vector_store import MemoryVectorStore, global_vector_store
from .retriever import HybridRetriever
from .reranker import get_reranker_provider
from .citations import CitationBuilder
from .indexing import IndexingManager
from .metadata import MetadataExtractor
from .search import SearchCoordinator
from .pipelines import RAGIngestionPipeline

# Initialize premium default RAG objects
default_embedder = get_embedding_provider("local")
default_retriever = HybridRetriever(global_vector_store, default_embedder)
default_reranker = get_reranker_provider("lexical")
default_search_coordinator = SearchCoordinator(default_retriever, default_reranker)
default_ingestion_pipeline = RAGIngestionPipeline(global_vector_store, default_embedder)
