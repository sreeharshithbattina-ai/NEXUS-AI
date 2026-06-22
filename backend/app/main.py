import datetime
import uuid
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, Base, get_db
from . import models, schemas, auth
from .auth import get_current_user

# Create tables in SQLite/Postgres automatically if in development mode
if settings.ENVIRONMENT == "development":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NEXUS AI OS Core API Backend",
    description="Production-grade personal artificial intelligence operating system core backend service built with FastAPI, SQLite/PostgreSQL, Clean Architecture and SOLID principles.",
    version="1.0.0",
)

# CORS Middlewares to securely integrate and allow cross origin lookups
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated Redis cache layer
class RedisMock:
    def __init__(self):
        self._store = {}
    def get(self, key: str) -> Optional[str]:
        return self._store.get(key)
    def set(self, key: str, value: str, ex: Optional[int] = None):
        self._store[key] = value
    def delete(self, key: str):
        if key in self._store:
            del self._store[key]

redis_client = RedisMock()

# API Health Check Endpoint
@app.get("/api/health", tags=["System"])
def health_check():
    """Outputs current container integrity and heartbeat status metrics."""
    return {
        "status": "healthy",
        "service": "NEXUS AI OS Core Service",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "database": "online",
        "cache": "redis-simulated-ok" if redis_client else "no-cache",
    }

# --- 1. Authentication Router ---
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=schemas.Token, status_code=201)
def register_user(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    """Registers a clean, fresh identity credentials block inside Secure Kernel Vault."""
    db_user = db.query(models.AuthUser).filter(models.AuthUser.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Address already linked to an active identity credentials block."
        )
    h_pass = auth.get_password_hash(user_in.password)
    new_user = models.AuthUser(email=user_in.email, hashed_password=h_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-initialize user profile configurations
    default_profile = models.UserProfile(
        user_id=new_user.id,
        name="Apex Operator",
        assistant_personality="Balanced",
        assistant_voicepack="Zephyr",
        speaking_speed=1.0,
        allow_always_listening=False,
        require_approval_for_financial=True,
        schedule_json=[],
        reminders_json=[]
    )
    db.add(default_profile)
    
    # Auto-seed startup initial records
    log = models.OSLog(
        user_id=new_user.id,
        level="info",
        source="Kernel",
        message=f"Created active operator core user space block for {user_in.email} successfully."
    )
    db.add(log)
    db.commit()

    token = auth.create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer", "user_email": new_user.email}

@auth_router.post("/login", response_model=schemas.Token)
def login_user(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    """Validates user security parameters and issues cryptographic JWT scope locks."""
    db_user = db.query(models.AuthUser).filter(models.AuthUser.email == user_in.email).first()
    if not db_user or not auth.verify_password(user_in.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect cryptographic security identity credentials pairing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful kernel login audit
    log = models.OSLog(
        user_id=db_user.id,
        level="success",
        source="Security",
        message="Operator authenticated successfully. Initialized clean runtime session."
    )
    db.add(log)
    db.commit()

    token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer", "user_email": db_user.email}

app.include_router(auth_router)

# Import and include the AI Core Router
from .routers import ai_core
app.include_router(ai_core.router)

# --- 2. Profile Router ---
profile_router = APIRouter(prefix="/api/profile", tags=["User Profile"])

@profile_router.get("", response_model=schemas.UserProfileSchema)
def get_user_profile(user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieves standard identity metadata settings file."""
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User preference file missing.")
    
    return {
        "name": profile.name,
        "assistantPreferences": {
            "voicepack": profile.assistant_voicepack,
            "speakingSpeed": profile.speaking_speed,
            "personality": profile.assistant_personality,
            "model": "gemini-3.5-flash",
            "allowAlwaysListening": profile.allow_always_listening,
            "requireApprovalForFinancial": profile.require_approval_for_financial
        },
        "schedule": profile.schedule_json or [],
        "reminders": profile.reminders_json or []
    }

@profile_router.put("", response_model=schemas.UserProfileSchema)
def update_user_profile(payload: schemas.ProfileUpdate, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atomically modifies existing parameters inside Active Preference Stack."""
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User context mismatch.")

    if payload.name is not None:
        profile.name = payload.name
    if payload.assistantPreferences is not None:
        p_pref = payload.assistantPreferences
        profile.assistant_voicepack = p_pref.voicepack
        profile.speaking_speed = p_pref.speakingSpeed
        profile.assistant_personality = p_pref.personality
        profile.allow_always_listening = p_pref.allowAlwaysListening
        profile.require_approval_for_financial = p_pref.requireApprovalForFinancial
    if payload.schedule is not None:
        profile.schedule_json = [item.dict() for item in payload.schedule]
    if payload.reminders is not None:
        profile.reminders_json = [item.dict() for item in payload.reminders]

    db.commit()
    db.refresh(profile)

    # Invalidate configuration cache reference
    redis_client.delete(f"profile_cache:{user.id}")

    return {
        "name": profile.name,
        "assistantPreferences": {
            "voicepack": profile.assistant_voicepack,
            "speakingSpeed": profile.speaking_speed,
            "personality": profile.assistant_personality,
            "model": "gemini-3.5-flash",
            "allowAlwaysListening": profile.allow_always_listening,
            "requireApprovalForFinancial": profile.require_approval_for_financial
        },
        "schedule": profile.schedule_json or [],
        "reminders": profile.reminders_json or []
    }

app.include_router(profile_router)

# --- 3. Memory Router ---
memory_router = APIRouter(prefix="/api/memories", tags=["Memory Management"])

@memory_router.get("", response_model=List[schemas.MemorySchema])
def list_memories(user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieves all long-term, episodic, and semantic memory vectors linked to user space."""
    return db.query(models.MemoryItem).filter(models.MemoryItem.user_id == user.id).all()

@memory_router.post("", response_model=schemas.MemorySchema, status_code=201)
def create_memory(memory_in: schemas.MemoryCreate, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Commit an experiential fact, pref, pattern or rule directly into Cognitive Long-Term memory database."""
    new_mem = models.MemoryItem(
        user_id=user.id,
        content=memory_in.content,
        type=memory_in.type,
        category=memory_in.category,
        tags=memory_in.tags,
        confidence=memory_in.confidence
    )
    db.add(new_mem)

    # Log memory addition
    log = models.OSLog(
        user_id=user.id,
        level="success",
        source="Memory",
        message=f"Successfully indexed semantic fact memory block: '{memory_in.content[:40]}...'"
    )
    db.add(log)
    db.commit()
    db.refresh(new_mem)
    return new_mem

@memory_router.delete("/{memory_id}", status_code=200)
def delete_memory(memory_id: str, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Completely de-indexes and purges specific factual coordinates from Cognitive Vault."""
    mem = db.query(models.MemoryItem).filter(models.MemoryItem.id == memory_id, models.MemoryItem.user_id == user.id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Memory coordinate block not found inside Operator scope.")
    db.delete(mem)

    log = models.OSLog(
        user_id=user.id,
        level="warn",
        source="Memory",
        message=f"Purged long-term memory synapse reference '{memory_id}' permanently."
    )
    db.add(log)
    db.commit()
    return {"status": "purged", "id": memory_id}

app.include_router(memory_router)

# --- 4. Document Management & Vector RAG Router ---
document_router = APIRouter(prefix="/api/documents", tags=["RAG Document Indexer"])

# Pydantic search models
class SearchRequestPayload(BaseModel):
    query: str
    limit: Optional[int] = 4

from .rag import (
    default_ingestion_pipeline,
    default_search_coordinator,
    global_vector_store
)

@document_router.get("", response_model=List[schemas.DocumentSchema])
def list_documents(user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists current verified tokenized vector contexts."""
    docs = db.query(models.KnowledgeDoc).filter(models.KnowledgeDoc.user_id == user.id).all()
    out = []
    for d in docs:
        out.append({
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "mimeType": d.mime_type,
            "dateAdded": d.date_added,
            "size": d.size,
            "wordCount": d.word_count,
            "chunks": d.chunks_json or []
        })
    return out

@document_router.post("", response_model=schemas.DocumentSchema, status_code=201)
def compile_document(doc_in: schemas.DocumentCreate, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Accepts unstructured metadata parameters, executes contextual chunking rules and auto-calculates vectors."""
    # Ensure title has appropriate extension format
    title = doc_in.title
    if not (title.endswith(".md") or title.endswith(".txt") or title.endswith(".json")):
        title += ".md"
        
    try:
        # Ingest text document directly via RAG pipeline
        res = default_ingestion_pipeline.ingest_document(
            file_bytes=doc_in.content.encode("utf-8", errors="ignore"),
            filename=title,
            user_id=user.id,
            chunk_strategy="recursive"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_doc = models.KnowledgeDoc(
        id=res["document_id"],
        user_id=user.id,
        title=res["filename"],
        content=doc_in.content,
        mime_type=doc_in.mimeType,
        size=res["metadata"].get("size", f"{len(doc_in.content.encode('utf-8')) / 1024:.2f} KB"),
        word_count=res["word_count"],
        chunks_json=res["chunks"]
    )
    db.add(new_doc)

    log = models.OSLog(
        user_id=user.id,
        level="success",
        source="Document",
        message=f"Compiled Document vector indexes for '{title}'. Generated {res['chunks_count']} chunks."
    )
    db.add(log)
    db.commit()
    
    return {
        "id": new_doc.id,
        "title": new_doc.title,
        "content": new_doc.content,
        "mimeType": new_doc.mime_type,
        "dateAdded": new_doc.date_added,
        "size": new_doc.size,
        "wordCount": new_doc.word_count,
        "chunks": res["chunks"]
    }

@document_router.post("/upload", response_model=schemas.DocumentSchema, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    strategy: str = Form("recursive"),
    user: models.AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Parses, chunks, embeds, and indexes any uploaded doc / pdf / slide / spreadsheet format."""
    file_bytes = file.file.read()
    filename = file.filename if file.filename else "uploaded_file.txt"
    
    try:
        res = default_ingestion_pipeline.ingest_document(
            file_bytes=file_bytes,
            filename=filename,
            user_id=user.id,
            chunk_strategy=strategy
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    derived_summary = res["metadata"].get("summary_snippet", "Document format parsed and chunked successfully.")
    size_str = f"{len(file_bytes) / 1024:.2f} KB"
    
    new_doc = models.KnowledgeDoc(
        id=res["document_id"],
        user_id=user.id,
        title=res["filename"],
        content=derived_summary,
        mime_type=file.content_type or "application/octet-stream",
        size=size_str,
        word_count=res["word_count"],
        chunks_json=res["chunks"]
    )
    db.add(new_doc)

    log = models.OSLog(
        user_id=user.id,
        level="success",
        source="Document",
        message=f"Uploaded and indexed file '{filename}' under {strategy} strategy. Created {res['chunks_count']} chunks."
    )
    db.add(log)
    db.commit()
    
    return {
        "id": new_doc.id,
        "title": new_doc.title,
        "content": new_doc.content,
        "mimeType": new_doc.mime_type,
        "dateAdded": new_doc.date_added,
        "size": new_doc.size,
        "wordCount": new_doc.word_count,
        "chunks": res["chunks"]
    }

@document_router.post("/search")
def search_documents(payload: SearchRequestPayload, user: models.AuthUser = Depends(get_current_user)):
    """Runs high-utility hybrid search and retrieves cited passages."""
    results = default_search_coordinator.search(payload.query, user_id=user.id, limit=payload.limit)
    return results

@document_router.post("/reindex/{document_id}")
def reindex_document(document_id: str, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Recalculates chunks and vectors for existing files."""
    doc = db.query(models.KnowledgeDoc).filter(models.KnowledgeDoc.id == document_id, models.KnowledgeDoc.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    # Clear active vectors
    global_vector_store.delete_document(document_id)
    
    try:
        res = default_ingestion_pipeline.ingest_document(
            file_bytes=doc.content.encode("utf-8", errors="ignore"),
            filename=doc.title,
            user_id=user.id,
            chunk_strategy="recursive"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    doc.chunks_json = res["chunks"]
    doc.word_count = res["word_count"]
    db.commit()
    
    return {"status": "reindexed", "document_id": document_id, "chunks_count": len(res["chunks"])}

@document_router.get("/{document_id}/chunks")
def list_document_chunks(document_id: str, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """View actual processed semantic nodes for a document."""
    doc = db.query(models.KnowledgeDoc).filter(models.KnowledgeDoc.id == document_id, models.KnowledgeDoc.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"document_id": document_id, "chunks": doc.chunks_json or []}

@document_router.get("/{document_id}/metadata")
def view_document_metadata(document_id: str, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Views deep metadata properties for an indexed document."""
    doc = db.query(models.KnowledgeDoc).filter(models.KnowledgeDoc.id == document_id, models.KnowledgeDoc.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {
        "document_id": document_id,
        "title": doc.title,
        "mime_type": doc.mime_type,
        "size": doc.size,
        "word_count": doc.word_count,
        "date_added": doc.date_added,
        "estimated_reading_time_minutes": max(1, round(doc.word_count / 200)),
        "summary": doc.content[:350] + ("..." if len(doc.content) > 350 else "")
    }

@document_router.delete("/{document_id}", status_code=200)
def delete_document(document_id: str, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletes document and purges its vector mapping embeddings."""
    doc = db.query(models.KnowledgeDoc).filter(models.KnowledgeDoc.id == document_id, models.KnowledgeDoc.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    db.delete(doc)
    # Purge from RAG vector store
    global_vector_store.delete_document(document_id)

    log = models.OSLog(
        user_id=user.id,
        level="warn",
        source="Document",
        message=f"Purged document index reference '{document_id}' successfully."
    )
    db.add(log)
    db.commit()
    return {"status": "purged", "id": document_id}

app.include_router(document_router)

# --- 5. Automation Router ---
automation_router = APIRouter(prefix="/api/automation", tags=["Automation Center (MCP)"])

@automation_router.get("", response_model=List[schemas.TaskSchema])
def list_tasks(user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists current system automation tasks inside verification lock."""
    tasks = db.query(models.AutomationTask).filter(models.AutomationTask.user_id == user.id).all()
    out = []
    for t in tasks:
        out.append({
            "id": t.id,
            "name": t.name,
            "type": t.type,
            "description": t.description,
            "status": t.status,
            "timestamp": t.timestamp,
            "isIrreversible": t.is_reversible,
            "costEstimate": t.cost_estimate,
            "details": t.details_json or {}
        })
    return out

@automation_router.post("", response_model=schemas.TaskSchema, status_code=201)
def create_automation_task(task_in: schemas.TaskCreate, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Queues a programmatic automation task requiring security inspection."""
    new_task = models.AutomationTask(
        user_id=user.id,
        name=task_in.name,
        type=task_in.type,
        description=task_in.description,
        is_reversible=task_in.isIrreversible,
        cost_estimate=task_in.costEstimate,
        details_json=task_in.details,
        status="pending"
    )
    db.add(new_task)

    log = models.OSLog(
        user_id=user.id,
        level="warn" if task_in.isIrreversible else "info",
        source="Security",
        message=f"Automation trigger queued: '{task_in.name}' (Action Lock: Pending user signature)."
    )
    db.add(log)
    db.commit()
    db.refresh(new_task)

    return {
        "id": new_task.id,
        "name": new_task.name,
        "type": new_task.type,
        "description": new_task.description,
        "status": new_task.status,
        "timestamp": new_task.timestamp,
        "isIrreversible": new_task.is_reversible,
        "costEstimate": new_task.cost_estimate,
        "details": new_task.details_json or {}
    }

@automation_router.put("/{task_id}", response_model=schemas.TaskSchema)
def update_task_status(task_id: str, payload: schemas.TaskUpdate, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Modifies task signature (authorizes or cancels scheduled bookings)."""
    task = db.query(models.AutomationTask).filter(models.AutomationTask.id == task_id, models.AutomationTask.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task coordinate mismatch inside Operator context.")
    
    old_status = task.status
    task.status = payload.status
    
    # Cascade simulation logs
    if payload.status == "approved":
        log_msg = f"User signed task verification: Executing routine '{task.name}'."
        log_lvl = "success"
    elif payload.status == "rejected":
        log_msg = f"User declined task validation: PURGED '{task.name}'."
        log_lvl = "warn"
    else:
        log_msg = f"Task '{task.name}' status transited: {old_status} -> {payload.status}."
        log_lvl = "info"

    log = models.OSLog(user_id=user.id, level=log_lvl, source="Security", message=log_msg)
    db.add(log)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "name": task.name,
        "type": task.type,
        "description": task.description,
        "status": task.status,
        "timestamp": task.timestamp,
        "isIrreversible": task.is_reversible,
        "costEstimate": task.cost_estimate,
        "details": task.details_json or {}
    }

app.include_router(automation_router)

# --- 6. Unified OS Logging Router ---
logs_router = APIRouter(prefix="/api/logs", tags=["Unified OS System Logs"])

@logs_router.get("", response_model=List[schemas.OSLogSchema])
def retrieve_system_logs(user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns chronologically compiled operational audits matching operator space."""
    return db.query(models.OSLog).filter(models.OSLog.user_id == user.id).order_by(models.OSLog.timestamp.desc()).limit(100).all()

@logs_router.post("", response_model=schemas.OSLogSchema, status_code=201)
def append_system_log(log_in: schemas.OSLogSchema, user: models.AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Manually registers an operating system diagnostic message."""
    new_log = models.OSLog(
        user_id=user.id,
        level=log_in.level,
        source=log_in.source,
        message=log_in.message
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

app.include_router(logs_router)

# --- 7. Desktop Agent Runtime Router ---
from .routers import runtime
app.include_router(runtime.router)

# --- 8. Agent Execution Engine Router ---
from .routers import execution
app.include_router(execution.router)

# --- 9. Intelligent Interaction Layer Router ---
from .routers import intelligence
app.include_router(intelligence.router)



