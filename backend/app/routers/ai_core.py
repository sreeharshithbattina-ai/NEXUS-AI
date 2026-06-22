from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime

from ..database import get_db
from ..auth import get_current_user
from .. import models
from ..ai_core import (
    ModelManager,
    PromptManager,
    MemoryManager,
    ToolManager,
    SafetyManager,
    Planner,
    Reasoner,
    Executor,
    ContextManager,
    WorkflowEngine
)
from ..agents import build_and_register_all, AgentOrchestrator

router = APIRouter(prefix="/api/ai", tags=["AI OS Core Kernel"])

# --- Request/Response Pydantic Models ---

class PlanRequest(BaseModel):
    user_intent: str = Field(..., description="The objective input to orchestrate.")
    context_summary: Optional[str] = Field(None, description="Optional baseline execution context.")

class ReasonRequest(BaseModel):
    plan: Dict[str, Any] = Field(..., description="The planned stage metrics dictionary.")
    context_summary: Optional[str] = None

class ExecuteStageRequest(BaseModel):
    stage: Dict[str, Any] = Field(..., description="A single action plan stage definition.")

class ExecutePlanRequest(BaseModel):
    plan: Dict[str, Any] = Field(..., description="The dictionary containing completed stages.")

class WorkflowCreateRequest(BaseModel):
    user_intent: str
    context_summary: Optional[str] = None
    auto_trigger: bool = True

class ResumeWorkflowRequest(BaseModel):
    approved: bool

class ChangeProviderRequest(BaseModel):
    provider_name: str

class AgentRegistryUpdateRequest(BaseModel):
    agent_id: str
    enabled: bool

class OrchestrateRequest(BaseModel):
    user_intent: str
    stages: Optional[List[Dict[str, Any]]] = None
    context_summary: Optional[str] = None

# Shared singletons for configuration registry
model_manager = ModelManager()
prompt_manager = PromptManager()
tool_manager = ToolManager()
safety_manager = SafetyManager()

# Global Agent orchestration setups
shared_agent_registry = build_and_register_all(model_manager=model_manager)
shared_agent_orchestrator = AgentOrchestrator(shared_agent_registry)
orchestration_history_logs: List[Dict[str, Any]] = []

# Global WorkflowEngine thread-safe cache
global_workflow_engine = WorkflowEngine(
    planner=Planner(model_manager, prompt_manager),
    reasoner=Reasoner(model_manager, prompt_manager),
    executor=Executor(tool_manager, MemoryManager(), model_manager, safety_manager)
)

def get_context_manager() -> ContextManager:
    return ContextManager()


# --- Endpoints ---

@router.post("/plan", summary="Generate system staging sequences")
def post_plan(payload: PlanRequest, user: models.AuthUser = Depends(get_current_user)):
    planner = Planner(model_manager, prompt_manager)
    try:
        plan_res = planner.plan(payload.user_intent, payload.context_summary)
        return plan_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reason", summary="Audit alignment and confidence variables")
def post_reason(payload: ReasonRequest, user: models.AuthUser = Depends(get_current_user)):
    reasoner = Reasoner(model_manager, prompt_manager)
    try:
        reason_res = reasoner.reason(payload.plan, payload.context_summary)
        return reason_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute/stage", summary="Execute individual plan stage parameters")
def post_execute_stage(payload: ExecuteStageRequest, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    memory_manager = MemoryManager(db_session=db)
    executor = Executor(tool_manager, memory_manager, model_manager, safety_manager)
    try:
        res = executor.execute_plan_stage(payload.stage, user.id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", summary="Execute absolute verified sequence list")
def post_execute_plan(payload: ExecutePlanRequest, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    memory_manager = MemoryManager(db_session=db)
    executor = Executor(tool_manager, memory_manager, model_manager, safety_manager)
    try:
        results = executor.execute_plan(payload.plan, user.id)
        return {"stages_executed": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools", summary="List system capability registry")
def get_tools(user: models.AuthUser = Depends(get_current_user)):
    return {"registered_tools": tool_manager.get_registered_tools()}

@router.get("/models", summary="List adapters and view active models")
def get_models(user: models.AuthUser = Depends(get_current_user)):
    return {
        "active_provider": model_manager.preferred_provider,
        "available_providers": model_manager.get_provider_names(),
        "fallback_execution_order": model_manager.fallback_chain
    }

@router.put("/models", summary="Dynamically select active system LLM provider")
def put_models(payload: ChangeProviderRequest, user: models.AuthUser = Depends(get_current_user)):
    if payload.provider_name.lower() not in model_manager.get_provider_names():
        raise HTTPException(status_code=400, detail="Requested engine adapter not found in registry.")
    model_manager.set_preferred_provider(payload.provider_name)
    return {
        "status": "changed",
        "active_provider": model_manager.preferred_provider
    }

@router.get("/prompts", summary="View system directives and revisions")
def get_prompts(user: models.AuthUser = Depends(get_current_user)):
    return {"prompt_templates": prompt_manager.get_all_templates()}

# --- Workflow Management ---

@router.post("/workflows")
def create_and_run_workflow(payload: WorkflowCreateRequest, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Initializes and runs state execution."""
    # Build local database adapter instances before triggers
    local_mem = MemoryManager(db_session=db)
    local_exec = Executor(tool_manager, local_mem, model_manager, safety_manager)
    
    # Configure dynamic workflow engines
    global_workflow_engine.executor = local_exec
    
    wkf = global_workflow_engine.create_workflow(payload.user_intent, user.id, payload.context_summary)
    
    if payload.auto_trigger:
        run_wkf = global_workflow_engine.run_all(wkf["id"])
        return run_wkf
    return wkf

@router.get("/workflows")
def list_workflows(user: models.AuthUser = Depends(get_current_user)):
    # Returns workflows registered inside global thread pool matching user ID
    user_workflows = [w for w in global_workflow_engine.list_workflows() if w.get("user_id") == user.id]
    return user_workflows

@router.get("/workflows/{workflow_id}")
def get_workflow_details(workflow_id: str, user: models.AuthUser = Depends(get_current_user)):
    wkf = global_workflow_engine.get_workflow(workflow_id)
    if not wkf or wkf.get("user_id") != user.id:
        raise HTTPException(status_code=404, detail="Workflow not located.")
    return wkf

@router.post("/workflows/{workflow_id}/resume")
def resume_workflow(workflow_id: str, payload: ResumeWorkflowRequest, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    wkf = global_workflow_engine.get_workflow(workflow_id)
    if not wkf or wkf.get("user_id") != user.id:
         raise HTTPException(status_code=404, detail="Workflow not located.")
         
    # Build local session instances prior to resumption loop
    local_mem = MemoryManager(db_session=db)
    local_exec = Executor(tool_manager, local_mem, model_manager, safety_manager)
    global_workflow_engine.executor = local_exec
    
    try:
        updated = global_workflow_engine.resume_workflow(workflow_id, payload.approved)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Multi-Agent Orchestration Layer Endpoints ---

@router.get("/agents", summary="View registered specialized agents")
def get_agents(user: models.AuthUser = Depends(get_current_user)):
    return {"agents": shared_agent_registry.list_agents()}

@router.get("/agents/status", summary="Check agent health stats")
def get_agents_status(user: models.AuthUser = Depends(get_current_user)):
    agents = shared_agent_registry.list_agents()
    return {
        "total_agents": len(agents),
        "enabled_count": sum(1 for a in agents if a["enabled"]),
        "disabled_count": sum(1 for a in agents if not a["enabled"]),
        "health_status": "All systems operational" if all(a["status"] == "Healthy" for a in agents) else "Degraded"
    }

@router.put("/agents/registry", summary="Update agent registration status")
def put_agent_registry_status(payload: AgentRegistryUpdateRequest, user: models.AuthUser = Depends(get_current_user)):
    success = shared_agent_registry.set_agent_status(payload.agent_id, payload.enabled)
    if not success:
        raise HTTPException(status_code=404, detail=f"Agent '{payload.agent_id}' not found.")
    return {
        "agent_id": payload.agent_id,
        "enabled": payload.enabled,
        "status": "updated"
    }

@router.post("/agents/orchestrate", summary="Trigger dynamic multi-agent task collaboration workflow")
def post_agents_orchestrate(payload: OrchestrateRequest, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    stages = payload.stages
    if not stages:
        planner_instance = Planner(model_manager, prompt_manager)
        try:
            plan_obj = planner_instance.plan(payload.user_intent, payload.context_summary)
            stages = plan_obj.get("stages", [])
        except Exception:
            stages = [
                {"stage_id": 1, "name": "Strategic Audit", "specialty_agent": "ceo", "tool": "none", "description": "Defining orchestration parameters."},
                {"stage_id": 2, "name": "Deep Intel", "specialty_agent": "research", "tool": "none", "description": payload.user_intent},
                {"stage_id": 3, "name": "Quality Audit", "specialty_agent": "reviewer", "tool": "none", "description": "Incoherence scans."}
            ]
            
    ctx_mgr = ContextManager()
    dummy_messages = [{"role": "user", "content": payload.user_intent}]
    memory_manager = MemoryManager(db_session=db)
    
    context_matrix = ctx_mgr.build_context(
        user_id=user.id,
        messages=dummy_messages,
        memories=[],
        documents=[],
        active_tasks=[]
    )
    
    try:
        orchestrated_res = shared_agent_orchestrator.orchestrate_task(
            user_intent=payload.user_intent,
            planned_stages=stages,
            context_matrix=context_matrix
        )
        orchestrated_res["timestamp_completed"] = datetime.datetime.utcnow().isoformat() + "Z"
        orchestrated_res["user_id"] = user.id
        
        # Save to logs
        orchestration_history_logs.append(orchestrated_res)
        return orchestrated_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/history", summary="Fetch trace history log entries")
def get_agents_history(user: models.AuthUser = Depends(get_current_user)):
    user_traces = [t for t in orchestration_history_logs if t.get("user_id") == user.id]
    return {"orchestration_history": user_traces}

