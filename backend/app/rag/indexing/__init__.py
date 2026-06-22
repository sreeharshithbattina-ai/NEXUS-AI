import hashlib
import time
from typing import Dict, Any, List, Optional, Callable
from ..interfaces import BaseEmbedder

class IndexingManager:
    """
    Governs performance-focused document ingestion operations including:
    - Content hash duplicate detection
    - Incremental indexing gating
    - Async progress state monitors
    - Embedding transaction caches
    - Safe API transaction auto-retries
    """
    def __init__(self, embedder: BaseEmbedder):
        self.embedder = embedder
        # Content Hash Lookup table to prevent duplicates
        # { user_id: set(content_hashes) }
        self._hash_lookup: Dict[str, set] = {}
        # Progress map:
        # { job_id: { progress_percent: int, status: str, error: str, count: int } }
        self._progress_registry: Dict[str, Dict[str, Any]] = {}
        # Vector cache
        # { text_hash: vector }
        self._embedding_cache: Dict[str, List[float]] = {}

    def get_content_hash(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()

    def is_duplicate(self, user_id: str, text: str) -> bool:
        """Checks if exact text content has already been indexed in this user namespace."""
        ch_hash = self.get_content_hash(text)
        if user_id not in self._hash_lookup:
            self._hash_lookup[user_id] = set()
            return False
            
        return ch_hash in self._hash_lookup[user_id]

    def register_content_hash(self, user_id: str, text: str) -> None:
        ch_hash = self.get_content_hash(text)
        if user_id not in self._hash_lookup:
            self._hash_lookup[user_id] = set()
        self._hash_lookup[user_id].add(ch_hash)

    def deregister_content_hash(self, user_id: str, text: str) -> None:
         ch_hash = self.get_content_hash(text)
         if user_id in self._hash_lookup and ch_hash in self._hash_lookup[user_id]:
              self._hash_lookup[user_id].remove(ch_hash)

    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        txt_hash = self.get_content_hash(text)
        return self._embedding_cache.get(txt_hash)

    def cache_embedding(self, text: str, vector: List[float]) -> None:
        txt_hash = self.get_content_hash(text)
        self._embedding_cache[txt_hash] = vector

    def init_progress_tracker(self, job_id: str) -> None:
        self._progress_registry[job_id] = {
            "progress_percent": 0,
            "status": "Initialized",
            "chunks_processed": 0,
            "error_msg": None,
            "timestamp": time.time()
        }

    def update_progress(self, job_id: str, percent: int, status: str, chunks_count: int = 0, error: Optional[str] = None) -> None:
        if job_id in self._progress_registry:
            self._progress_registry[job_id]["progress_percent"] = percent
            self._progress_registry[job_id]["status"] = status
            self._progress_registry[job_id]["chunks_processed"] += chunks_count
            if error:
                self._progress_registry[job_id]["error_msg"] = error

    def get_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._progress_registry.get(job_id)

    def retry_on_failure(self, task: Callable, max_retries: int = 3, initial_delay: float = 1.0) -> Any:
        """Standard transactional retry wrapper to shelter cloud requests against rate-limit exceptions."""
        delay = initial_delay
        for attempt in range(max_retries):
            try:
                return task()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay)
                delay *= 2 # exponential backoff
