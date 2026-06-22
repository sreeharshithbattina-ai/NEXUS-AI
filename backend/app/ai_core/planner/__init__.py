import json
from typing import Dict, Any, List, Optional
from ..model_manager import ModelManager
from ..prompt_manager import PromptManager

class Planner:
    """
    Formulates a structured execution sequence after evaluating the user objective.
    Maps appropriate micro-agents and tools to each plan stage.
    """
    def __init__(self, model_manager: ModelManager, prompt_manager: PromptManager):
        self.model_manager = model_manager
        self.prompt_manager = prompt_manager

    def plan(self, user_intent: str, context_summary: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes intent and yields structured sequence plan dictionary.
        Does not execute actions directly.
        """
        context = context_summary or "Operating Sandbox Shell environment default."
        
        # Get Prompt
        prompt = self.prompt_manager.get_prompt_value("system_planner", {
            "context": context,
            "user_intent": user_intent
        })
        
        # Query Model with high structure request
        system_instructions = (
            "You are the NEXUS Planner Agent. You must respond ONLY with a raw JSON object conforming exactly to this structure:\n"
            "{\n"
            "  \"goal\": \"The core objective being targeted\",\n"
            "  \"stages\": [\n"
            "     {\n"
            "        \"stage_id\": 1,\n"
            "        \"name\": \"Name describing stage task\",\n"
            "        \"specialty_agent\": \"CEO | Planner | Reasoner | Executor | custom\",\n"
            "        \"tool\": \"calculator | time | filesystem | browser | calendar | email | terminal | git | vscode | none\",\n"
            "        \"description\": \"Specific task stage parameters\"\n"
            "     }\n"
            "  ]\n"
            "}"
        )
        
        raw_response = self.model_manager.generate(prompt, system_instruction=system_instructions)
        
        # Attempt secure parsing
        try:
            # Strip markdown surrounding json if any
            clean_res = raw_response.strip()
            if clean_res.startswith("```json"):
                clean_res = clean_res[7:]
            if clean_res.endswith("```"):
                clean_res = clean_res[:-3]
            clean_res = clean_res.strip()
            
            plan_obj = json.loads(clean_res)
            return plan_obj
        except Exception:
            # High quality fallback struct
            return {
                "goal": user_intent,
                "stages": [
                    {
                        "stage_id": 1,
                        "name": "Deconstruct Intent",
                        "specialty_agent": "Planner",
                        "tool": "none",
                        "description": f"Auditing starting conditions for user request: '{user_intent}'"
                    },
                    {
                        "stage_id": 2,
                        "name": "Run Environment Actions",
                        "specialty_agent": "Executor",
                        "tool": "terminal" if "run" in user_intent or "terminal" in user_intent else "filesystem",
                        "description": f"Process primary operations matching the user parameter boundaries."
                    },
                    {
                        "stage_id": 3,
                        "name": "Formulate Synthesis Response",
                        "specialty_agent": "CEO",
                        "tool": "none",
                        "description": "Compile output, log results, and return report summary to user."
                    }
                ]
            }
class MockPlanner(Planner):
    """Fallback planner for testing."""
    def plan(self, user_intent: str, context_summary: Optional[str] = None) -> Dict[str, Any]:
         return {
                "goal": user_intent,
                "stages": [
                    {
                        "stage_id": 1,
                        "name": "Audit Task Conditions",
                        "specialty_agent": "Planner",
                        "tool": "time",
                        "description": "Initial checklist audit"
                    },
                    {
                        "stage_id": 2,
                        "name": "Execute Action sequence",
                        "specialty_agent": "Executor",
                        "tool": "calculator",
                        "description": "Evaluate math calculations as requested"
                    }
                ]
            }
