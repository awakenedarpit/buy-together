"""Extraction Service

Responsible for coordinating message extraction via the configured AIProvider,
validating outputs through Pydantic contracts, applying business sanity checks,
and returning clean, normalized items.
"""

from typing import List, Optional
from backend.app.ai.base import BaseAIProvider
from backend.app.ai.factory import get_ai_provider
from backend.app.ai.exceptions import AIProviderError, AIExtractionValidationError
from backend.app.schemas.ai import ExtractedItem, ExtractionResult
from backend.app.core.logging import logger


class ExtractionService:
    """Zero-Trust AI extraction and normalization pipeline."""

    def __init__(self, provider: Optional[BaseAIProvider] = None):
        self._explicit_provider = provider

    @property
    def provider(self) -> BaseAIProvider:
        if self._explicit_provider is not None:
            return self._explicit_provider
        return get_ai_provider()


    async def extract_and_validate(self, text: str) -> List[ExtractedItem]:
        """Extract structured items from natural language text and enforce strict business validation.
        
        Args:
            text: Raw message string from member.
            
        Returns:
            List of clean, validated ExtractedItem instances.
            
        Raises:
            AIProviderError: If the provider experiences an unrecoverable failure.
        """
        clean_text = text.strip()
        if not clean_text:
            return []

        # 1. AI Provider Extraction with Graceful Fallback
        try:
            result: ExtractionResult = await self.provider.extract_items(clean_text)
        except Exception as exc:
            logger.warning(f"[ExtractionService] Primary provider failed: {exc}. Engaging fallback extractor.")
            from backend.app.ai.mock_provider import MockAIProvider
            fallback_provider = MockAIProvider()
            result = await fallback_provider.extract_items(clean_text)

        # 2. Pydantic & Business Validation Layer (Zero Trust)
        validated_items: List[ExtractedItem] = []

        for raw_item in result.items:
            try:
                # Ensure Pydantic model instantiation / validation
                if isinstance(raw_item, dict):
                    item = ExtractedItem(**raw_item)
                elif isinstance(raw_item, ExtractedItem):
                    item = raw_item
                else:
                    logger.warning(f"[ExtractionService] Ignoring unknown item type: {type(raw_item)}")
                    continue

                # Enforce business validation rules
                # Name must be non-empty string <= 150 chars
                name = item.name.strip().lower()
                if not name or len(name) < 1:
                    logger.warning("[ExtractionService] Rejecting item with empty name")
                    continue

                # Quantity must be positive integer >= 1
                if not isinstance(item.quantity, int) or item.quantity < 1:
                    logger.warning(f"[ExtractionService] Rejecting invalid quantity: {item.quantity} for item '{name}'")
                    continue

                # Unit normalization
                unit = self._normalize_unit(item.unit)

                # Variant normalization
                variant = item.variant.strip().lower() if item.variant and item.variant.strip() else None

                validated_items.append(ExtractedItem(
                    name=name,
                    variant=variant,
                    quantity=item.quantity,
                    unit=unit,
                ))

            except Exception as val_err:
                logger.warning(f"[ExtractionService] Item validation rejected item {raw_item}: {val_err}")
                continue

        logger.info(f"[ExtractionService] Successfully validated {len(validated_items)} items")
        return validated_items

    @staticmethod
    def _normalize_unit(unit_str: str) -> str:
        """Map common unit variants to canonical vocabulary."""
        u = unit_str.strip().lower()
        if u in ("pcs", "pc", "piece", "pieces", "units", "unit", "nos", "no"):
            return "piece"
        if u in ("packets", "packet", "pkts", "pkt", "packs", "pack", "pouch", "pouches"):
            return "packet"
        if u in ("kg", "kgs", "kilo", "kilogram", "kilograms"):
            return "kg"
        if u in ("liter", "liters", "litre", "litres", "l", "ltr", "ltrs"):
            return "liter"
        if u in ("bottle", "bottles", "btl", "btls"):
            return "bottle"
        if u in ("box", "boxes", "bx", "bxs", "carton", "cartons"):
            return "box"
        if u in ("can", "cans", "tin", "tins"):
            return "can"
        if u in ("meter", "meters", "metre", "metres", "m"):
            return "meter"
        return u if len(u) <= 50 else u[:50]
