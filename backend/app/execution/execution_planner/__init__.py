from typing import Dict, Any, List, Optional
import uuid
from ..interfaces import IExecutionPlanner
from ..task_graph import TaskGraph, TaskNode

class ExecutionPlanner(IExecutionPlanner):
    """Translates categorized objectives into topological task DAG execution plans."""
    def __init__(self):
        pass

    def generate_plan(self, goal: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Maps classified user intent objects into a standard Directed Acyclic Graph."""
        intent_cat = goal.get("primary_category", "Conversation")
        user_intent = goal.get("user_intent", "")
        params = goal.get("parameters", {})
        
        graph = TaskGraph()
        plan_id = f"plan-{str(uuid.uuid4())[:8]}"
        
        if intent_cat == "Coding":
            # Generate coding-centric DAG: RAG search -> write files -> compile/test check
            step1 = graph.add_step(
                step_id="step-rag-code-context",
                name="Retrieve coding guidelines and workspace files",
                action_type="search_rag",
                agent_target="research",
                params={"query": f"Code implementation patterns for {user_intent}"}
            )
            
            target_path = params.get("file_path", "src/solution.py")
            step2 = graph.add_step(
                step_id="step-write-code",
                name=f"Generate and write source file to {target_path}",
                action_type="write_file",
                agent_target="coding",
                params={"path": target_path, "content": "# Generated solution code\nprint('Nexus OS active')"},
                depends_on=[step1.step_id]
            )
            
            # Submits test run
            step3 = graph.add_step(
                step_id="step-test-compile",
                name="Run compilation or test validation in terminal",
                action_type="run_command",
                agent_target="automation",
                params={"command": f"python {target_path}"},
                depends_on=[step2.step_id],
                max_retries=3
            )
            
            # Setup conditional path branch if validation fails
            step3.conditional_branch = {
                "condition": "last_step_failed == True",
                "then_steps": [
                    {
                        "step_id": "step-auto-correct-source",
                        "name": "Auto-correct source syntax anomalies",
                        "action_type": "write_file",
                        "agent_target": "coding",
                        "params": {"path": target_path, "content": "# Rectified syntax\nprint('Nexus OS active - Rectified')"}
                    }
                ]
            }

        elif intent_cat == "File Operation":
            # Generates workspace file ops
            target_path = params.get("file_path", "workspace/notes.txt")
            step1 = graph.add_step(
                step_id="step-check-exists",
                name="Scan directory for target files",
                action_type="read_file",
                agent_target="document",
                params={"path": target_path},
                max_retries=1
            )
            
            step2 = graph.add_step(
                step_id="step-write-log-backup",
                name="Write safety backup file",
                action_type="write_file",
                agent_target="document",
                params={"path": f"{target_path}.bak", "content": "Backup trace"},
                depends_on=[step1.step_id]
            )
            
            step3 = graph.add_step(
                step_id="step-delete-unneeded",
                name="Delete transient workspace document",
                action_type="delete_file",
                agent_target="security",
                params={"path": target_path, "force": False},
                depends_on=[step2.step_id]
            )

        elif intent_cat == "Scheduling":
            # Parallel scheduling activities
            step1 = graph.add_step(
                step_id="step-check-calendar",
                name="Queries conflict blocks inside Calendar",
                action_type="read_file",
                agent_target="calendar",
                params={"path": "schedule.json"}
            )
            
            # Runs step 2 & 3 in parallel because both depend only on step1
            step2 = graph.add_step(
                step_id="step-book-meeting",
                name="Commit new calendar meeting",
                action_type="send_email",
                agent_target="calendar",
                params={"to": "operator@nexus.ai", "subject": "Booked: Executive Sync", "body": "Calendar Event scheduled."},
                depends_on=[step1.step_id]
            )
            
            step3 = graph.add_step(
                step_id="step-queue-reminder",
                name="Schedule notification trigger alarm",
                action_type="write_file",
                agent_target="automation",
                params={"path": "reminders.json", "content": "Alarm queued"},
                depends_on=[step1.step_id]
            )

        elif intent_cat == "Travel":
            # Sequential steps for Travel plans
            step1 = graph.add_step(
                step_id="step-query-fares",
                name="Query flight prices and hotel availabilities",
                action_type="search_rag",
                agent_target="travel",
                params={"query": f"Available trips for {user_intent}"}
            )
            
            step2 = graph.add_step(
                step_id="step-book-reservation",
                name="Authorize reservations trigger",
                action_type="run_command", # triggers booking workflow via command
                agent_target="travel",
                params={"command": "python -m app.runtime.desktop_runtime --book-flight"},
                depends_on=[step1.step_id]
            )

        else:
            # Default fallback plans
            step1 = graph.add_step(
                step_id="step-rag-resolve-intel",
                name="Query local operational RAG index",
                action_type="search_rag",
                agent_target="research",
                params={"query": user_intent}
            )
            
            step2 = graph.add_step(
                step_id="step-execute-assistant-response",
                name="Synthesize and broadcast cognitive response",
                action_type="write_clipboard",
                agent_target="ceo",
                params={"text": f"Resolved: {user_intent}"},
                depends_on=[step1.step_id]
            )

        # Ensure correct topology validation
        is_valid = graph.validate_dag()
        
        return {
            "plan_id": plan_id,
            "user_intent": user_intent,
            "primary_category": intent_cat,
            "is_valid_dag": is_valid,
            "steps": graph.serialize()
        }

global_execution_planner = ExecutionPlanner()
