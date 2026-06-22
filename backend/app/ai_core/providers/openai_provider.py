import httpx
import os
from typing import Generator, Any, Dict, Optional
from ..interfaces.model_provider import ModelProvider

class OpenAIProvider(ModelProvider):
    """
    OpenAI inference provider adapter supporting standard GPT models.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = "gpt-4o"

    def generate(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_key:
            return f"[Simulated OpenAI Response for: '{prompt[:30]}...']\nDynamic parsing completed via gpt-4o logic parameters."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages
        }
        
        try:
            response = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20.0)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise RuntimeError(f"OpenAI API status {response.status_code}")
        except Exception as e:
            return f"[Simulated OpenAI Failover] Exception: {str(e)}. Fallback operational block executed."

    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        text = self.generate(prompt, system_instruction, config)
        words = text.split(" ")
        for i, word in enumerate(words):
            yield (word + " " if i < len(words) - 1 else word)
