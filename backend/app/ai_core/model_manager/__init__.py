from typing import Dict, Any, Generator, Optional, List
from ..interfaces.model_provider import ModelProvider
from ..providers.gemini_provider import GeminiProvider
from ..providers.openai_provider import OpenAIProvider
from ..providers.anthropic_provider import AnthropicProvider
from ..providers.ollama_provider import OllamaProvider

class ModelManager:
    """
    Central Manager registry coordinating selectable LLM providers and automated fallback chains.
    """
    def __init__(self, preferred_provider: str = "gemini"):
        self.preferred_provider = preferred_provider.lower()
        self._providers: Dict[str, ModelProvider] = {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "ollama": OllamaProvider()
        }
        # Fallback queue order
        self.fallback_chain: List[str] = ["gemini", "openai", "anthropic", "ollama"]

    def set_preferred_provider(self, provider_name: str) -> None:
        """Dynamically switch active provider."""
        normalized = provider_name.lower()
        if normalized in self._providers:
            self.preferred_provider = normalized

    def get_provider_names(self) -> List[str]:
        return list(self._providers.keys())

    def generate(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates text. Tries primary configured provider; fallback to subsequent providers in chain
        if errors occur to ensure high availability.
        """
        tested_chain = [self.preferred_provider] + [p for p in self.fallback_chain if p != self.preferred_provider]
        
        for provider_name in tested_chain:
            provider = self._providers[provider_name]
            try:
                # If is mock but is valid fallback, execute
                res = provider.generate(prompt, system_instruction, config)
                if res and not "Exception: " in res:
                    return res
            except Exception:
                continue
                
        # Hard failover to first available
        return self._providers["gemini"].generate(prompt, system_instruction, config)

    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """Streams text. Leverages generate fallback if first step fails."""
        try:
            prov = self._providers[self.preferred_provider]
            for chunk in prov.generate_stream(prompt, system_instruction, config):
                yield chunk
        except Exception:
            # Fallback to absolute standard gemini mock stream
            for chunk in self._providers["gemini"].generate_stream(prompt, system_instruction, config):
                yield chunk
