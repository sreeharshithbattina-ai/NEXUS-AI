from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import datetime

class BaseAgent(ABC):
    """
    Abstract state-machine representation of a specialized NEXUS Intelligence Agent.
    Defines identity registries, capability matches, context boundaries, and tool runtimes.
    """
    def __init__(self, agent_id: str, name: str, version: str = "1.0.0"):
        self.agent_id = agent_id
        self.name = name
        self.version = version
        self.enabled = True
        self.status = "Healthy"

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """List of expert skill domains this agent covers."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema dictionary of anticipated parameters."""
        pass

    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """JSON Schema of structured output deliverables."""
        pass

    @abstractmethod
    def run_lifecycle(self, 
                      task: str, 
                      context: Dict[str, Any], 
                      tools: List[Dict[str, Any]], 
                      memory_variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes internal reasoning cycle yielding standardized results metrics.
        """
        pass
