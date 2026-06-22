from typing import Dict, Any, List, Optional
import time
import uuid
import datetime
from ..planner import Planner
from ..reasoner import Reasoner
from ..executor import Executor

class WorkflowState:
    RECEIVED = "Received"
    PLANNING = "Planning"
    REASONING = "Reasoning"
    WAITING_FOR_APPROVAL = "WaitingForApproval"
    EXECUTING = "Executing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

class WorkflowEngine:
    """
    Coordinates state transitions for multi-stage system goals.
    Maintains timeline execution telemetry logs and supports resumption after approval prompts.
    """
    def __init__(self, planner: Planner, reasoner: Reasoner, executor: Executor):
        self.planner = planner
        self.reasoner = reasoner
        self.executor = executor
        # Active in-memory workflows
        self.workflows: Dict[str, Dict[str, Any]] = {}

    def create_workflow(self, user_intent: str, user_id: str, context: Optional[str] = None) -> Dict[str, Any]:
        workflow_id = "wkf-" + str(uuid.uuid4())[:8]
        now = datetime.datetime.utcnow().isoformat() + "Z"
        
        wkf = {
            "id": workflow_id,
            "user_id": user_id,
            "intent": user_intent,
            "state": WorkflowState.RECEIVED,
            "context": context,
            "plan": None,
            "reasoning_audit": None,
            "execution_trace": [],
            "current_stage_index": 0,
            "timeline": [
                {
                    "timestamp": now,
                    "event": "Workflow initialized.",
                    "status_from": "None",
                    "status_to": WorkflowState.RECEIVED
                }
            ],
            "metrics": {
                "created_at": now,
                "completed_at": None,
                "elapsed_ms": 0,
                "model_calls": 0,
                "tool_invocations": [],
                "errors": []
            }
        }
        self.workflows[workflow_id] = wkf
        return wkf

    def _log_event(self, workflow_id: str, event_text: str, status_from: str, status_to: str) -> None:
        wkf = self.workflows[workflow_id]
        now = datetime.datetime.utcnow().isoformat() + "Z"
        wkf["timeline"].append({
            "timestamp": now,
            "event": event_text,
            "status_from": status_from,
            "status_to": status_to
        })
        wkf["state"] = status_to

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.workflows.get(workflow_id)

    def list_workflows(self) -> List[Dict[str, Any]]:
        return list(self.workflows.values())

    def run_all(self, workflow_id: str) -> Dict[str, Any]:
        """Runs the whole workflow lifecycle sequentially."""
        wkf = self.get_workflow(workflow_id)
        if not wkf:
            raise KeyError("Workflow not found.")
            
        start_time = time.time()
        
        try:
            # 1. Planning
            if wkf["state"] == WorkflowState.RECEIVED:
                self._log_event(workflow_id, "Transitioning to Planning Stage.", wkf["state"], WorkflowState.PLANNING)
                plan = self.planner.plan(wkf["intent"], wkf["context"])
                wkf["plan"] = plan
                wkf["metrics"]["model_calls"] += 1
                
            # 2. Reasoning
            if wkf["state"] == WorkflowState.PLANNING:
                self._log_event(workflow_id, "Transitioning to Reasoning validation.", wkf["state"], WorkflowState.REASONING)
                audit = self.reasoner.reason(wkf["plan"], wkf["context"])
                wkf["reasoning_audit"] = audit
                wkf["metrics"]["model_calls"] += 1
                
                # Check for blocking loops or conflicts
                if audit.get("requires_user_clarification"):
                    self._log_event(workflow_id, f"Blocked. Missing context: {audit.get('clarification_prompt')}", wkf["state"], WorkflowState.WAITING_FOR_APPROVAL)
                    wkf["metrics"]["elapsed_ms"] += int((time.time() - start_time) * 1000)
                    return wkf
                    
            # 3. Execution
            if wkf["state"] == WorkflowState.REASONING:
                self._log_event(workflow_id, "Action plan validated. Directing to Executor.", wkf["state"], WorkflowState.EXECUTING)
                
            if wkf["state"] in [WorkflowState.EXECUTING, WorkflowState.WAITING_FOR_APPROVAL]:
                plan = wkf["plan"]
                stages = plan.get("stages", []) if plan else []
                
                # Sequential resume execution logic
                for idx in range(wkf["current_stage_index"], len(stages)):
                    stage = stages[idx]
                    step_res = self.executor.execute_plan_stage(stage, wkf["user_id"])
                    wkf["execution_trace"].append(step_res)
                    wkf["current_stage_index"] = idx + 1
                    
                    if step_res.get("tool_used") and step_res.get("tool_used") != "none":
                        wkf["metrics"]["tool_invocations"].append({
                            "tool": step_res["tool_used"],
                            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
                        })
                        
                    if step_res.get("requires_approval"):
                        self._log_event(workflow_id, f"Manual approval required for tool: '{step_res['tool']}'", wkf["state"], WorkflowState.WAITING_FOR_APPROVAL)
                        wkf["metrics"]["elapsed_ms"] += int((time.time() - start_time) * 1000)
                        return wkf
                        
                    if step_res.get("status") == "failed":
                        wkf["metrics"]["errors"].append(step_res.get("result", {}).get("message", "Unknown stage error"))
                        self._log_event(workflow_id, f"Execution halted due to step failure.", wkf["state"], WorkflowState.FAILED)
                        wkf["metrics"]["elapsed_ms"] += int((time.time() - start_time) * 1000)
                        wkf["metrics"]["completed_at"] = datetime.datetime.utcnow().isoformat() + "Z"
                        return wkf
                        
                # Completed successfully
                self._log_event(workflow_id, "All actions successfully completed.", wkf["state"], WorkflowState.COMPLETED)
                
        except Exception as e:
            wkf["metrics"]["errors"].append(str(e))
            self._log_event(workflow_id, f"Core Workflow failure: {str(e)}", wkf["state"], WorkflowState.FAILED)
            
        wkf["metrics"]["elapsed_ms"] += int((time.time() - start_time) * 1000)
        wkf["metrics"]["completed_at"] = datetime.datetime.utcnow().isoformat() + "Z"
        return wkf

    def resume_workflow(self, workflow_id: str, approved: bool) -> Dict[str, Any]:
        """Resumes WAITING_FOR_APPROVAL status with approved/rejected directives."""
        wkf = self.get_workflow(workflow_id)
        if not wkf or wkf["state"] != WorkflowState.WAITING_FOR_APPROVAL:
            raise RuntimeError("Workflow is not waiting for manual approval.")
            
        if not approved:
            self._log_event(workflow_id, "User rejected approval block. Workflow cancelled.", wkf["state"], WorkflowState.CANCELLED)
            wkf["metrics"]["completed_at"] = datetime.datetime.utcnow().isoformat() + "Z"
            return wkf
            
        # Transition back to Executing
        self._log_event(workflow_id, "User approved block. Continuing execution sequence.", wkf["state"], WorkflowState.EXECUTING)
        return self.run_all(workflow_id)
