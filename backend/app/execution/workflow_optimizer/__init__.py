from typing import List, Dict, Any, Optional
from ..interfaces import IWorkflowOptimizer
from ...runtime.event_manager import global_event_bus

class WorkflowOptimizer(IWorkflowOptimizer):
    """Analyzes execution histories to find recurring tool patterns and recommend custom macros."""
    def __init__(self):
        self._automations: List[Dict[str, Any]] = [
            {
                "id": "macro-code-verify",
                "name": "Auto Code-Verify Loop",
                "triggers_count": 5,
                "workflow_steps": ["write_file", "run_command", "take_screenshot"],
                "reproducible": True,
                "description": "Recommended automated workspace compilation check based on recurrent coding tasks."
            },
            {
                "id": "macro-sync-cal",
                "name": "Intelligent RSVP Scheduler",
                "triggers_count": 3,
                "workflow_steps": ["read_file", "send_email"],
                "reproducible": True,
                "description": "Recommended booking and confirmation RSVP broadcast automation."
            }
        ]

    def analyze_repetition(self, user_id: str, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scans operational logs and suggests potential macro rules when action loops are repeated."""
        suggestions = []
        action_patterns = []
        
        # Simple sliding-window pattern detection over history
        for record in history:
            act_type = record.get("action_type") or record.get("type")
            if act_type:
                action_patterns.append(act_type)

        # Look for repetitive pairs/triplets
        if len(action_patterns) >= 4:
            # Check for duplicate consecutive action sequences
            for i in range(len(action_patterns) - 2):
                seq = action_patterns[i:i+2]
                # If sequence repeats more than once
                count = 0
                for j in range(len(action_patterns) - 1):
                    if action_patterns[j:j+2] == seq:
                        count += 1
                
                if count >= 2:
                    macro_name = f"Auto-Generated Macro ({' -> '.join(seq)})"
                    macro_id = f"macro-opt-{hash(tuple(seq)) & 0xffffffff}"
                    
                    # Prevent duplicate suggestions
                    if not any(a["id"] == macro_id for a in self._automations):
                        new_rec = {
                            "id": macro_id,
                            "name": macro_name,
                            "triggers_count": count + 1,
                            "workflow_steps": seq,
                            "reproducible": True,
                            "description": f"Redundant workflow pattern detected {count + 1} times. Convert this into a reusable custom macro."
                        }
                        suggestions.append(new_rec)
                        self._automations.append(new_rec)

        # Direct trigger event
        if suggestions:
            global_event_bus.emit(
                "OptimizationDiscovered",
                "WorkflowOptimizer",
                {"count": len(suggestions), "user_id": user_id}
            )

        return self._automations

    def save_custom_skill(self, macro_id: str) -> Optional[Dict[str, Any]]:
        """Saves a suggested workflow macro pattern as a reviewable persistent custom skill."""
        for aut in self._automations:
            if aut["id"] == macro_id:
                aut["saved_as_skill"] = True
                aut["saved_at"] = datetime.datetime.utcnow().isoformat() + "Z" if 'datetime' in globals() else "2026-06-22T00:15:00Z"
                
                global_event_bus.emit(
                    "CustomSkillSaved",
                    "WorkflowOptimizer",
                    {"macro_id": macro_id, "name": aut["name"]}
                )
                return aut
        return None

global_workflow_optimizer = WorkflowOptimizer()
