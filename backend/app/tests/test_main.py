import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base, get_db
from ..main import app

# Setup local SQLite in-memory test database engine
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

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_register_and_login(client):
    # Register check
    register_payload = {"email": "operator@nexus.os", "password": "securepassword"}
    response = client.post("/api/auth/register", json=register_payload)
    assert response.status_code == 201
    reg_data = response.json()
    assert "access_token" in reg_data
    assert reg_data["user_email"] == "operator@nexus.os"

    # Repeated Register (fail state)
    fail_response = client.post("/api/auth/register", json=register_payload)
    assert fail_response.status_code == 400

    # Login check
    login_payload = {"email": "operator@nexus.os", "password": "securepassword"}
    login_response = client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data

def test_profile_retrieval(client):
    # Register and login to retrieve access token
    register_payload = {"email": "profile@nexus.os", "password": "securepassword"}
    reg_response = client.post("/api/auth/register", json=register_payload)
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch initial default profile
    profile_response = client.get("/api/profile", headers=headers)
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["name"] == "Apex Operator"
    assert profile_data["assistantPreferences"]["personality"] == "Balanced"

    # Update profile settings
    update_payload = {
        "name": "NEXUS Core Administrator",
        "assistantPreferences": {
            "personality": "Sarcastic",
            "speakingSpeed": 1.2,
            "voicepack": " Fenrir",
            "allowAlwaysListening": True,
            "requireApprovalForFinancial": False,
            "model": "gemini-3.5-flash"
        }
    }
    put_response = client.put("/api/profile", json=update_payload, headers=headers)
    assert put_response.status_code == 200
    put_data = put_response.json()
    assert put_data["name"] == "NEXUS Core Administrator"
    assert put_data["assistantPreferences"]["personality"] == "Sarcastic"
    assert put_data["assistantPreferences"]["speakingSpeed"] == 1.2

def test_memories_crud(client):
    register_payload = {"email": "memory@nexus.os", "password": "securepassword"}
    reg_response = client.post("/api/auth/register", json=register_payload)
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch empty memories list
    list_response = client.get("/api/memories", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 0

    # Add new memory item
    mem_payload = {
        "content": "Operator double-clicks vector items to trigger citations",
        "type": "semantic",
        "category": "Preference",
        "tags": ["ui", "clicks"],
        "confidence": 0.95
    }
    create_response = client.post("/api/memories", json=mem_payload, headers=headers)
    assert create_response.status_code == 201
    mem_item = create_response.json()
    assert mem_item["content"] == mem_payload["content"]
    assert mem_item["tags"] == ["ui", "clicks"]

    # Delete memory item
    mem_id = mem_item["id"]
    del_response = client.delete(f"/api/memories/{mem_id}", headers=headers)
    assert del_response.status_code == 200
    assert del_response.json()["status"] == "purged"

def test_documents_and_rag(client):
    register_payload = {"email": "docs@nexus.os", "password": "securepassword"}
    reg_response = client.post("/api/auth/register", json=register_payload)
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Save and chunk document
    doc_payload = {
        "title": "Vocal Synthesizer instructions.txt",
        "content": "High speed voice synthesis operates over offline CPU modes.\nAlways request audio buffer streams sequentially."
    }
    doc_response = client.post("/api/documents", json=doc_payload, headers=headers)
    assert doc_response.status_code == 201
    doc_data = doc_response.json()
    assert doc_data["title"] == "Vocal Synthesizer instructions.txt"
    assert len(doc_data["chunks"]) == 2

    # Query lists
    doc_list = client.get("/api/documents", headers=headers)
    assert doc_list.status_code == 200
    assert len(doc_list.json()) == 1
