"""Base AI Provider Interface

Defines the pluggable contract that all AI model providers (Mock, Local Gemma, Hosted) must implement.
"""

from abc import ABC, abstractmethod
from backend.app.schemas.ai import ExtractionResult


class BaseAIProvider(ABC):
    """Abstract base class for all linguistic extraction providers.
    
    Provides strict decoupling: callers interact solely with this interface
    without depending on model-specific runtimes, tokenizers, or external API SDKs.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique identifier string for this provider."""
        pass

    @abstractmethod
    async def extract_items(self, text: str) -> ExtractionResult:
        """Extract structured purchase items from an input text message.
        
        Args:
            text: Raw input message from a user (English, Hindi, Hinglish, etc.)
            
        Returns:
            ExtractionResult containing structured ExtractedItem objects and raw text.
            
        Raises:
            AIProviderRuntimeError: If model inference fails.
            AIExtractionValidationError: If output parsing fails irreparably.
        """
        pass
