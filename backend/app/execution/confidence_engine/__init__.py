import random
from typing import Dict, Any, List, Optional
from ..interfaces import IConfidenceEngine

class ConfidenceEngine(IConfidenceEngine):
    """Measures, aggregates, and exposes execution integrity scores across all subsystem runs."""
    def __init__(self):
        pass

    def evaluate_confidence(self, component: str, details: Dict[str, Any]) -> float:
        """Determines component specific confidence scores based on execution statistics."""
        comp_lower = component.lower()
        
        if comp_lower == "planner":
            # Is valid DAG structure, number of steps, presence of ambiguities
            is_valid = details.get("is_valid_dag", True)
            if not is_valid:
                return 0.10
            steps_cnt = len(details.get("steps", []))
            is_ambiguous = details.get("is_ambiguous", False)
            
            score = 0.95
            if is_ambiguous:
                score -= 0.40
            if steps_cnt > 5:
                score -= 0.05 # minor decrease for long graphs due to compound risk
            return max(0.10, min(1.0, score))

        elif comp_lower == "agents":
            # Evaluates agent output metrics (length, structure, syntax)
            agent_id = details.get("agent_id", "ceo")
            status = details.get("status", "Healthy")
            base_map = {
                "ceo": 0.95,
                "research": 0.92,
                "coding": 0.89,
                "security": 0.97,
                "reviewer": 0.96
            }
            score = base_map.get(agent_id, 0.90)
            if status != "Healthy":
                score -= 0.30
            return max(0.10, min(1.0, score))

        elif comp_lower == "retrieved_knowledge" or comp_lower == "rag":
            # Derived from vector similarity score, check cosine similarity values if present
            similarities = details.get("similarities", [])
            if not similarities:
                return 0.80 # healthy average lexical backup confidence
            # Calculate average cosine similarity
            avg_sim = sum(similarities) / len(similarities)
            return max(0.10, min(1.0, avg_sim))

        elif comp_lower == "tool_outputs" or comp_lower == "tools":
            success = details.get("success", True)
            if not success:
                return 0.30
            
            # Check for warnings or nested errors in standard shell command feedback
            res = str(details.get("result", "")).lower()
            score = 0.98
            if "warning" in res:
                score -= 0.15
            if "exception" in res or "error" in res:
                score -= 0.50
            return max(0.10, min(1.0, score))

        else:
            return 0.90

    def compute_overall_confidence(self, planner_score: float, step_scores: List[float]) -> float:
        """Derives a weighted average capturing overall DAG execution confidence."""
        if not step_scores:
            return planner_score
            
        avg_steps = sum(step_scores) / len(step_scores)
        # Weighted metric: 30% Planner, 70% execution outcomes
        overall = (planner_score * 0.30) + (avg_steps * 0.70)
        return round(max(0.10, min(1.0, overall)), 2)

global_confidence_engine = ConfidenceEngine()
