import datetime
from typing import Dict, Any, List, Optional

class AgentMessage:
    """
    Standard structured communication message parsed during inter-agent collaboration loops.
    """
    def __init__(self, 
                 sender: str, 
                 receiver: str, 
                 task: str, 
                 context: Dict[str, Any], 
                 confidence: float = 1.0, 
                 dependencies: Optional[List[str]] = None,
                 payload: Optional[Dict[str, Any]] = None):
        self.sender = sender
        self.receiver = receiver
        self.timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        self.task = task
        self.context = context
        self.confidence = confidence
        self.dependencies = dependencies or []
        self.payload = payload or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "timestamp": self.timestamp,
            "task": self.task,
            "context": self.context,
            "confidence": self.confidence,
            "dependencies": self.dependencies,
            "payload": self.payload
        }
