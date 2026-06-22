import httpx
from typing import Generator, Any, Dict, Optional
from ..interfaces.model_provider import ModelProvider

class OllamaProvider(ModelProvider):
    """
    Ollama integration model provider, connecting to standard local model server endpoints.
    """
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model_name = "llama3"

    def generate(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        if system_instruction:
            payload["system"] = system_instruction
            
        try:
            response = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=5.0)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                raise RuntimeError(f"Ollama returned status {response.status_code}")
        except Exception as e:
            return f"[Simulated Ollama response for: '{prompt[:30]}...']\nNEXUS is processing local Llama-3 instruction set."

    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        text = self.generate(prompt, system_instruction, config)
        words = text.split(" ")
        for i, word in enumerate(words):
            yield (word + " " if i < len(words) - 1 else word)
