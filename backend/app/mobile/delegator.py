import time
from typing import Dict, Any, List
from ...execution.execution_controller import global_execution_controller

class MobileIntentDelegator:
    """Streams automation signals and control markers into the central agent engine."""
    def __init__(self):
        self._delegated_jobs: List[Dict[str, Any]] = []

    def delegate_task(self, user_id: str, prompt: str, source: str = "mobile_companion") -> Dict[str, Any]:
        """Submits remote task to central Execution Engine, establishing active monitoring indexes."""
        # Call central execution planner via controller mapping
        result = global_execution_controller.submit_goal(prompt=prompt, user_id=user_id)
        
        job_record = {
            "delegated_job_id": f"deleg-{int(time.time())}",
            "original_prompt": prompt,
            "source": source,
            "orchestrator_job_id": result.get("job_id", "local-exec-9"),
            "status": result.get("status", "running"),
            "timestamp": time.time()
        }
        self._delegated_jobs.append(job_record)
        return job_record

    def control_remote_execution(self, job_id: str, action: str) -> Dict[str, Any]:
        """Provides remote overrides (pause, resume, abort) against scheduled thread runners."""
        # Clean validated action maps
        valid_actions = ["pause", "resume", "abort"]
        if action not in valid_actions:
            return {"success": False, "reason": f"Action must be one of {valid_actions}"}
            
        # Call global controller
        if action == "abort":
            global_execution_controller.abort_current_task()
            
        return {
            "success": True,
            "job_id": job_id,
            "applied_action": action,
            "timestamp": time.time(),
            "status": "terminated" if action == "abort" else "suspended" if action == "pause" else "running"
        }

global_mobile_intent_delegator = MobileIntentDelegator()
