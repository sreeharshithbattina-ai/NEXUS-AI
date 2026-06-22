import json
from typing import Dict, Any, Optional
from ..model_manager import ModelManager
from ..prompt_manager import PromptManager

class Reasoner:
    """
    Evaluates generated execution paths. Checks for missing assets, Logical inconsistencies,
    risk parameters, and assigns structured reliability metadata before approval.
    """
    def __init__(self, model_manager: ModelManager, prompt_manager: PromptManager):
        self.model_manager = model_manager
        self.prompt_manager = prompt_manager

    def reason(self, plan: Dict[str, Any], context_summary: Optional[str] = None) -> Dict[str, Any]:
        """
        Reviews proposed staging. Returns consistency feedback.
        """
        context = context_summary or "Operating Sandbox Shell Environment."
        
        # Get Prompt
        prompt = self.prompt_manager.get_prompt_value("system_reasoner", {
            "input_plan": json.dumps(plan),
            "context": context
        })
        
        system_instructions = (
            "You are NEXUS Reasoner Agent. Audit the proposed plan for logical inconsistencies, "
            "missing parameters, and safety and return a JSON dictionary matching this schema:\n"
            "{\n"
            "  \"is_consistent\": true | false,\n"
            "  \"confidence_score\": 0.0 to 1.0,\n"
            "  \"missing_information_detected\": [\"item1\", ...],\n"
            "  \"conflicts_identified\": [\"conflict1\", ...],\n"
            "  \"requires_user_clarification\": true | false,\n"
            "  \"clarification_prompt\": \"Ask user for more details if needed, otherwise empty\"\n"
            "}"
        )
        
        raw_res = self.model_manager.generate(prompt, system_instruction=system_instructions)
        
        try:
            clean_res = raw_res.strip()
            if clean_res.startswith("```json"):
                clean_res = clean_res[7:]
            if clean_res.endswith("```"):
                clean_res = clean_res[:-3]
            clean_res = clean_res.strip()
            
            audit_obj = json.loads(clean_res)
            return audit_obj
        except Exception:
            # Struct fallback based on safety heuristics
            stages = plan.get("stages", [])
            requires_clarification = len(stages) == 0
            
            # Simple conflict rules
            conflicts = []
            if any(s.get("tool") == "terminal" and s.get("specialty_agent") == "CEO" for s in stages):
                conflicts.append("CEO specialty assigned directly to terminal action sequence.")
                
            return {
                "is_consistent": len(conflicts) == 0,
                "confidence_score": 0.95 if len(conflicts) == 0 else 0.75,
                "missing_information_detected": [],
                "conflicts_identified": conflicts,
                "requires_user_clarification": requires_clarification,
                "clarification_prompt": "Please define active parameters if the execution path seems wrong." if requires_clarification else ""
            }
