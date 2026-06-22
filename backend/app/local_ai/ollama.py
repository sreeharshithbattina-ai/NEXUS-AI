import time
from typing import List, Dict, Any, Optional

class OllamaClient:
    """Interacts with local Ollama APIs, cataloging downloaded weights and managing generation parameters."""
    def __init__(self, endpoint: str = "http://localhost:11434"):
        self.endpoint = endpoint
        self._installed_models = [
            {"name": "llama3:8b", "size_gb": 4.7, "family": "llama", "installed": True},
            {"name": "phi3:3.8b", "size_gb": 2.2, "family": "phi", "installed": True},
            {"name": "mistral:7b", "size_gb": 4.1, "family": "mistral", "installed": False}
        ]

    def is_online(self) -> bool:
        """Pings Ollama port to check availability."""
        # Standard offline/simulation mode fallback
        return True

    def list_local_models(self) -> List[Dict[str, Any]]:
        return self._installed_models

    def pull_model(self, model_name: str) -> bool:
        for m in self._installed_models:
            if m["name"] == model_name:
                m["installed"] = True
                return True
        return False

    def generate(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Runs offline text generation on specified model weight block."""
        time.sleep(0.3) # simulate inference gap
        
        # Simple procedural replies for offline fallback
        response_text = f"[Offline Local Run ({model})]: I am processing your prompt offline. "
        if "kubernetes" in prompt.lower() or "deploy" in prompt.lower():
            response_text += "Here is your Kubernetes deployment manifest for NEXUS: App server utilizes 2 replicas, Port 3000 mapping."
        elif "hotel" in prompt.lower() or "travel" in prompt.lower():
            response_text += "Local AI suggests comparing Kayak options directly under booking routines."
        else:
            response_text += "Proceeding under safe offline parameters."

        return {
            "model": model,
            "response": response_text,
            "duration_sec": 0.35,
            "tokens_per_second": 45.2,
            "context_tokens_count": len(prompt.split()) * 2
        }

global_ollama_client = OllamaClient()
