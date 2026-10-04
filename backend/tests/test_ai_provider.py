"""Unit tests for AI Provider abstraction, MockAIProvider, LocalGemmaProvider, and ExtractionService."""

import pytest
from backend.app.ai.base import BaseAIProvider
from backend.app.ai.mock_provider import MockAIProvider
from backend.app.ai.local_gemma_provider import LocalGemmaProvider
from backend.app.ai.hosted_gemma_provider import HostedGemmaProvider
from backend.app.ai.factory import get_ai_provider, reset_ai_provider
from backend.app.ai.exceptions import (
    AIProviderRuntimeError,
    AIProviderConfigurationError,
    AIExtractionValidationError,
)
from backend.app.services.extraction_service import ExtractionService
from backend.app.schemas.ai import ExtractedItem, ExtractionResult


@pytest.fixture(autouse=True)
def clean_ai_factory():
    """Ensure AI factory cached provider is reset between test cases."""
    reset_ai_provider()
    yield
    reset_ai_provider()


@pytest.mark.asyncio
async def test_mock_provider_interface():
    """Verify MockAIProvider adheres to BaseAIProvider contract."""
    provider = MockAIProvider()
    assert isinstance(provider, BaseAIProvider)
    assert provider.provider_name == "mock"


@pytest.mark.asyncio
async def test_mock_provider_hinglish_extraction():
    """Verify MockAIProvider extracts items from Hinglish sentence."""
    provider = MockAIProvider()
    result = await provider.extract_items("bhai 2 notebook aur ek blue pen")

    assert isinstance(result, ExtractionResult)
    assert len(result.items) == 2

    notebook = next(i for i in result.items if i.name == "notebook")
    assert notebook.quantity == 2
    assert notebook.unit == "piece"
    assert notebook.variant is None

    pen = next(i for i in result.items if i.name == "pen")
    assert pen.quantity == 1
    assert pen.variant == "blue"
    assert pen.unit == "piece"


@pytest.mark.asyncio
async def test_mock_provider_english_groceries():
    """Verify MockAIProvider extracts items from complex English grocery request."""
    provider = MockAIProvider()
    result = await provider.extract_items("Please add 3 packets of milk, 1kg sugar and 2 black gel pens")

    assert len(result.items) == 3
    names = {it.name for it in result.items}
    assert "milk" in names
    assert "sugar" in names
    assert "gel pen" in names


@pytest.mark.asyncio
async def test_mock_provider_conversational_greeting():
    """Verify conversational messages without purchase intent return empty items."""
    provider = MockAIProvider()
    result = await provider.extract_items("hello sab log kaise ho?")
    assert len(result.items) == 0


@pytest.mark.asyncio
async def test_mock_provider_simulated_error():
    """Verify MockAIProvider raises AIProviderRuntimeError when simulated."""
    provider = MockAIProvider(simulate_error=True)
    with pytest.raises(AIProviderRuntimeError, match="Simulated AI inference error"):
        await provider.extract_items("2 notebooks")


@pytest.mark.asyncio
async def test_extraction_service_clean_flow():
    """Verify ExtractionService orchestrates extraction and normalizes units."""
    service = ExtractionService(provider=MockAIProvider())
    items = await service.extract_and_validate("bhai 2 notebook aur ek blue pen")

    assert len(items) == 2
    assert all(isinstance(i, ExtractedItem) for i in items)
    assert items[0].name == "notebook"
    assert items[0].quantity == 2


@pytest.mark.asyncio
async def test_extraction_service_malformed_items_handling():
    """Verify ExtractionService safely drops malformed items without crashing."""
    custom_raw = '{"items": [{"name": "valid item", "quantity": 3, "unit": "piece"}, {"name": "", "quantity": 2, "unit": "piece"}, {"name": "bad qty", "quantity": -5, "unit": "kg"}]}'
    provider = MockAIProvider(custom_raw_response=custom_raw)
    service = ExtractionService(provider=provider)

    items = await service.extract_and_validate("some test text")
    assert len(items) == 1
    assert items[0].name == "valid item"
    assert items[0].quantity == 3


@pytest.mark.asyncio
async def test_extraction_service_unit_normalization():
    """Verify units like 'pkts', 'kgs', 'pcs' are canonicalized to standard terms."""
    custom_raw = '{"items": [{"name": "tea", "quantity": 2, "unit": "pkts"}, {"name": "rice", "quantity": 5, "unit": "kgs"}, {"name": "pen", "quantity": 10, "unit": "pcs"}]}'
    provider = MockAIProvider(custom_raw_response=custom_raw)
    service = ExtractionService(provider=provider)

    items = await service.extract_and_validate("some order")
    assert len(items) == 3
    assert items[0].unit == "packet"
    assert items[1].unit == "kg"
    assert items[2].unit == "piece"


@pytest.mark.asyncio
async def test_extraction_service_empty_text():
    """Verify empty text returns empty items immediately without invoking provider."""
    service = ExtractionService(provider=MockAIProvider(simulate_error=True))
    items = await service.extract_and_validate("   ")
    assert items == []


def test_ai_factory_selection():
    """Verify get_ai_provider selects correct provider implementation."""
    mock = get_ai_provider("mock")
    assert isinstance(mock, MockAIProvider)

    reset_ai_provider()
    local = get_ai_provider("local_gemma")
    assert isinstance(local, LocalGemmaProvider)

    reset_ai_provider()
    hosted = get_ai_provider("hosted")
    assert isinstance(hosted, HostedGemmaProvider)

    reset_ai_provider()
    with pytest.raises(AIProviderConfigurationError):
        get_ai_provider("invalid_provider")


@pytest.mark.asyncio
async def test_local_gemma_graceful_missing_weights():
    """Verify LocalGemmaProvider raises a clean AIProviderRuntimeError/ConfigurationError when model path is unavailable."""
    provider = LocalGemmaProvider(model_path="/nonexistent/path/gemma-weights")
    assert not provider.is_loaded

    with pytest.raises((AIProviderRuntimeError, AIProviderConfigurationError)):
        await provider.extract_items("test message")


@pytest.mark.asyncio
async def test_hosted_gemma_clean_error():
    """Verify HostedGemmaProvider raises AIProviderConfigurationError when unconfigured."""
    provider = HostedGemmaProvider()
    with pytest.raises(AIProviderConfigurationError, match="Hosted Gemma inference endpoint is not configured"):
        await provider.extract_items("test message")
