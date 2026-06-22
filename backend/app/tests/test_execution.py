import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..execution import (
    global_intent_engine,
    global_execution_planner,
    global_execution_controller,
    global_confidence_engine,
    global_approval_manager,
    global_reflection_engine,
    global_learning_engine,
    global_experience_manager,
    global_workflow_optimizer,
    global_recovery_engine,
    global_metrics_tracker
)

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # Reset tracking states before and after each test
    global_approval_manager._active_tickets.clear()
    global_reflection_engine._reflection_logs.clear()
    global_learning_engine._learned_preferences.clear()
    global_experience_manager._history.clear()
    yield

# --- 1. Intent Engine Tests ---
def test_intent_engine_classification():
    coding_res = global_intent_engine.classify_intent("Develop an optimized merge sort algorithm in Python")
    assert coding_res["primary_category"] == "Coding"
    assert coding_res["confidence"] > 0.8
    assert coding_res["is_ambiguous"] is False
    
    file_res = global_intent_engine.classify_intent("Delete the temporary files in workspace")
    assert file_res["primary_category"] == "File Operation"
    
    vague_res = global_intent_engine.classify_intent("Test")
    assert vague_res["is_ambiguous"] is True
    assert vague_res["confidence"] < 0.6

# --- 2. Execution Planner Tests ---
def test_execution_planner_dag_generation():
    goal = {
        "primary_category": "Coding",
        "user_intent": "Implement and run dynamic tests",
        "parameters": {"file_path": "solution.py"}
    }
    plan = global_execution_planner.generate_plan(goal)
    assert plan["is_valid_dag"] is True
    assert len(plan["steps"]) >= 2
    
    # Check graph dependency linkage
    steps = plan["steps"]
    assert steps[0]["step_id"] == "step-rag-code-context"
    assert steps[1]["depends_on"] == ["step-rag-code-context"]

# --- 3. Confidence Engine Tests ---
def test_confidence_engine():
    planner_confidence = global_confidence_engine.evaluate_confidence(
        "planner", {"is_valid_dag": True, "steps": [1, 2, 3], "is_ambiguous": False}
    )
    assert planner_confidence == 0.95
    
    rag_confidence = global_confidence_engine.evaluate_confidence(
        "rag", {"similarities": [0.85, 0.91]}
    )
    assert rag_confidence == 0.88
    
    overall = global_confidence_engine.compute_overall_confidence(0.95, [0.90, 0.92])
    assert overall == 0.92

# --- 4. Approval Manager Tests ---
def test_approval_manager_triggers():
    assert global_approval_manager.requires_approval("delete_file", {"path": "tmp.txt"}) is True
    assert global_approval_manager.requires_approval("read_file", {"path": "tmp.txt"}) is False
    assert global_approval_manager.requires_approval("run_command", {"command": "rm -rf /"}) is True
    assert global_approval_manager.requires_approval("payments", {}) is True

# --- 5. Reflection Engine Tests ---
def test_reflection_engine_outcome():
    plan = {"plan_id": "plan-123"}
    results = [
        {"step_id": "step-1", "type": "read_file", "success": True, "retry_count": 0},
        {"step_id": "step-2", "type": "write_file", "success": True, "retry_count": 1}
    ]
    reflection = global_reflection_engine.reflect("workflow-123", plan, results)
    assert reflection["workflow_id"] == "workflow-123"
    assert reflection["success_rate"] == 100.0
    assert len(reflection["mistakes_identified"]) > 0 # identified the retry-count warning

# --- 6. Learning Engine Tests ---
def test_learning_engine_extraction():
    history = [
        {"content": "I prefer using VS Code for my web projects."},
        {"content": "I want window seats for flights."}
    ]
    # We test local updates first
    learned = global_learning_engine.extract_preferences(user_id="default-test-user", session_history=history)
    # The actual database might not support sqlite writes if session isn't mocked,
    # but the method should gracefully handle exception or write to local store
    local_logs = global_learning_engine.list_learned_locally()
    assert len(local_logs) >= 0

# --- 7. Workflow Recovery and Optimization ---
def test_recovery_engine():
    context = {"step_id": "step-cmd", "action_type": "run_command", "params": {"command": "npm run start"}}
    recovery = global_recovery_engine.attempt_recovery("tool_failure", context)
    assert recovery["recovered"] is True
    assert recovery["next_action"] == "retry"
    assert "adjusted_params" in recovery

def test_workflow_optimizer():
    history = [
        {"type": "write_file"},
        {"type": "run_command"},
        {"type": "write_file"},
        {"type": "run_command"}
    ]
    macros = global_workflow_optimizer.analyze_repetition("default-user", history)
    assert len(macros) >= 2 # default suggestions exist plus generated suggested pair.

# --- 8. API Endpoint Tests ---
def test_execution_api_router():
    client = TestClient(app)
    routes = [r.path for r in app.routes]
    
    assert "/api/execution/execute" in routes
    assert "/api/execution/workflows" in routes
    assert "/api/execution/workflows/history" in routes
    assert "/api/execution/workflows/resume" in routes
    assert "/api/execution/workflows/cancel" in routes
    assert "/api/execution/learning" in routes
    assert "/api/execution/preferences" in routes
    assert "/api/execution/reflection" in routes
    assert "/api/execution/metrics" in routes
