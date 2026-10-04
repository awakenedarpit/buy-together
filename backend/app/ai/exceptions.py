"""Custom exceptions for the AI extraction subsystem."""


class AIProviderError(Exception):
    """Base exception for all AI provider failures."""
    pass


class AIProviderConfigurationError(AIProviderError):
    """Raised when an AI provider is configured improperly or missing prerequisites."""
    pass


class AIProviderRuntimeError(AIProviderError):
    """Raised when an AI model fails during runtime execution or inference."""
    pass


class AIExtractionValidationError(AIProviderError):
    """Raised when the AI output cannot be parsed or validated into expected schemas."""
    pass
