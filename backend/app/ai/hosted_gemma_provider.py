"""Hosted Gemma Provider stub for remote inference (HuggingFace / OpenAI-compatible endpoint)."""

from typing import Optional
from backend.app.ai.base import BaseAIProvider
from backend.app.ai.exceptions import AIProviderConfigurationError
from backend.app.schemas.ai import ExtractionResult
from backend.app.core.config import settings
from backend.app.core.logging import logger


class HostedGemmaProvider(BaseAIProvider):
    """Provider stub for remote/cloud hosted Gemma inference.
    
    Acts as an extension point for external API endpoints (e.g. HuggingFace Serverless Inference,
    vLLM, or dedicated inference instances).
    """

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url
        self.api_key = api_key

    @property
    def provider_name(self) -> str:
        return "hosted_gemma"

    async def extract_items(self, text: str) -> ExtractionResult:
        logger.warning("[HostedGemmaProvider] Hosted inference provider invoked but not configured.")
        raise AIProviderConfigurationError(
            "Hosted Gemma inference endpoint is not configured in this environment. "
            "Set AI_PROVIDER=mock for local deterministic testing or configure remote API credentials."
        )
