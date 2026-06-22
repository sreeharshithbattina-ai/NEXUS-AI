from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict

# --- Authentication & User ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_email: str

# --- Settings & Profile ---
class AssistantPreferencesSchema(BaseModel):
    voicepack: str = "Zephyr"
    speakingSpeed: float = 1.0
    personality: str = "Balanced"
    model: str = "gemini-3.5-flash"
    allowAlwaysListening: bool = False
    requireApprovalForFinancial: bool = True

class ScheduleItemSchema(BaseModel):
    id: str
    title: str
    time: str
    category: str
    done: bool

class ReminderItemSchema(BaseModel):
    id: str
    text: str
    due: str
    priority: str

class UserProfileSchema(BaseModel):
    name: str = "Apex Operator"
    assistantPreferences: AssistantPreferencesSchema
    schedule: List[ScheduleItemSchema] = []
    reminders: List[ReminderItemSchema] = []

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    assistantPreferences: Optional[AssistantPreferencesSchema] = None
    schedule: Optional[List[ScheduleItemSchema]] = None
    reminders: Optional[List[ReminderItemSchema]] = None

# --- Memories ---
class MemoryCreate(BaseModel):
    content: str
    type: str = "semantic"
    category: str = "Preference"
    tags: List[str] = []
    confidence: float = 0.9

class MemorySchema(BaseModel):
    id: str
    content: str
    type: str
    category: str
    timestamp: str
    tags: List[str]
    confidence: float

    class Config:
        from_attributes = True

# --- Documents ---
class DocumentChunkSchema(BaseModel):
    id: str
    text: str
    vectorId: List[float]
    confidence: float

class DocumentCreate(BaseModel):
    title: str
    content: str
    mimeType: str = "text/markdown"

class DocumentSchema(BaseModel):
    id: str
    title: str
    content: str
    mimeType: str
    dateAdded: str
    size: str
    wordCount: int
    chunks: List[DocumentChunkSchema]

    class Config:
        from_attributes = True

# --- Automation ---
class TaskCreate(BaseModel):
    name: str
    type: str
    description: str
    isIrreversible: bool = False
    costEstimate: Optional[str] = None
    details: Dict[str, str] = {}

class TaskUpdate(BaseModel):
    status: str # pending, approved, executing, completed, rejected

class TaskSchema(BaseModel):
    id: str
    name: str
    type: str
    description: str
    status: str
    timestamp: str
    isIrreversible: bool
    costEstimate: Optional[str] = None
    details: Dict[str, str]

    class Config:
        from_attributes = True

# --- Chat & Conversations ---
class ChatStepSchema(BaseModel):
    agent: str
    action: str
    duration: str

class ChatRequest(BaseModel):
    message: str
    agent: str = "CEO"
    conversationId: str = "default"

class ChatResponse(BaseModel):
    content: str
    activeAgent: str
    steps: List[ChatStepSchema]

class MessageSchema(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str
    activeAgent: Optional[str] = "CEO"
    steps: Optional[List[ChatStepSchema]] = []

    class Config:
        from_attributes = True

# --- Unified OS Log ---
class OSLogSchema(BaseModel):
    id: str
    timestamp: str
    level: str
    source: str
    message: str

    class Config:
        from_attributes = True
