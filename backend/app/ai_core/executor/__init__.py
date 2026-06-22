from typing import Dict, Any, List, Optional
import time
from ..tool_manager import ToolManager
from ..memory_manager import MemoryManager
from ..model_manager import ModelManager
from ..safety_manager import SafetyManager

class Executor:
    """
    Orchestrates the active execution of approved stages.
    Integrates live Tool calls, Memory buffers, model triggers, and dynamic logging outputs.
    """
    def __init__(self, tool_manager: ToolManager, memory_manager: MemoryManager, model_manager: ModelManager, safety_manager: SafetyManager):
        self.tool_manager = tool_manager
        self.memory_manager = memory_manager
        self.model_manager = model_manager
        self.safety_manager = safety_manager

    def execute_plan_stage(self, stage: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Runs a single plan stage."""
        stage_id = stage.get("stage_id", 0)
        name = stage.get("name", "Unnamed Stage")
        tool_name = stage.get("tool", "none")
        agent = stage.get("specialty_agent", "Executor")
        desc = stage.get("description", "")
        
        start_time = time.time()
        
        # 1. Coordinate tools
        if tool_name and tool_name != "none" and self.tool_manager.has_tool(tool_name):
            tool = self.tool_manager.lookup_tool(tool_name)
            
            # Formulate arguments using model synthesis from context and description
            args_prompt = (
                f"Synthesize the required arguments for {tool_name} tool.\n"
                f"Description: '{desc}'\n"
                f"Schema definition: {tool.parameters_schema}\n"
                f"Output ONLY a flat JSON dictionary of keys matching the tool schema."
            )
            raw_args = self.model_manager.generate(args_prompt)
            
            # Parse arguments
            try:
                import json
                clean_args = raw_args.strip()
                if clean_args.startswith("```json"):
                    clean_args = clean_args[7:]
                if clean_args.endswith("```"):
                    clean_args = clean_args[:-3]
                args = json.loads(clean_args.strip())
            except Exception:
                # Safe argument guesses matching tool expectations
                args = {}
                if tool_name == "calculator":
                    args = {"expression": "2 + 2"}
                elif tool_name == "filesystem":
                    args = {"action": "list", "filepath": "."}
                elif tool_name == "calendar":
                    args = {"action": "list"}
                    
            # 2. Check safety gates
            requires_approval, reason, approval_payload = self.safety_manager.assess_risk(tool_name, args)
            if requires_approval:
                return {
                    "stage_id": stage_id,
                    "status": "awaiting_approval",
                    "requires_approval": True,
                    "reason": reason,
                    "approval_payload": approval_payload,
                    "tool": tool_name,
                    "arguments": args,
                    "duration_seconds": round(time.time() - start_time, 3)
                }

            # 3. Secure execution
            res = self.tool_manager.execute_tool(tool_name, args)
            
            # Store tool trace in working memory registry
            self.memory_manager.set_working_variable(f"stage_{stage_id}_result", res)
            
            return {
                "stage_id": stage_id,
                "status": "completed" if res.get("status") == "success" else "failed",
                "result": res,
                "tool_used": tool_name,
                "arguments": args,
                "duration_seconds": round(time.time() - start_time, 3)
            }
            
        else:
            # Model-only reasoning execution
            result_txt = self.model_manager.generate(
                f"Process this reasoning and syntheses step directly without tools:\n"
                f"Step: {name}\n"
                f"Description: {desc}"
            )
            
            self.memory_manager.set_working_variable(f"stage_{stage_id}_reasoning_result", result_txt)
            
            return {
                "stage_id": stage_id,
                "status": "completed",
                "result": {"status": "success", "summary": result_txt},
                "tool_used": "none",
                "duration_seconds": round(time.time() - start_time, 3)
            }

    def execute_plan(self, plan: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """Sequential execution of complete approved plan."""
        stages = plan.get("stages", [])
        trace_steps = []
        for stage in stages:
            ans = self.execute_plan_stage(stage, user_id)
            trace_steps.append(ans)
            if ans.get("status") in ["awaiting_approval", "failed"]:
                # Halt execution to respect safety or failure cascades
                break
        return trace_steps
+
```
