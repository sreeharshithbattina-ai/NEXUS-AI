from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
import uuid
import datetime
from .database import Base

class AuthUser(Base):
    __tablename__ = "auth_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    memories = relationship("MemoryItem", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("KnowledgeDoc", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("AutomationTask", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("OSLog", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("auth_users.id"), unique=True, nullable=False)
    name = Column(String(100), default="Apex Operator")
    assistant_personality = Column(String(50), default="Balanced")
    assistant_voicepack = Column(String(50), default="Zephyr")
    speaking_speed = Column(Float, default=1.0)
    allow_always_listening = Column(Boolean, default=False)
    require_approval_for_financial = Column(Boolean, default=True)
    schedule_json = Column(JSON, default=lambda: [])
    reminders_json = Column(JSON, default=lambda: [])

    # Relationships
    user = relationship("AuthUser", back_populates="profile")

class MemoryItem(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("auth_users.id"), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="semantic") # short, episodic, semantic
    category = Column(String(50), default="Preference")
    timestamp = Column(String(50), default=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    tags = Column(JSON, default=lambda: [])
    confidence = Column(Float, default=0.9)

    user = relationship("AuthUser", back_populates="memories")

class KnowledgeDoc(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("auth_users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    mime_type = Column(String(100), default="text/markdown")
    date_added = Column(String(50), default=lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    size = Column(String(50), default="0.0 KB")
    word_count = Column(Integer, default=0)
    chunks_json = Column(JSON, default=lambda: []) # [{id, text, vectorId, confidence}]

    user = relationship("AuthUser", back_populates="documents")

class AutomationTask(Base):
    __tablename__ = "automation_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("auth_users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False) # travel, git, email, purchase etc
    description = Column(Text, nullable=False)
    status = Column(String(50), default="pending") # pending, approved, executing, completed, rejected
    timestamp = Column(String(50), default=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    is_reversible = Column(Boolean, default=False)
    cost_estimate = Column(String(50), nullable=True)
    details_json = Column(JSON, default=lambda: {})

    user = relationship("AuthUser", back_populates="tasks")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(100), default="default")
    user_id = Column(String(36), ForeignKey("auth_users.id"), nullable=False)
    role = Column(String(50), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(String(50), default=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    active_agent = Column(String(50), default="CEO")
    steps_json = Column(JSON, default=lambda: [])

    user = relationship("AuthUser", back_populates="messages")

class OSLog(Base):
    __tablename__ = "os_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("auth_users.id"), nullable=False)
    timestamp = Column(String(50), default=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    level = Column(String(50), default="info") # info, warn, error, success, agent
    source = Column(String(100), default="Kernel")
    message = Column(Text, nullable=False)

    user = relationship("AuthUser", back_populates="logs")
