import pytest
import io
import base64
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base, get_db
from ..main import app
from ..sync import global_sync_encryptor

# Setup SQLite in-memory test database engine specifically for intelligence runs
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
    register_payload = {"email": "apex_operator@nexus.os", "password": "supersecretpassword"}
    reg_response = client.post("/api/auth/register", json=register_payload)
    token = reg_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==================== VOICE RUNTIME TESTS ====================

def test_voice_transcribe(client, auth_headers):
    # Create raw audio file payload (dummy bytes representing 2 seconds of high wave inputs)
    audio_stream = io.BytesIO(b"\x00\x02" * 150000)
    response = client.post(
        "/api/intelligence/voice/transcribe",
        files={"file": ("user_speech.wav", audio_stream, "audio/wav")},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "confidence" in data
    assert data["confidence"] > 0.9

def test_voice_synthesize(client, auth_headers):
    payload = {
        "text": "Initiate system hyper-parameters and update the routing tables.",
        "voice_pack": "borealis",
        "speed": 1.2,
        "pitch": 0.95
    }
    response = client.post("/api/intelligence/voice/synthesize", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "base64_audio" in data
    assert data["mime_type"] == "audio/wav"

def test_voice_packs_listing(client, auth_headers):
    response = client.get("/api/intelligence/voice/voicepacks", headers=auth_headers)
    assert response.status_code == 200
    packs = response.json()
    assert len(packs) >= 3
    assert packs[0]["id"] == "zephyr"
    assert packs[0]["downloaded"] is True

def test_voice_pack_download(client, auth_headers):
    dl_payload = {"voice_id": "echo"}
    response = client.post("/api/intelligence/voice/voicepacks/download", json=dl_payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "downloaded"


# ==================== BROWSER AUTOMATION TESTS ====================

def test_browser_navigation(client, auth_headers):
    nav_payload = {"url": "https://finance.yahoo.com/quote/GOOG"}
    response = client.post("/api/intelligence/browser/navigate", json=nav_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["current_url"] == "https://finance.yahoo.com/quote/GOOG"
    assert "screenshot_url" in data

def test_browser_booking_with_approval_gate(client, auth_headers):
    # This checks that expensive or final transactions trigger Approval requests safely
    book_payload = {
        "service_type": "flight",
        "destination": "Paris, FRA",
        "price_target": 750.00
    }
    response = client.post("/api/intelligence/browser/book", json=book_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "requires_approval"
    assert data["needs_gateway"] is True
    assert "proposal" in data or "payload" in data


# ==================== LOCAL AI RUNTIME TESTS ====================

def test_local_ai_status(client, auth_headers):
    response = client.get("/api/intelligence/local_ai/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "accelerator" in data
    assert "ollama_layer_status" in data
    assert len(data["available_local_models"]) >= 2


# ==================== CROSS-DEVICE SYNC TESTS ====================

def test_cross_device_secure_sync(client, auth_headers):
    # 1. Package a dummy preferences update
    data_block = {
        "sync_type": "preferences",
        "data": {
            "assistant_personality": "Sarcastic",
            "assistant_voicepack": "borealis",
            "speaking_speed": 1.25,
            "timestamp": time.time()
        }
    }
    # 2. Encrypt using global E2EE key
    envelope = global_sync_encryptor.encrypt_payload(data_block)
    
    # 3. Post sync packet
    sync_payload = {"encrypted_envelope": envelope}
    response = client.post("/api/intelligence/sync/packet", json=sync_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["synced_records_count"] == 1


# ==================== MOBILE COMPANION TESTS ====================

def test_mobile_pairing_challenge_and_verification(client, auth_headers):
    # Get challenge
    chal_response = client.get("/api/intelligence/mobile/challenge", headers=auth_headers)
    assert chal_response.status_code == 200
    challenge = chal_response.json()
    assert "pairing_code" in challenge
    assert "qr_payload" in challenge
    
    # Verify challenge PIN
    pin_payload = {
        "candidate_pin": challenge["pairing_code"],
        "device_name": "Apex Operator iPhone 15 Pro"
    }
    verify_response = client.post("/api/intelligence/mobile/verify", json=pin_payload, headers=auth_headers)
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data["success"] is True
    assert "api_token" in verify_data

def test_mobile_delegation(client, auth_headers):
    delegate_payload = {"prompt": "Run full code linting and deploy to staging cluster."}
    response = client.post("/api/intelligence/mobile/delegate", json=delegate_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "job" in data


# ==================== TELEMETRY & SECURITY AUDIT TESTS ====================

def test_dashboard_telemetry(client, auth_headers):
    response = client.get("/api/intelligence/dashboard/telemetry", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "hardware" in data
    assert "ai_performance" in data
    assert "approval_telemetry" in data

def test_cryptographic_audits_integrity(client, auth_headers):
    response = client.get("/api/intelligence/security/audits", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["cryptographic_chain_integrity_valid"] is True
    assert len(data["registry"]) >= 1

def test_plugins_listing(client, auth_headers):
    response = client.get("/api/intelligence/plugins", headers=auth_headers)
    assert response.status_code == 200
    plugins = response.json()
    assert isinstance(plugins, list)
