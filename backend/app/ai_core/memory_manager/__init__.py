from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import datetime

class VectorDatabaseInterface(ABC):
    """
    Abstract contract specification where future semantic vector databases (like ChromaDB, FAISS, Milvus)
    can slot in without impacting core AI state managers.
    """
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Calculates textual semantic multi-dimensional float vectors."""
        pass

    @abstractmethod
    def query_similar(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Queries database for near vector embeddings using Cosine Similarity metrics."""
        pass

class MockVectorDatabase(VectorDatabaseInterface):
    """Initial vector interface fallback. Simulates vector dimensional checks."""
    def embed_text(self, text: str) -> List[float]:
        # Return mock 8-dimensional space vector
        return [0.15, -0.3, 0.45, 0.0, 0.12, -0.05, 0.88, -0.22]

    def query_similar(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        return []

class MemoryManager:
    """
    Central Coordinator managing transient session states, active chat conversation threads,
    and long-term persistent declarative semantic memories.
    """
    def __init__(self, db_session: Optional[Any] = None):
        self.db_session = db_session
        self.working_memory: Dict[str, Any] = {}
        self.conversation_buffer: List[Dict[str, str]] = []
        self.vector_db = MockVectorDatabase()

    def set_working_variable(self, key: str, value: Any) -> None:
        """Stores short-term execution task variables."""
        self.working_memory[key] = value

    def get_working_variable(self, key: str) -> Any:
        return self.working_memory.get(key)

    def append_conversation(self, role: str, content: str) -> None:
        """Keeps transient trace of standard prompt context turns."""
        self.conversation_buffer.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_buffer

    def clear_working_memory(self) -> None:
        self.working_memory.clear()

    # Episodic, Semantic, Declarative operations with Database fallback
    def load_semantic_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Loads semantic facts from SQL DB if session exists, else returns defaults."""
        if self.db_session:
            from ...models import MemoryItem
            items = self.db_session.query(MemoryItem).filter_by(user_id=user_id).all()
            return [
                {
                    "id": item.id,
                    "content": item.content,
                    "type": item.type,
                    "category": item.category,
                    "timestamp": item.timestamp,
                    "tags": item.tags,
                    "confidence": item.confidence
                } for item in items
            ]
        return [
            {"id": "mock-1", "content": "User prefers high-contrast interface themes.", "type": "semantic", "category": "Preference", "confidence": 0.95},
            {"id": "mock-2", "content": "Favorite programming language is TypeScript.", "type": "semantic", "category": "Preference", "confidence": 0.90}
        ]

    def store_semantic_memory(self, user_id: str, content: str, category: str = "Preference", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Saves a permanent memory item."""
        tags = tags or []
        created_time = datetime.datetime.utcnow().isoformat() + "Z"
        
        if self.db_session:
            from ...models import MemoryItem
            import uuid
            new_item = MemoryItem(
                id=str(uuid.uuid4()),
                user_id=user_id,
                content=content,
                type="semantic",
                category=category,
                timestamp=created_time,
                tags=tags,
                confidence=0.95
            )
            self.db_session.add(new_item)
            self.db_session.commit()
            return {
                "id": new_item.id,
                "content": new_item.content,
                "type": new_item.type,
                "category": new_item.category,
                "timestamp": new_item.timestamp,
                "tags": new_item.tags,
                "confidence": new_item.confidence
            }
            
        import uuid
        return {
            "id": str(uuid.uuid4()),
            "content": content,
            "type": "semantic",
            "category": category,
            "timestamp": created_time,
            "tags": tags,
            "confidence": 0.95
        }
