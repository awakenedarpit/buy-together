"""Unit and integration tests for GeminiProvider and Zero-Trust Extraction Pipeline."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.app.ai.gemini_provider import GeminiProvider
from backend.app.ai.exceptions import AIProviderConfigurationError, AIProviderRuntimeError
from backend.app.services.extraction_service import ExtractionService
from backend.app.schemas.ai import ExtractedItem


@pytest.mark.asyncio
async def test_gemini_provider_missing_key():
    """Verify GeminiProvider raises AIProviderConfigurationError when no key is provided."""
    provider = GeminiProvider(api_key=None)
    with pytest.raises(AIProviderConfigurationError):
        await provider.extract_items("2 notebooks")


def test_gemini_provider_json_parser():
    """Verify _parse_json correctly handles raw JSON and markdown-wrapped JSON."""
    provider = GeminiProvider(api_key="test-key")

    raw_json = '{"items": [{"name": "notebook", "quantity": 2, "unit": "piece", "variant": null}]}'
    parsed = provider._parse_json(raw_json)
    assert len(parsed["items"]) == 1
    assert parsed["items"][0]["name"] == "notebook"

    # Markdown wrapped
    md_json = '```json\n{"items": [{"name": "pen", "quantity": 1, "unit": "piece", "variant": "blue"}]}\n```'
    parsed_md = provider._parse_json(md_json)
    assert len(parsed_md["items"]) == 1
    assert parsed_md["items"][0]["variant"] == "blue"


@pytest.mark.asyncio
async def test_gemini_provider_mocked_success():
    """Verify GeminiProvider parses responses from Google GenAI client accurately."""
    provider = GeminiProvider(api_key="test-key")

    fake_response = MagicMock()
    fake_response.text = json.dumps({
        "items": [
            {"name": "notebook", "quantity": 2, "unit": "piece", "variant": None},
            {"name": "pen", "quantity": 1, "unit": "piece", "variant": "blue"},
        ]
    })

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=fake_response)

    with patch.object(provider, "_get_client", return_value=mock_client):
        res = await provider.extract_items("bhai 2 notebook aur ek blue pen")
        assert len(res.items) == 2
        assert res.items[0].name == "notebook"
        assert res.items[0].quantity == 2
        assert res.items[1].name == "pen"
        assert res.items[1].variant == "blue"


@pytest.mark.asyncio
async def test_extraction_service_fallback_on_gemini_error():
    """Verify ExtractionService automatically falls back to heuristic extractor if Gemini fails."""
    provider = GeminiProvider(api_key="invalid-key")

    # Mock client failure
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=RuntimeError("Quota exceeded or network timeout"))

    with patch.object(provider, "_get_client", return_value=mock_client):
        service = ExtractionService(provider=provider)
        # Should gracefully fall back to MockAIProvider without throwing error to user
        items = await service.extract_and_validate("bhai 2 notebook aur ek blue pen")
        assert len(items) == 2
        assert items[0].name == "notebook"
        assert items[0].quantity == 2
        assert items[1].name == "pen"
        assert items[1].variant == "blue"


@pytest.mark.asyncio
async def test_all_five_user_scenarios_fallback():
    """Verify all 5 user test cases produce correct extracted requirements."""
    from backend.app.ai.mock_provider import MockAIProvider
    fallback_provider = MockAIProvider()
    service = ExtractionService(provider=fallback_provider)

    # 1. "bhai 2 notebook aur ek blue pen"
    items1 = await service.extract_and_validate("bhai 2 notebook aur ek blue pen")
    assert any(i.name == "notebook" and i.quantity == 2 for i in items1)
    assert any(i.name == "pen" and i.quantity == 1 and i.variant == "blue" for i in items1)

    # 2. "5 A4 notebooks and 3 black pens"
    items2 = await service.extract_and_validate("5 A4 notebooks and 3 black pens")
    assert any(i.name == "notebook" and i.quantity == 5 and i.variant == "a4" for i in items2)
    assert any(i.name == "pen" and i.quantity == 3 and i.variant == "black" for i in items2)

    # 3. "mujhe 2 red files chahiye"
    items3 = await service.extract_and_validate("mujhe 2 red files chahiye")
    assert any(i.name == "file" and i.quantity == 2 and i.variant == "red" for i in items3)

    # 4. "10 pencils"
    items4 = await service.extract_and_validate("10 pencils")
    assert any(i.name == "pencil" and i.quantity == 10 for i in items4)

    # 5. "ek blue pen aur do black pen"
    items5 = await service.extract_and_validate("ek blue pen aur do black pen")
    assert any(i.name == "pen" and i.quantity == 1 and i.variant == "blue" for i in items5)
    assert any(i.name == "pen" and i.quantity == 2 and i.variant == "black" for i in items5)
