import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base, get_db
from ..main import app
from ..agents import build_and_register_all, AgentMessage, AgentOrchestrator

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def auth_headers(client):
    # Auto register a testing operator and return authentication tokens
    register_payload = {"email": "multiplier@nexus.os", "password": "securepassword"}
    reg_res = client.post("/api/auth/register", json=register_payload)
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- Multi-Agent Verification Suites ---

def test_base_and_specialized_discovery(client, auth_headers):
    # GET /api/ai/agents
    res = client.get("/api/ai/agents", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "agents" in data
    agents_list = data["agents"]
    
    # Verify all 17 specialized agents exist
    registered_ids = [a["agent_id"] for a in agents_list]
    expected_agents = [
        "ceo_agent", "planner_agent", "research_agent", "coding_agent",
        "browser_agent", "automation_agent", "memory_agent", "document_agent",
        "calendar_agent", "travel_agent", "finance_agent", "learning_agent",
        "career_agent", "security_agent", "vision_agent", "health_agent", "reviewer_agent"
    ]
    for expected in expected_agents:
        assert expected in registered_ids

def test_registry_health_and_toggles(client, auth_headers):
    # GET /api/ai/agents/status
    res = client.get("/api/ai/agents/status", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_agents"] == 17
    assert data["enabled_count"] == 17
    assert data["disabled_count"] == 0
    assert data["health_status"] == "All systems operational"

    # Toggle career agent to disabled
    put_res = client.put(
        "/api/ai/agents/registry", 
        json={"agent_id": "career_agent", "enabled": False}, 
        headers=auth_headers
    )
    assert put_res.status_code == 200
    assert put_res.json()["enabled"] is False

    # Check status changed
    res2 = client.get("/api/ai/agents/status", headers=auth_headers)
    assert res2.json()["disabled_count"] == 1
    assert res2.json()["enabled_count"] == 16

    # Restore career agent status
    client.put(
        "/api/ai/agents/registry", 
        json={"agent_id": "career_agent", "enabled": True}, 
        headers=auth_headers
    )

def test_orchestrate_complex_trip_goal(client, auth_headers):
    # Simulate: "Plan a trip to Hyderabad, estimate my budget, update my calendar, and prepare a packing checklist"
    planned_collaboration_stages = [
        {"stage_id": 1, "name": "Strategic Directives", "specialty_agent": "ceo", "tool": "none", "description": "Formulate execution track"},
        {"stage_id": 2, "name": "Destination Logistics", "specialty_agent": "travel", "tool": "none", "description": "Generate itineraries for Hyderabad"},
        {"stage_id": 3, "name": "Budget Projections", "specialty_agent": "finance", "tool": "none", "description": "Calculate Hyderabad flight estimations"},
        {"stage_id": 4, "name": "Time Booking", "specialty_agent": "calendar", "tool": "none", "description": "Schedule vacation duration block"},
        {"stage_id": 5, "name": "Coherence Check", "specialty_agent": "reviewer", "tool": "none", "description": "Quality assurance validation audit"}
    ]
    
    payload = {
        "user_intent": "Plan a trip to Hyderabad, estimate my budget, update my calendar, and prepare a packing checklist",
        "stages": planned_collaboration_stages
    }
    
    t0 = time.time()
    res = client.post("/api/ai/agents/orchestrate", json=payload, headers=auth_headers)
    duration = time.time() - t0
    
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == payload["user_intent"]
    assert data["status"] == "Orchestrated"
    
    # Verify sequential timeline trace and metrics
    trace = data["timeline_trace"]
    assert len(trace) == 5
    assert trace[0]["executing_agent"] == "NEXUS CEO Coordinating Authority"
    assert trace[1]["executing_agent"] == "NEXUS Travel Consultant"
    assert trace[2]["executing_agent"] == "NEXUS Financial Advisory"
    assert trace[3]["executing_agent"] == "NEXUS Time Scheduler"
    assert trace[4]["executing_agent"] == "NEXUS QA Quality Control"
    
    # Ensure there are message logs
    msgs = data["inter_agent_messages"]
    assert len(msgs) > 0
    # Every trace should report high confidence scores
    for step in trace:
        assert step["confidence"] >= 0.85
        assert "elapsed_seconds" in step

def test_orchestration_history(client, auth_headers):
    # First trigger orchestrate
    client.post(
        "/api/ai/agents/orchestrate", 
        json={"user_intent": "Summarize coding logs"}, 
        headers=auth_headers
    )
    
    # Query GET /api/ai/agents/history
    res = client.get("/api/ai/agents/history", headers=auth_headers)
    assert res.status_code == 200
    history = res.json()["orchestration_history"]
    assert len(history) >= 1
    assert history[0]["intent"] == "Summarize coding logs"
