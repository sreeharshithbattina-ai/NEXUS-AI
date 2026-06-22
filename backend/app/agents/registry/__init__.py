from typing import Dict, Any, List, Optional
from ..base import BaseAgent

class AgentRegistry:
    """
    Central service directory cataloging active specializations, 
    matching tasks with capability subsets, and coordinating system runtime toggles.
    """
    def __init__(self):
        self._registry: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Saves or updates agent capability markers dynamically."""
        self._registry[agent.agent_id.lower()] = agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self._registry.get(agent_id.lower())

    def unregister_agent(self, agent_id: str) -> None:
        self._registry.pop(agent_id.lower(), None)

    def list_agents(self) -> List[Dict[str, Any]]:
        """Returns diagnostic and capabilities breakdown metadata of registered nodes."""
        return [
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "version": a.version,
                "enabled": a.enabled,
                "status": a.status,
                "capabilities": a.capabilities,
                "input_schema": a.input_schema,
                "output_schema": a.output_schema
            }
            for a in self._registry.values()
        ]

    def set_agent_status(self, agent_id: str, enabled: bool) -> bool:
        agent = self.get_agent(agent_id)
        if agent:
            agent.enabled = enabled
            return True
        return False

    def lookup_by_capability(self, capability: str) -> List[BaseAgent]:
        """Returns active agents capable of handling the specified query skill."""
        return [
            a for a in self._registry.values()
            if a.enabled and any(capability.lower() in cap.lower() for cap in a.capabilities)
        ]
