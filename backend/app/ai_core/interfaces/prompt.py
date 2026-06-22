from abc import ABC, abstractmethod
from typing import Dict, Any

class PromptTemplate(ABC):
    """
    Abstract representation of a versioned, dynamic system, developer, or agent prompt template.
    """
    @abstractmethod
    def render(self, variables: Dict[str, Any]) -> str:
        """Renders the prompt template given dynamic variables."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Returns the version marker of the prompt template."""
        pass
