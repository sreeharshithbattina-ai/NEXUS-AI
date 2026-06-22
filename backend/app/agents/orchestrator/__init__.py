import time
import datetime
from typing import Dict, Any, List, Optional
from ..registry import AgentRegistry
from ..communication import AgentMessage

class AgentOrchestrator:
    """
    Central Orchestrator coordinating specialized agents, formulating sequential-parallel tracks,
    gathering traces, resolving conflicting schemas, and emitting unified responses.
    """
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def orchestrate_task(self, 
                         user_intent: str, 
                         planned_stages: List[Dict[str, Any]], 
                         context_matrix: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes list of planned steps (from Planner output), maps and executes specialized agents,
        keeps the active message history stream, and returns a unified outcome.
        """
        start_time = time.time()
        agent_traces = []
        message_history = []
        
        # Mapping helpers for specialty names -> registered agent ids
        agent_map = {
            "ceo": "ceo_agent",
            "planner": "planner_agent",
            "research": "research_agent",
            "coding": "coding_agent",
            "browser": "browser_agent",
            "automation": "automation_agent",
            "memory": "memory_agent",
            "document": "document_agent",
            "calendar": "calendar_agent",
            "travel": "travel_agent",
            "finance": "finance_agent",
            "learning": "learning_agent",
            "career": "career_agent",
            "security": "security_agent",
            "vision": "vision_agent",
            "health": "health_agent",
            "reviewer": "reviewer_agent"
        }
        
        # 1. Sequential Execution of Stages
        for stage in planned_stages:
            stage_id = stage.get("stage_id", 1)
            stage_name = stage.get("name", "Unnamed Stage")
            specialty_name = str(stage.get("specialty_agent", "ceo")).lower()
            associated_tool = stage.get("tool", "none")
            stage_desc = stage.get("description", user_intent)
            
            # Lookup target agent
            target_agent_id = agent_map.get(specialty_name, "ceo_agent")
            agent = self.registry.get_agent(target_agent_id)
            if not agent or not agent.enabled:
                # Fallback to CEO Agent
                agent = self.registry.get_agent("ceo_agent")
                
            agent_start = time.time()
            agent_id = agent.agent_id if agent else "ceo_agent"
            agent_name = agent.name if agent else "CEO"
            
            # 2. Formulate Structured Nachricht (Message)
            msg = AgentMessage(
                sender="orchestrator",
                receiver=agent_id,
                task=stage_desc,
                context=context_matrix,
                confidence=0.95
            )
            message_history.append(msg.to_dict())
            
            # 3. Trigger Agent Execution Lifecycle
            try:
                lifecycle_res = agent.run_lifecycle(
                    task=stage_desc,
                    context=context_matrix,
                    tools=[],
                    memory_orders={}
                ) if agent else {"output": f"CEO coordinates: {stage_desc}"}
                
                # Register response feedback
                confidence_rating = lifecycle_res.get("confidence_score", 0.95)
                
                trace_entry = {
                    "stage_id": stage_id,
                    "stage_name": stage_name,
                    "executing_agent": agent_name,
                    "agent_id": agent_id,
                    "tool": associated_tool,
                    "status": "Success",
                    "result": lifecycle_res,
                    "confidence": confidence_rating,
                    "elapsed_seconds": round(time.time() - agent_start, 3)
                }
            except Exception as e:
                trace_entry = {
                    "stage_id": stage_id,
                    "stage_name": stage_name,
                    "executing_agent": agent_name,
                    "agent_id": agent_id,
                    "tool": associated_tool,
                    "status": "Failed",
                    "error": str(e),
                    "confidence": 0.0,
                    "elapsed_seconds": round(time.time() - agent_start, 3)
                }
                
            agent_traces.append(trace_entry)
            
            # Notify trace loop
            feedback_msg = AgentMessage(
                sender=agent_id,
                receiver="orchestrator",
                task=f"Completed {stage_name}",
                context=context_matrix,
                confidence=trace_entry.get("confidence", 0.9),
                payload=lifecycle_res if "lifecycle_res" in locals() else {}
            )
            message_history.append(feedback_msg.to_dict())

        # 4. Invoke Reviewer / Conflict Resolution if we have multiple outputs
        reviewer = self.registry.get_agent("reviewer_agent")
        conflict_resolved_status = "Approved without outstanding conflicts"
        if reviewer and reviewer.enabled:
            rev_start = time.time()
            rev_res = reviewer.run_lifecycle(
                task=f"Audit trace paths for: '{user_intent}'",
                context={"outputs": agent_traces},
                tools=[],
                memory_orders={}
            )
            conflict_resolved_status = rev_res.get("qa_feedback", "All stages conform to QA protocols.")
            
        return {
            "intent": user_intent,
            "status": "Orchestrated",
            "timeline_trace": agent_traces,
            "inter_agent_messages": message_history,
            "conflict_audit_feedback": conflict_resolved_status,
            "total_latency_seconds": round(time.time() - start_time, 3)
        }
