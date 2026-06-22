from .base import BaseAgent
from .registry import AgentRegistry
from .communication import AgentMessage
from .orchestrator import AgentOrchestrator

from .ceo import CEOAgent
from .planner import PlannerAgent
from .research import ResearchAgent
from .coding import CodingAgent
from .browser import BrowserAgent
from .automation import AutomationAgent
from .memory import MemoryAgent
from .document import DocumentAgent
from .calendar import CalendarAgent
from .travel import TravelAgent
from .finance import FinanceAgent
from .learning import LearningAgent
from .career import CareerAgent
from .security import SecurityAgent
from .vision import VisionAgent
from .health import HealthAgent
from .reviewer import ReviewerAgent

# Dynamic instantiation and registration context helper
def build_and_register_all(model_manager=None) -> AgentRegistry:
    registry = AgentRegistry()
    
    # 17 Specialized Agents instantiation
    agents = [
        CEOAgent(model_manager),
        PlannerAgent(model_manager),
        ResearchAgent(model_manager),
        CodingAgent(model_manager),
        BrowserAgent(model_manager),
        AutomationAgent(model_manager),
        MemoryAgent(model_manager),
        DocumentAgent(model_manager),
        CalendarAgent(model_manager),
        TravelAgent(model_manager),
        FinanceAgent(model_manager),
        LearningAgent(model_manager),
        CareerAgent(model_manager),
        SecurityAgent(model_manager),
        VisionAgent(model_manager),
        HealthAgent(model_manager),
        ReviewerAgent(model_manager)
    ]
    
    for agent in agents:
        registry.register_agent(agent)
        
    return registry

__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "AgentMessage",
    "AgentOrchestrator",
    "CEOAgent",
    "PlannerAgent",
    "ResearchAgent",
    "CodingAgent",
    "BrowserAgent",
    "AutomationAgent",
    "MemoryAgent",
    "DocumentAgent",
    "CalendarAgent",
    "TravelAgent",
    "FinanceAgent",
    "LearningAgent",
    "CareerAgent",
    "SecurityAgent",
    "VisionAgent",
    "HealthAgent",
    "ReviewerAgent",
    "build_and_register_all"
]
