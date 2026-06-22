import time
from typing import List, Dict, Any, Optional
from ...runtime.event_manager import global_event_bus

class ExperienceManager:
    """Stores and retrieves historical execution metrics to provide experiential context for planning."""
    def __init__(self):
        self._history: Dict[str, Dict[str, Any]] = {}

    def log_experience(self, plan_id: str, user_intent: str, success: bool, steps_count: int, duration_sec: float) -> Dict[str, Any]:
        experience = {
            "plan_id": plan_id,
            "user_intent": user_intent,
            "success": success,
            "steps_count": steps_count,
            "duration_sec": round(duration_sec, 2),
            "timestamp": time.time()
        }
        self._history[plan_id] = experience
        
        global_event_bus.emit(
            "ExperienceLogged",
            "ExperienceManager",
            {"plan_id": plan_id, "success": success}
        )
        return experience

    def get_experiences(self) -> List[Dict[str, Any]]:
        return list(self._history.values())

    def get_success_rate(self) -> float:
        if not self._history:
            return 100.0
        successes = sum(1 for e in self._history.values() if e["success"])
        return round((successes / len(self._history)) * 100, 1)

    def recommend_best_path(self, user_intent: str) -> Optional[Dict[str, Any]]:
        """Scans previous successful matches for matching intents to guide planner templates."""
        best_match = None
        best_overlap = 0.0
        
        words_target = set(user_intent.lower().split())
        for exp in self._history.values():
            if not exp["success"]:
                continue
            words_exp = set(exp["user_intent"].lower().split())
            overlap = len(words_target.intersection(words_exp))
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = exp
                
        return best_match if best_overlap >= 2 else None

global_experience_manager = ExperienceManager()
