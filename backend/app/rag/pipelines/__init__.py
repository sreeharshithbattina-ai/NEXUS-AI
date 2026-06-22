import uuid
from typing import Dict, Any, List, Optional
from ..interfaces import BaseParser, BaseChunker, BaseEmbedder, BaseVectorStore
from ..parsers import DocumentParserRegistry
from ..chunking import RAGChunker
from ..metadata import MetadataExtractor
from ..indexing import IndexingManager


class RAGIngestionPipeline:
    """
    Implements the enterprise-grade Document Pipeline.
    Manages end-to-end file ingestion, validation, parsing, metadata extraction,
    embedding derivation, vector storage, and incremental index caching.
    """
    def __init__(self, vector_store: BaseVectorStore, embedder: BaseEmbedder):
        self.vector_store = vector_store
        self.embedder = embedder
        self.parser_registry = DocumentParserRegistry()
        self.indexing_manager = IndexingManager(embedder)

    def validate_file(self, content_size: int, filename: str) -> None:
        """Validates file constraints."""
        max_size = 15 * 1024 * 1024 # 15MB ceiling
        if content_size > max_size:
            raise ValueError(f"File size exceeds allowable limit (Max 15MB). Received {content_size/1024/1024:.2f}MB.")
            
        supported_extensions = {
            "pdf", "docx", "pptx", "txt", "md", "markdown", 
            "csv", "json", "html", "htm", "xlsx", "xls"
        }
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in supported_extensions:
            raise ValueError(f"Unsupported file format: '.{ext}'. Supported: {', '.join(supported_extensions)}")

    def ingest_document(self, file_bytes: bytes, filename: str, user_id: str, chunk_strategy: str = "recursive") -> Dict[str, Any]:
        """
        Executes end-to-end pipeline:
        1. Validate
        2. Parse & extract text
        3. Clean formatting
        4. Split into chunks with parent-child tracking
        5. Extract metadata tags
        6. Generate embeddings with memoized caching
        7. Store vectors in enterprise store
        """
        # Step 1: Validate file sizes and types
        self.validate_file(len(file_bytes), filename)
        
        # Step 2: Parse text & structure
        parsed = self.parser_registry.parse_file(file_bytes, filename)
        raw_text = parsed["raw_text"]
        
        # Duplicate detection sanity check
        if self.indexing_manager.is_duplicate(user_id, raw_text):
            # Already indexed exact same contents, return mock success to prevent duplicate CPU cycles
             parsed["metadata"]["is_duplicate"] = True
             
        self.indexing_manager.register_content_hash(user_id, raw_text)
        
        # Step 3: Extract & enrich metadata
        enriched_metadata = MetadataExtractor.extract_metadata(parsed)
        enriched_metadata["user_id"] = user_id
        parsed["metadata"] = enriched_metadata
        
        # Step 4: Chunk document
        chunker = RAGChunker(strategy=chunk_strategy)
        chunks = chunker.chunk(parsed)
        
        # Step 5: Embed chunks with caching and retry protections
        document_id = f"doc-{str(uuid.uuid4())[:12]}"
        vectorized_chunks = []
        
        for chk in chunks:
            chunk_text = chk["text"]
            # Check embedding ledger cache
            vector = self.indexing_manager.get_cached_embedding(chunk_text)
            if not vector:
                # Cache miss, invoke embed with exponential-retry wrapper
                def embed_job():
                    return self.embedder.embed_text(chunk_text)
                vector = self.indexing_manager.retry_on_failure(embed_job)
                self.indexing_manager.cache_embedding(chunk_text, vector)
                
            chk_vectorized = dict(chk)
            chk_vectorized["vector"] = vector
            vectorized_chunks.append(chk_vectorized)
            
        # Step 6: Store vectors in Unified Memory Store
        self.vector_store.add_chunks(document_id, vectorized_chunks)
        
        return {
            "document_id": document_id,
            "filename": filename,
            "user_id": user_id,
            "word_count": enriched_metadata["word_count"],
            "chunks_count": len(chunks),
            "chunks": [
                {
                    "id": c["id"],
                    "text": c["text"],
                    "parent_id": c["parent_id"],
                    "vectorId": c["vector"][:8], # trunc vector for compact DB reporting
                    "confidence": 0.95
                }
                for c in vectorized_chunks
            ],
            "metadata": enriched_metadata
        }
