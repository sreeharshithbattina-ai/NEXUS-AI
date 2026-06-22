from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class IIntentEngine(ABC):
    @abstractmethod
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classifies intent category, estimates confidence, and parses ambiguity."""
        pass

class IExecutionPlanner(ABC):
    @abstractmethod
    def generate_plan(self, goal: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates a DAG of tasks / steps for execution."""
        pass

class IApprovalManager(ABC):
    @abstractmethod
    def requires_approval(self, action_type: str, params: Dict[str, Any]) -> bool:
        """Determines if the action requires explicit human signoff."""
        pass

    @abstractmethod
    def suspend_for_approval(self, workflow_id: str, step_id: str, prompt: str) -> str:
        """Registers a suspended step waiting for user approval, returning ticket ID."""
        pass

    @abstractmethod
    def resolve_approval(self, approval_id: str, approved: bool) -> bool:
        """Completes approval gate resolution."""
        pass

class IConfidenceEngine(ABC):
    @abstractmethod
    def evaluate_confidence(self, component: str, details: Dict[str, Any]) -> float:
        """Computes subcomponents or aggregated overall execution confidence scores."""
        pass

class IReflectionEngine(ABC):
    @abstractmethod
    def reflect(self, workflow_id: str, plan: Dict[str, Any], execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates final execution run, logs improvements, and derives lessons learned."""
        pass

class ILearningEngine(ABC):
    @abstractmethod
    def extract_preferences(self, user_id: str, session_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scans session interactions and learns sustainable user preference rules."""
        pass

class IWorkflowOptimizer(ABC):
    @abstractmethod
    def analyze_repetition(self, user_id: str, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifies repetitive patterns and recommends macro automations."""
        pass

class IRecoveryEngine(ABC):
    @abstractmethod
    def attempt_recovery(self, failure_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Triggers specific recovery paths (retries, alternative paths, rollbacks)."""
        pass

class IMetricsTracker(ABC):
    @abstractmethod
    def record_metric(self, name: str, value: Any, tags: Optional[Dict[str, str]] = None) -> None:
        """Records telemetry execution metrics safely."""
        pass

    @abstractmethod
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Computes current average latencies, success rates, and agent telemetry."""
        pass
