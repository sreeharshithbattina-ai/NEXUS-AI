import httpx
import os
from typing import Generator, Any, Dict, Optional
from ..interfaces.model_provider import ModelProvider

class AnthropicProvider(ModelProvider):
    """
    Anthropic inference provider adapter supporting Claude suite.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = "claude-3-5-sonnet"

    def generate(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_key:
            return f"[Simulated Anthropic Claude response for: '{prompt[:30]}...']\nNEXUS is processing layout parameters using Claude-3.5-Sonnet adapter."

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_instruction:
            payload["system"] = system_instruction
            
        try:
            response = httpx.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=20.0)
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                raise RuntimeError(f"Anthropic returned status {response.status_code}")
        except Exception as e:
            return f"[Simulated Anthropic Failover] Exception: {str(e)}. Fallback core operational."

    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        text = self.generate(prompt, system_instruction, config)
        words = text.split(" ")
        for i, word in enumerate(words):
            yield (word + " " if i < len(words) - 1 else word)
