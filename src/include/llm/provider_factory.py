import os
from typing import Optional, List
from enum import Enum
import logging
from .base_provider import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


class LLMProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class LLMProviderFactory:
    @staticmethod
    def create_provider(
        provider_type: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseLLMProvider:
        provider_type = provider_type.lower()
        
        if provider_type == LLMProviderType.OPENAI:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return OpenAIProvider(api_key=api_key, model=model, **kwargs)
        
        elif provider_type == LLMProviderType.ANTHROPIC:
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            return AnthropicProvider(api_key=api_key, model=model, **kwargs)
        
        elif provider_type == LLMProviderType.GEMINI:
            api_key = api_key or os.getenv("GEMINI_API_KEY")
            model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            return GeminiProvider(api_key=api_key, model=model, **kwargs)
        
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
    
    @staticmethod
    def create_with_fallback(
        primary_provider: str,
        fallback_order: Optional[List[str]] = None,
        **kwargs
    ) -> List[BaseLLMProvider]:
        if fallback_order is None:
            fallback_order = os.getenv("LLM_FALLBACK_ORDER", "gemini,openai,anthropic").split(",")
        
        providers = []
        tried_providers = set()
        
        all_providers = [primary_provider] + [p.strip() for p in fallback_order if p.strip() != primary_provider]
        
        for provider_type in all_providers:
            if provider_type in tried_providers:
                continue
            
            try:
                provider = LLMProviderFactory.create_provider(provider_type, **kwargs)
                providers.append(provider)
                tried_providers.add(provider_type)
                logger.info(f"Successfully initialized {provider_type} provider")
            except Exception as e:
                logger.warning(f"Failed to initialize {provider_type} provider: {e}")
                continue
        
        if not providers:
            raise RuntimeError("No LLM providers could be initialized")
        
        return providers
    
    @staticmethod
    def get_primary_provider(**kwargs) -> BaseLLMProvider:
        primary = os.getenv("LLM_PRIMARY_PROVIDER", "openai")
        enable_fallback = os.getenv("LLM_ENABLE_FALLBACK", "true").lower() == "true"
        
        if enable_fallback:
            providers = LLMProviderFactory.create_with_fallback(primary, **kwargs)
            return providers[0]
        else:
            return LLMProviderFactory.create_provider(primary, **kwargs)
