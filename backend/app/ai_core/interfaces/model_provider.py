from abc import ABC, abstractmethod
from typing import Generator, Any, Dict, Optional

class ModelProvider(ABC):
    """
    Abstract interface for all Large Language Model inference providers in NEXUS AI OS.
    Ensures that business logic remains decoupled from specific provider SDKs.
    """
    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> str:
        """Generates a synchronous text completion response."""
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """Streams text completion response chunk by chunk."""
        pass
