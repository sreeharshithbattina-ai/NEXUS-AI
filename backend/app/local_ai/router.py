import socket
from typing import Dict, Any, Optional
from .ollama import global_ollama_client

class HybridLLMRouter:
    """Interprets prompt risks (sensitive terms) and network metrics to choose between cloud Gemini or local llama3/phi3."""
    def __init__(self):
        self.offline_mode_active = False
        self.preferred_local_model = "llama3:8b"

    def is_internet_available(self) -> bool:
        """Heuristically tests host dns lookups."""
        try:
            # Pings safe public servers on port 53
            socket.setdefaulttimeout(1.0)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except Exception:
            return False

    def determine_route(self, prompt: str, secure_override: bool = False) -> Dict[str, Any]:
        """Runs policy checks. Choice rules: 1. Offline force, 2. No internet, 3. Privacy sensitive topics -> Local."""
        prompt_lower = prompt.lower()
        private_keywords = ["key", "password", "secret", "cvv", "credit", "passport", "tax", "payroll"]
        is_sensitive = any(term in prompt_lower for term in private_keywords) or secure_override
        
        internet_up = self.is_internet_available()
        
        if self.offline_mode_active or not internet_up or is_sensitive:
            # Route to local model
            reason = "Offline policy enforced" if self.offline_mode_active else ("No Internet Connection" if not internet_up else "Confidentiality compliance trigger")
            return {
                "route": "local",
                "model": self.preferred_local_model,
                "reason": reason,
                "confidence": 0.95
            }
            
        return {
            "route": "cloud",
            "model": "gemini-2.5-flash",
            "reason": "Stable web connection and clean context classification",
            "confidence": 1.0
        }

global_hybrid_llm_router = HybridLLMRouter()
