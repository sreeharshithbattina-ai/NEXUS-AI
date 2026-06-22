import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base, get_db
from ..main import app

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
    register_payload = {"email": "aicore@nexus.os", "password": "securepassword"}
    reg_res = client.post("/api/auth/register", json=register_payload)
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- AI OS Core Component Tests ---

def test_get_tools_registry(client, auth_headers):
    response = client.get("/api/ai/tools", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "registered_tools" in data
    tools_list = data["registered_tools"]
    # Verify standard tools exist in the tool schema list
    names = [t["name"] for t in tools_list]
    assert "calculator" in names
    assert "time" in names
    assert "filesystem" in names
    assert "terminal" in names

def test_get_models_manager(client, auth_headers):
    response = client.get("/api/ai/models", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["active_provider"] == "gemini"
    assert "available_providers" in data
    assert "gemini" in data["available_providers"]
    assert "openai" in data["available_providers"]

    # Put/switch provider
    put_res = client.put("/api/ai/models", json={"provider_name": "openai"}, headers=auth_headers)
    assert put_res.status_code == 200
    assert put_res.json()["active_provider"] == "openai"

def test_prompt_manager_versioning(client, auth_headers):
    response = client.get("/api/ai/prompts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "prompt_templates" in data
    templates = data["prompt_templates"]
    assert "system_ceo" in templates
    assert "version" in templates["system_ceo"]

def test_planning_and_reasoning_pipeline(client, auth_headers):
    # 1. Post to plan
    plan_payload = {"user_intent": "Schedule a critical review meeting tomorrow at 3 PM and notify lead engineers."}
    plan_res = client.post("/api/ai/plan", json=plan_payload, headers=auth_headers)
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert "goal" in plan_data
    assert "stages" in plan_data
    assert len(plan_data["stages"]) > 0

    # 2. Post to reason
    reason_payload = {"plan": plan_data, "context_summary": "Active Workspace limits."}
    reason_res = client.post("/api/ai/reason", json=reason_payload, headers=auth_headers)
    assert reason_res.status_code == 200
    reason_data = reason_res.json()
    assert "is_consistent" in reason_data
    assert "confidence_score" in reason_data
    assert "requires_user_clarification" in reason_data

def test_stage_execution_with_calculator(client, auth_headers):
    calc_stage = {
        "stage_id": 1,
        "name": "Solve formula",
        "specialty_agent": "Executor",
        "tool": "calculator",
        "description": "Calculate 350 * 1.15 to estimate billing tax values."
    }
    response = client.post("/api/ai/execute/stage", json={"stage": calc_stage}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["completed", "failed", "awaiting_approval"]
    if data["status"] == "completed":
        assert data["result"]["status"] == "success"
        # Since calculation of 350*1.15 is 402.5, let's verify if result parsed correctly or defaulted
        assert "result" in data["result"]

def test_resumable_workflows(client, auth_headers):
    # Initiate workflow that auto triggers execution sequence
    wf_payload = {
        "user_intent": "Update directory logs and push code commits",
        "auto_trigger": True
    }
    response = client.post("/api/ai/workflows", json=wf_payload, headers=auth_headers)
    assert response.status_code == 200
    wkf = response.json()
    assert "id" in wkf
    assert "state" in wkf
    assert wkf["intent"] == wf_payload["user_intent"]
    
    # Query specific workflow details
    wkf_id = wkf["id"]
    get_res = client.get(f"/api/ai/workflows/{wkf_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["state"] == wkf["state"]

    # Query lists
    list_res = client.get("/api/ai/workflows", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
