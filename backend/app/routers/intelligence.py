import base64
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuthUser, OSLog
from ..auth import get_current_user

# Import subsystem packages safely
from ..voice import (
    global_tts_engine,
    global_audio_router,
    global_voice_profile_manager,
    global_conversational_loop_manager,
    SpeechRecognizer
)
from ..browser import (
    global_playwright_engine,
    global_booking_engine,
    global_shopping_engine,
    global_job_application_engine,
    global_download_handler,
    global_web_navigator
)
from ..local_ai import (
    global_hardware_detector,
    global_ollama_client,
    global_local_doc_index,
    global_hybrid_llm_router
)
from ..sync import (
    global_central_sync_engine,
    global_sync_encryptor
)
from ..mobile import (
    global_mobile_pairing_manager,
    global_mobile_intent_delegator,
    global_mobile_push_manager
)
from ..intelligence_dashboard import global_metrics_aggregator
from ..plugins import global_plugin_manager
from ..security import (
    global_rbac_manager,
    global_chained_audit_logger,
    global_sandbox_verifier,
    AccessRole
)

router = APIRouter(prefix="/api/intelligence", tags=["Intelligence Layer"])

# --- Request/Response Schemes ---
class TTSRequest(BaseModel):
    text: str
    voice_pack: Optional[str] = "zephyr"
    speed: Optional[float] = 1.0
    pitch: Optional[float] = 1.0

class DownloadVoiceRequest(BaseModel):
    voice_id: str

class NavigateRequest(BaseModel):
    url: str

class BookRequest(BaseModel):
    service_type: str # e.g. "flight", "hotel"
    destination: str
    price_target: float

class SyncPayloadRequest(BaseModel):
    encrypted_envelope: str

class PairPinRequest(BaseModel):
    candidate_pin: str
    device_name: str

class DelegatePromptRequest(BaseModel):
    prompt: str

class LocalSearchRequest(BaseModel):
    query: str


# ==================== VOICE RUNTIME ENDPOINTS ====================

@router.post("/voice/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...),
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Parses incoming waveform and transcribes spoken speech."""
    if not global_rbac_manager.has_clearance(AccessRole.OPERATOR, "request_transcribe"):
        raise HTTPException(status_code=403, detail="RBAC: Insufficient scope security privileges.")
        
    audio_data = await file.read()
    
    # Process through Audio Router (Noise reduction)
    filtered_audio = global_audio_router.process_input(audio_data)
    
    # Run transcriber
    recognizer = SpeechRecognizer()
    text = recognizer.transcribe(filtered_audio)
    
    # Log Audit block
    global_chained_audit_logger.commit_audit_entry(
        user_id=str(user.id),
        action="SpeechToText",
        details=f"Transcribed {len(audio_data)} audio bytes into string: '{text}'"
    )
    
    return {"text": text, "confidence": 0.96}

@router.post("/voice/synthesize")
def synthesize_text(
    req: TTSRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transforms written command reports into synthetic speech bytes."""
    if not global_rbac_manager.has_clearance(AccessRole.OPERATOR, "voice_input"):
        raise HTTPException(status_code=403, detail="RBAC: Insufficient permissions")
        
    try:
        wav_bytes = global_tts_engine.synthesize(
            text=req.text,
            voice_pack=req.voice_pack,
            speed=req.speed,
            pitch=req.pitch
        )
        wav_base64 = base64.b64encode(wav_bytes).decode("utf-8")
        return {
            "success": True,
            "mime_type": "audio/wav",
            "base64_audio": wav_base64,
            "text": req.text,
            "duration": round(len(wav_bytes) / 32000.0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS synthesis error: {str(e)}")

@router.get("/voice/voicepacks")
def list_voice_packs(user: AuthUser = Depends(get_current_user)):
    """Fetches voice packs catalogs and physical download markers."""
    return global_tts_engine.list_voice_packs()

@router.post("/voice/voicepacks/download")
def trigger_voice_download(req: DownloadVoiceRequest, user: AuthUser = Depends(get_current_user)):
    """Downloads voice pack components locally."""
    success = global_tts_engine.download_voice_pack(req.voice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Voice pack not found")
    return {"success": True, "voice_id": req.voice_id, "status": "downloaded"}


# ==================== BROWSER AUTOMATION ENDPOINTS ====================

@router.post("/browser/navigate")
def launch_web_navigation(req: NavigateRequest, user: AuthUser = Depends(get_current_user)):
    """Navigates and scrapes HTML structures using virtualization."""
    if not global_rbac_manager.has_clearance(AccessRole.OPERATOR, "browser_navigate"):
        raise HTTPException(status_code=403, detail="RBAC: Unauthorized browser actions.")
        
    global_playwright_engine.navigate_to(req.url)
    screenshot_file = global_playwright_engine.take_screenshot()
    
    return {
        "current_url": global_playwright_engine.current_url,
        "screenshot_url": screenshot_file,
        "status_code": 200,
        "history": global_playwright_engine._pages_history
    }

@router.post("/browser/book")
def request_travel_booking(req: BookRequest, user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Initiates reservation preparation checks, ensuring safety approvals validate payments."""
    details = {
        "destination": req.destination,
        "price": req.price_target,
        "timestamp": time.time()
    }
    
    # Query comparative deals
    deals = global_booking_engine.compare_deals(req.destination)
    best_deal = deals[0] if deals else {"price": req.price_target}
    details["price"] = best_deal.get("price", req.price_target)
    
    proposal = global_booking_engine.prepare_reservation(req.service_type, details)
    
    # Audit log
    global_chained_audit_logger.commit_audit_entry(
        user_id=str(user.id),
        action="TravelReservationCheck",
        details=f"Scanned booking to {req.destination}. Target Price: ${req.price_target}. Decision: {proposal['status']}"
    )
    
    return proposal


# ==================== LOCAL AI RUNTIME ENDPOINTS ====================

@router.get("/local_ai/status")
def query_local_ai_status(user: AuthUser = Depends(get_current_user)):
    """Gathers local host GPU capabilities and active Ollama model indices."""
    hw = global_hardware_detector.get_hardware_status()
    models_list = global_ollama_client.list_local_models()
    online = global_ollama_client.is_online()
    
    return {
        "accelerator": hw,
        "ollama_layer_status": "online" if online else "offline",
        "available_local_models": models_list
    }

@router.post("/local_ai/search")
def search_local_indices(req: LocalSearchRequest, user: AuthUser = Depends(get_current_user)):
    """Runs high-speed semantic matching locally over previously scanned PDF files."""
    results = global_local_doc_index.search(req.query)
    return {"query": req.query, "matches_count": len(results), "results": results}


# ==================== CROSS-DEVICE SYNC ENDPOINTS ====================

@router.post("/sync/packet")
def synchronise_custom_packet(req: SyncPayloadRequest, user: AuthUser = Depends(get_current_user)):
    """Decrypts incoming synchronization nodes payload and resolves storage conflicts."""
    if not global_rbac_manager.has_clearance(AccessRole.OPERATOR, "pair_device"):
        raise HTTPException(status_code=403, detail="RBAC: Cannot participate in cross-device sync.")
        
    result = global_central_sync_engine.process_incoming_sync(
        user_id=str(user.id),
        encrypted_envelope=req.encrypted_envelope
    )
    return result


# ==================== MOBILE COMPANION ENDPOINTS ====================

@router.get("/mobile/challenge")
def generate_mobile_challenge(user: AuthUser = Depends(get_current_user)):
    """Emits short lived PIN hashes and QR strings for pairing mobile devices."""
    return global_mobile_pairing_manager.generate_pairing_challenge(str(user.id))

@router.post("/mobile/verify")
def verify_mobile_pin(req: PairPinRequest, user: AuthUser = Depends(get_current_user)):
    """Verifies numeric challenges and issues encrypted session tokens."""
    return global_mobile_pairing_manager.verify_pairing_pin(
        user_id=str(user.id),
        candidate_pin=req.candidate_pin,
        device_name=req.device_name
    )

@router.post("/mobile/delegate")
def delegate_remote_intent(req: DelegatePromptRequest, user: AuthUser = Depends(get_current_user)):
    """Enables hands-free command handoffs from the companion phone interface."""
    if not global_rbac_manager.has_clearance(AccessRole.OPERATOR, "submit_delegation"):
        raise HTTPException(status_code=403, detail="RBAC: Task delegation disabled.")
        
    # Route command
    job = global_mobile_intent_delegator.delegate_task(
        user_id=str(user.id),
        prompt=req.prompt
    )
    
    return {
        "success": True,
        "message": "Task received and queued globally inside OS context.",
        "job": job
    }


# ==================== DASHBOARD & AUDITS ENDPOINTS ====================

@router.get("/dashboard/telemetry")
def retrieve_system_telemetry(user: AuthUser = Depends(get_current_user)):
    """Exposes real-time CPU performance graphs, model latencies, and approval rates."""
    return global_metrics_aggregator.gather_system_telemetry(str(user.id))

@router.get("/security/audits")
def retrieve_cryptographic_audits(user: AuthUser = Depends(get_current_user)):
    """Fetches high-integrity logs verifying cumulative hash signature traces."""
    valid = global_chained_audit_logger.verify_chain_integrity()
    return {
        "cryptographic_chain_integrity_valid": valid,
        "logs_count": len(global_chained_audit_logger.list_entries()),
        "registry": global_chained_audit_logger.list_entries()[-50:] # latest 50
    }

@router.get("/plugins")
def query_installed_plugins(user: AuthUser = Depends(get_current_user)):
    """Lists external custom hooks registered under system directories."""
    return global_plugin_manager.list_installed_plugins()
