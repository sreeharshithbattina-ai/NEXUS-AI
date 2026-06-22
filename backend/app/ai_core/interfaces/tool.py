from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """
    Abstract standard for NEXUS AI OS execution tools.
    Every tool must define its name, descriptions, schema of arguments,
    and a synchronous or asynchronous execution pathway.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the tool for model matching."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of what the tool accomplishes."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON Schema format of valid input parameters."""
        pass

    @property
    def requires_approval(self) -> bool:
        """True if executing this tool represents a high-risk/irreversible operation."""
        return False

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the tool logic and returns a structured status body."""
        pass
