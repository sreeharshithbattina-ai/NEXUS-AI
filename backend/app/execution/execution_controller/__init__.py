import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from ..interfaces import IExecutionController

# Imports of sub-modules
from ..intent_engine import global_intent_engine
from ..execution_planner import global_execution_planner
from ..task_graph import TaskGraph, TaskNode
from ..confidence_engine import global_confidence_engine
from ..approval_manager import global_approval_manager
from ..reflection_engine import global_reflection_engine
from ..learning_engine import global_learning_engine
from ..experience_manager import global_experience_manager
from ..workflow_optimizer import global_workflow_optimizer
from ..recovery_engine import global_recovery_engine
from ..execution_memory import ExecutionMemory

# System imports
from ...runtime.desktop_runtime import global_desktop_runtime
from ...runtime.event_manager import global_event_bus
from ...rag import default_search_coordinator
from ...ai_core.routers.ai_core import shared_agent_orchestrator, safety_manager

logger = logging.getLogger("execution_controller")

class ExecutionWorkflow:
    """Represents a live active workflow instance being run by the controller."""
    def __init__(self, workflow_id: str, intent_info: Dict[str, Any], plan: Dict[str, Any]):
        self.workflow_id = workflow_id
        self.intent_info = intent_info
        self.plan = plan
        self.graph = TaskGraph.deserialize(plan["steps"])
        self.status = "running" # running, suspended, completed, failed, cancelled
        self.memory = ExecutionMemory()
        self.start_time = time.time()
        self.results_log: List[Dict[str, Any]] = []
        self.is_paused_for_approval: Optional[str] = None # holds approval ticket ID if suspended

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "intent_info": self.intent_info,
            "is_paused_for_approval": self.is_paused_for_approval,
            "duration": round(time.time() - self.start_time, 2),
            "steps": self.graph.serialize(),
            "results_log": self.results_log
        }

class ExecutionController(IExecutionController):
    """The master orchestrator of NEXUS AI OS execution tracks, running task-level loops securely."""
    def __init__(self):
        self._workflows: Dict[str, ExecutionWorkflow] = {}

    def get_workflow(self, workflow_id: str) -> Optional[ExecutionWorkflow]:
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> List[Dict[str, Any]]:
        return [w.to_dict() for w in self._workflows.values()]

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Kills an active program workflow and executes recovery cleanup tasks."""
        wkf = self.get_workflow(workflow_id)
        if not wkf or wkf.status not in ["running", "suspended"]:
            return False
            
        wkf.status = "cancelled"
        
        # Trigger cleanup rollback
        global_recovery_engine.attempt_recovery(
            "cancelled", {"workflow_id": workflow_id, "step_id": "all"}
        )
        global_event_bus.emit(
            "WorkflowCancelled",
            "ExecutionController",
            {"workflow_id": workflow_id}
        )
        return True

    def run_pipeline(self, user_intent: str, user_id: str = "default") -> Dict[str, Any]:
        """Entrypoint execution pipeline connecting every subsystem in NEXUS AI OS."""
        # 1. Intent Engine
        intent_info = global_intent_engine.classify_intent(user_intent)
        
        # 2. Execution Planner
        plan = global_execution_planner.generate_plan(intent_info)
        
        workflow_id = f"wkf-{str(uuid.uuid4())[:8]}"
        workflow = ExecutionWorkflow(workflow_id, intent_info, plan)
        self._workflows[workflow_id] = workflow
        
        # Log flow start
        global_event_bus.emit(
            "WorkflowStarted",
            "ExecutionController",
            {"workflow_id": workflow_id, "user_intent": user_intent}
        )
        
        return self._execute_workflow_loop(workflow, user_id)

    def resume_workflow(self, workflow_id: str, approved: bool, user_id: str = "default") -> Dict[str, Any]:
        """Resumes a workflow that was suspended at an interactive human approval gate."""
        workflow = self.get_workflow(workflow_id)
        if not workflow or workflow.status != "suspended":
            return {"success": False, "reason": "Workflow is not suspended."}

        ticket_id = workflow.is_paused_for_approval
        if approved:
            # Mark the suspended step as ready to run or resolve it
            # Clear paused states
            workflow.is_paused_for_approval = None
            workflow.status = "running"
            
            # Resolve the ticket inside ApprovalManager
            global_approval_manager.resolve_approval(ticket_id, approved=True)
            
            # Retrieve node that was blocked
            blocked_nodes = [node for node in workflow.graph.nodes.values() if node.status == "suspended"]
            for n in blocked_nodes:
                n.status = "pending" # unlock
                
            global_event_bus.emit(
                "WorkflowResumed",
                "ExecutionController",
                {"workflow_id": workflow_id, "ticket_id": ticket_id}
            )
            return self._execute_workflow_loop(workflow, user_id)
        else:
            # Rejected
            workflow.status = "failed"
            workflow.is_paused_for_approval = None
            global_approval_manager.resolve_approval(ticket_id, approved=False)
            
            blocked_nodes = [node for node in workflow.graph.nodes.values() if node.status == "suspended"]
            for n in blocked_nodes:
                n.status = "failed"
                
            global_event_bus.emit(
                "WorkflowFailed",
                "ExecutionController",
                {"workflow_id": workflow_id, "reason": "User rejected safety approval."}
            )
            return workflow.to_dict()

    def _execute_workflow_loop(self, wkf: ExecutionWorkflow, user_id: str) -> Dict[str, Any]:
        """Iteratively fires ready steps in the topological DAG, handling pause nodes and RAG queries."""
        graph = wkf.graph
        
        while not graph.is_completed() and not graph.has_failures():
            ready_steps = graph.get_ready_steps()
            if not ready_steps:
                break
                
            for step in ready_steps:
                # Interpolate placeholding variables from global execution Memory
                resolved_params = wkf.memory.resolve_placeholders(step.params)
                
                # Check Approval Manager Gate
                if global_approval_manager.requires_approval(step.action_type, resolved_params):
                    step.status = "suspended"
                    wkf.status = "suspended"
                    ticket_id = global_approval_manager.suspend_for_approval(
                        wkf.workflow_id, step.step_id, f"Authorize {step.name} with details: {resolved_params}"
                    )
                    wkf.is_paused_for_approval = ticket_id
                    
                    return wkf.to_dict()
                
                step.status = "running"
                global_event_bus.emit(
                    "WorkflowProgress",
                    "ExecutionController",
                    {"workflow_id": wkf.workflow_id, "step_id": step.step_id, "message": f"Running: {step.name}"}
                )
                
                step_start = time.time()
                step_success = False
                step_result = None
                
                try:
                    # RAG Context retrieval
                    rag_context = ""
                    if step.action_type == "search_rag":
                        query = resolved_params.get("query", "Default query")
                        rag_res = default_search_coordinator.coordinate_search(query)
                        step_result = {"results": rag_res}
                        step_success = True
                        rag_context = str([r.get("text", "") for r in rag_res.get("retrieved_chunks", [])])
                    
                    # Agent Orchestrations
                    elif step.agent_target != "none":
                        # Runs multi-agent orchestrator
                        payload_intent = f"{step.name} using RAG details: {rag_context}"
                        orchestration_res = shared_agent_orchestrator.orchestrate_task(
                            user_intent=payload_intent,
                            planned_stages=[{
                                "stage_id": 1,
                                "name": step.name,
                                "specialty_agent": step.agent_target,
                                "tool": step.action_type,
                                "description": str(resolved_params)
                            }],
                            context_matrix={"user_id": user_id, "workspace": "."}
                        )
                        step_result = {"orchestration": orchestration_res}
                        step_success = True
                    
                    # Tool Executions on Desktop Runtime
                    else:
                        tool_res = global_desktop_runtime.execute_action(step.action_type, resolved_params, user_id=user_id)
                        step_result = tool_res
                        step_success = tool_res.get("success", False)

                except Exception as e:
                    step_result = {"error": str(e)}
                    step_success = False
                    
                step_duration = time.time() - step_start
                
                # Check for needed recoveries on failures
                if not step_success:
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        step.status = "pending" # resets to retry
                        # Trigger recovery engine
                        global_recovery_engine.attempt_recovery("tool_failure", {
                            "step_id": step.step_id,
                            "workflow_id": wkf.workflow_id,
                            "action_type": step.action_type,
                            "params": resolved_params
                        })
                        continue
                    else:
                        step.status = "failed"
                else:
                    step.status = "completed"
                    step.result = step_result
                    wkf.memory.set_step_output(step.step_id, step_result)
                    
                # Track logged records
                run_log = {
                    "step_id": step.step_id,
                    "type": step.action_type,
                    "target": step.agent_target,
                    "success": step_success,
                    "duration": round(step_duration, 2),
                    "retry_count": step.retry_count,
                    "result": step_result
                }
                wkf.results_log.append(run_log)

        # Post Execution Reflection, Learning, and Experience indices
        if graph.is_completed():
            wkf.status = "completed"
            duration = time.time() - wkf.start_time
            
            # Log Experience
            global_experience_manager.log_experience(
                wkf.plan["plan_id"], wkf.intent_info["user_intent"], success=True, steps_count=len(wkf.results_log), duration_sec=duration
            )
            
            # Execute reflection engine auditing
            reflection_res = global_reflection_engine.reflect(wkf.workflow_id, wkf.plan, wkf.results_log)
            wkf.results_log.append({"reflection": reflection_res})

            # Preference Learning Extracts
            dummy_convo_history = [{"content": wkf.intent_info["user_intent"]}]
            global_learning_engine.extract_preferences(user_id, dummy_convo_history)
            
            global_event_bus.emit(
                "WorkflowCompleted",
                "ExecutionController",
                {"workflow_id": wkf.workflow_id}
            )
            
        elif graph.has_failures():
            wkf.status = "failed"
            duration = time.time() - wkf.start_time
            global_experience_manager.log_experience(
                wkf.plan["plan_id"], wkf.intent_info["user_intent"], success=False, steps_count=len(wkf.results_log), duration_sec=duration
            )
            
            global_event_bus.emit(
                "WorkflowFailed",
                "ExecutionController",
                {"workflow_id": wkf.workflow_id, "reason": "A step failed after maximum retried bounds."}
            )

        return wkf.to_dict()

global_execution_controller = ExecutionController()
