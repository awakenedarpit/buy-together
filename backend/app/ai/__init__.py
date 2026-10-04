"""AI Providers and Extraction Subsystem Package."""

from backend.app.ai.base import BaseAIProvider
from backend.app.ai.mock_provider import MockAIProvider
from backend.app.ai.local_gemma_provider import LocalGemmaProvider
from backend.app.ai.hosted_gemma_provider import HostedGemmaProvider, HostedInferenceProvider
from backend.app.ai.factory import get_ai_provider, reset_ai_provider
from backend.app.ai.exceptions import (
    AIProviderError,
    AIProviderConfigurationError,
    AIProviderRuntimeError,
    AIExtractionValidationError,
)

__all__ = [
    "BaseAIProvider",
    "MockAIProvider",
    "LocalGemmaProvider",
    "HostedGemmaProvider",
    "HostedInferenceProvider",
    "get_ai_provider",
    "reset_ai_provider",
    "AIProviderError",
    "AIProviderConfigurationError",
    "AIProviderRuntimeError",
    "AIExtractionValidationError",
]
