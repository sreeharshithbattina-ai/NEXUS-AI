import time
from typing import List, Dict, Any, Optional
from ..interfaces import IReflectionEngine
from ...runtime.event_manager import global_event_bus

class ReflectionEngine(IReflectionEngine):
    """Audits running plans after completion, extracting improvements and saving persistent learning logs."""
    def __init__(self):
        self._reflection_logs: List[Dict[str, Any]] = []

    def reflect(self, workflow_id: str, plan: Dict[str, Any], execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs validation checks across executed steps to document learning updates."""
        mistakes = []
        improvements = []
        lessons_learned = []
        
        # 1. Evaluate steps
        total_steps = len(execution_results)
        failed_steps = [r for r in execution_results if not r.get("success", False)]
        retried_steps = [r for r in execution_results if r.get("retry_count", 0) > 0]
        
        # Check for mistakes
        if len(failed_steps) > 0:
            mistakes.append(f"Encountered step failures in {len(failed_steps)} nodes out of {total_steps}.")
            lessons_learned.append("Validate terminal path existence and user parameter schema constraints prior to execution launches.")
            improvements.append("Integrate dynamic pre-flight checks on paths or system permissions to prevent failure states.")
            
        if len(retried_steps) > 0:
            mistakes.append(f"Steps were retried {len(retried_steps)} times due to transient failures or network latency.")
            lessons_learned.append("Slightly increase step execution timeouts or pre-allocate caching variables for terminal jobs.")
            improvements.append("Establish exponential backoffs or pre-cache local environments before running long terminal subprocesses.")

        # If overall execution was fully clean and fast
        if len(failed_steps) == 0 and len(retried_steps) == 0:
            lessons_learned.append("Topological sequential step pipelines execute faster when parallel jobs have resolved their direct prerequisite edges.")
            improvements.append("Look for redundant file checks and optimize parallel DAG tracks to save system resources in subsequent runs.")

        # Identify duplicate tool usage as a potential mistake
        tool_frequency = {}
        for step in execution_results:
            a_type = step.get("type", "unknown")
            tool_frequency[a_type] = tool_frequency.get(a_type, 0) + 1
            
        for tool, freq in tool_frequency.items():
            if freq >= 3:
                mistakes.append(f"Repetitive tool execution: {tool} ran {freq} times in a single logical trace.")
                improvements.append(f"Consolidate multiple redundant '{tool}' operations into a single coordinated script process.")

        reflection = {
            "workflow_id": workflow_id,
            "plan_id": plan.get("plan_id"),
            "evaluated_steps_count": total_steps,
            "success_rate": round(((total_steps - len(failed_steps)) / total_steps) * 100, 1) if total_steps > 0 else 100.0,
            "mistakes_identified": mistakes or ["No critical structural mistakes detected during this execution."],
            "suggested_improvements": improvements or ["Workflow executed optimally. Keep utilizing current component configuration."],
            "lessons_learned": lessons_learned or ["DAG pipeline performed as estimated."],
            "timestamp": time.time()
        }
        
        self._reflection_logs.append(reflection)
        
        global_event_bus.emit(
            "WorkflowReflected",
            "ReflectionEngine",
            {"workflow_id": workflow_id, "success_rate": reflection["success_rate"]}
        )
        return reflection

    def list_reflections(self) -> List[Dict[str, Any]]:
        return self._reflection_logs

global_reflection_engine = ReflectionEngine()
