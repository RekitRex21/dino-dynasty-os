"""LLM Provider - Multi-provider fallback system for Dino Dynasty OS."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    finish_reason: str = "stop"


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    name: str = "base"
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize provider with config.
        
        Args:
            config: Provider configuration dict self.config = config.
        """
       
        self.model = config.get('model', 'default')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 4096)
        self.timeout = config.get('timeout', 60)
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object.
        """
        raise NotImplementedError
    
    def _prepare_headers(self, api_key: str) -> Dict[str, str]:
        """Prepare request headers.
        
        Args:
            api_key: API key
            
        Returns:
            Headers dict.
        """
        return {}


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider (unified API for multiple models)."""
    
    name = "openrouter"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://openrouter.ai/api/v1')
        self.api_key = config.get('api_key', os.environ.get('OPENROUTER_API_KEY', ''))
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate via OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://dinodynasty.os",
            "X-Title": "Dino Dynasty OS"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get('temperature', self.temperature),
            "max_tokens": kwargs.get('max_tokens', self.max_tokens)
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            return LLMResponse(
                content=data['choices'][0]['message']['content'],
                model=data.get('model', self.model),
                provider=self.name,
                tokens_used=data.get('usage', {}).get('total_tokens', 0)
            )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""
    
    name = "anthropic"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://api.anthropic.com')
        self.api_key = config.get('api_key', os.environ.get('ANTHROPIC_API_KEY', ''))
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate via Anthropic."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": kwargs.get('max_tokens', self.max_tokens),
            "temperature": kwargs.get('temperature', self.temperature),
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            return LLMResponse(
                content=data['content'][0]['text'],
                model=data.get('model', self.model),
                provider=self.name,
                tokens_used=data.get('usage', {}).get('input_tokens', 0) + data.get('usage', {}).get('output_tokens', 0)
            )


class MiniMaxProvider(BaseLLMProvider):
    """MiniMax provider."""
    
    name = "minimax"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', os.environ.get('MINIMAX_API_KEY', ''))
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate via MiniMax."""
        # MiniMax uses group_id + user_id for authentication
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # This is a simplified version - MiniMax has specific API format
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get('temperature', self.temperature),
            "max_tokens": kwargs.get('max_tokens', self.max_tokens)
        }
        
        # MiniMax endpoint format varies - simplified here
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Placeholder - actual implementation depends on MiniMax API
            resp = await client.post(
                "https://api.minimax.chat/v1/text/chatcompletion_v2",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            return LLMResponse(
                content=data['choices'][0]['message']['content'],
                model=data.get('model', self.model),
                provider=self.name
            )


class OllamaProvider(BaseLLMProvider):
    """Ollama local provider."""
    
    name = "ollama"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.api_key = "not-needed"
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate via Ollama."""
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": kwargs.get('temperature', self.temperature),
            "options": {
                "num_predict": kwargs.get('max_tokens', self.max_tokens)
            },
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            return LLMResponse(
                content=data.get('response', ''),
                model=self.model,
                provider=self.name
            )


class VLLMProvider(BaseLLMProvider):
    """vLLM local provider (OpenAI-compatible)."""
    
    name = "vl"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:8000/v1')
        self.api_key = config.get('api_key', 'not-needed')
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate via vLLM (OpenAI-compatible API)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get('temperature', self.temperature),
            "max_tokens": kwargs.get('max_tokens', self.max_tokens)
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            return LLMResponse(
                content=data['choices'][0]['message']['content'],
                model=data.get('model', self.model),
                provider=self.name,
                tokens_used=data.get('usage', {}).get('total_tokens', 0)
            )


# Provider registry
PROVIDER_CLASSES = {
    'openrouter': OpenRouterProvider,
    'anthropic': AnthropicProvider,
    'minimax': MiniMaxProvider,
    'ollama': OllamaProvider,
    'vl': VLLMProvider,
}


class LLMManager:
    """Multi-provider LLM manager with fallback."""
    
    def __init__(self, provider_configs: List[Dict[str, Any]], default_settings: Optional[Dict[str, Any]] = None):
        """Initialize LLM manager.
        
        Args:
            provider_configs: List of provider configurations (in priority order)
            default_settings: Default settings for all providers
        """
        self.providers: List[BaseLLMProvider] = []
        self.default_settings = default_settings or {}
        
        for config in provider_configs:
            if not config.get('enabled', True):
                continue
            
            provider_type = config.get('provider', '').lower()
            if provider_type in PROVIDER_CLASSES:
                # Merge with default settings
                merged_config = {**self.default_settings, **config}
                provider = PROVIDER_CLASSES[provider_type](merged_config)
                self.providers.append(provider)
    
    async def generate(self, prompt: str, **kwargs) -> Optional[LLMResponse]:
        """Generate with fallback - try each provider until success.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse or None if all providers fail.
        """
        last_error = None
        
        for provider in self.providers:
            try:
                response = await provider.generate(prompt, **kwargs)
                return response
            except Exception as e:
                last_error = e
                print(f"Provider {provider.name} failed: {e}")
                continue
        
        if last_error:
            raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")
        return None
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Get a specific provider by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None.
        """
        for p in self.providers:
            if p.name == name:
                return p
        return None
    
    @property
    def available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [p.name for p in self.providers]
