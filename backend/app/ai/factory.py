"""Provider factory for instantiating the active AI provider based on configuration."""

from typing import Optional
from backend.app.ai.base import BaseAIProvider
from backend.app.ai.mock_provider import MockAIProvider
from backend.app.ai.local_gemma_provider import LocalGemmaProvider
from backend.app.ai.hosted_gemma_provider import HostedGemmaProvider
from backend.app.ai.gemini_provider import GeminiProvider
from backend.app.ai.exceptions import AIProviderConfigurationError
from backend.app.core.config import settings
from backend.app.core.logging import logger

_provider_instance: Optional[BaseAIProvider] = None


def get_ai_provider(provider_type: Optional[str] = None) -> BaseAIProvider:
    """Factory to retrieve or create the designated AI Provider.
    
    Args:
        provider_type: Optional override ('gemini', 'mock', 'local_gemma', 'hosted').
                       If None, defaults to 'gemini' if GEMINI_API_KEY is configured,
                       otherwise reads settings.AI_PROVIDER.
                       
    Returns:
        Instance conforming to BaseAIProvider.
        
    Raises:
        AIProviderConfigurationError: If an unknown provider type is requested.
    """
    global _provider_instance
    if provider_type:
        target_type = provider_type.lower()
    elif settings.GEMINI_API_KEY:
        target_type = "gemini"
    else:
        target_type = settings.AI_PROVIDER.lower()

    # If instance already cached with matching provider_name, return it
    if _provider_instance is not None and _provider_instance.provider_name in (target_type, target_type.replace("_gemma", "")):
        return _provider_instance

    logger.info(f"[AI Factory] Initializing AI Provider: '{target_type}'")

    if target_type == "gemini":
        _provider_instance = GeminiProvider()
    elif target_type == "mock":
        _provider_instance = MockAIProvider()
    elif target_type == "local_gemma":
        _provider_instance = LocalGemmaProvider()
    elif target_type in ("hosted", "hosted_gemma"):
        _provider_instance = HostedGemmaProvider()
    else:
        raise AIProviderConfigurationError(
            f"Unsupported AI_PROVIDER '{target_type}'. Allowed values: 'gemini', 'mock', 'local_gemma', 'hosted'."
        )

    return _provider_instance


def reset_ai_provider() -> None:
    """Reset the cached provider instance (useful for test parameterization)."""
    global _provider_instance
    _provider_instance = None
