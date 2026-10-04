"""Mock AI Provider for deterministic, zero-dependency testing."""

import json
import re
from typing import Optional, List
from backend.app.ai.base import BaseAIProvider
from backend.app.ai.exceptions import AIProviderRuntimeError
from backend.app.schemas.ai import ExtractedItem, ExtractionResult
from backend.app.core.logging import logger


class MockAIProvider(BaseAIProvider):
    """Deterministic, rule-based AI provider.
    
    Used for local development, fast unit tests, and CI/CD pipelines
    where loading large model weights (e.g. Gemma 4 12B) is impossible or too slow.
    """

    def __init__(
        self,
        simulate_error: bool = False,
        simulate_malformed_json: bool = False,
        custom_raw_response: Optional[str] = None,
    ):
        self.simulate_error = simulate_error
        self.simulate_malformed_json = simulate_malformed_json
        self.custom_raw_response = custom_raw_response

    @property
    def provider_name(self) -> str:
        return "mock"

    async def extract_items(self, text: str) -> ExtractionResult:
        logger.info(f"[MockAIProvider] Ingesting message: '{text}'")

        if self.simulate_error:
            logger.error("[MockAIProvider] Simulating provider runtime error")
            raise AIProviderRuntimeError("Simulated AI inference error from MockAIProvider")

        if self.simulate_malformed_json:
            return ExtractionResult(
                items=[],
                raw_response="INVALID_JSON{{{not valid json",
            )

        if self.custom_raw_response is not None:
            try:
                data = json.loads(self.custom_raw_response)
                items = []
                for it in data.get("items", []):
                    try:
                        items.append(ExtractedItem(**it))
                    except Exception:
                        continue
                return ExtractionResult(items=items, raw_response=self.custom_raw_response)
            except Exception as exc:
                logger.warning(f"[MockAIProvider] Failed parsing custom raw response: {exc}")
                return ExtractionResult(items=[], raw_response=self.custom_raw_response)

        normalized = text.strip().lower()

        # Fixture 1: Hinglish canonical example
        if "notebook" in normalized and "pen" in normalized and ("bhai" in normalized or "aur" in normalized or "and" in normalized):
            items = [
                ExtractedItem(name="notebook", variant=None, quantity=2, unit="piece"),
                ExtractedItem(name="pen", variant="blue", quantity=1, unit="piece"),
            ]
            return ExtractionResult(
                items=items,
                raw_response=json.dumps({"items": [it.model_dump() for it in items]}),
            )

        # Fixture 2: English grocery & stationery
        if "milk" in normalized and "sugar" in normalized:
            items = [
                ExtractedItem(name="milk", variant=None, quantity=3, unit="packet"),
                ExtractedItem(name="sugar", variant=None, quantity=1, unit="kg"),
                ExtractedItem(name="gel pen", variant="black", quantity=2, unit="piece"),
            ]
            return ExtractionResult(
                items=items,
                raw_response=json.dumps({"items": [it.model_dump() for it in items]}),
            )

        # Fixture 3: Conversational greetings / no item intent
        greetings = ["hello", "hi", "kya haal", "sab theek", "good morning", "kaise ho"]
        if any(g in normalized for g in greetings) and not any(k in normalized for k in ["add", "need", "chahiye", "aur", "packet", "kg", "notebook", "pen"]):
            return ExtractionResult(
                items=[],
                raw_response=json.dumps({"items": []}),
            )

        # Heuristic / regex parser for common patterns (e.g. "5 notebooks", "2 packets of milk", "ek bread")
        extracted = self._heuristic_extract(text)
        return ExtractionResult(
            items=extracted,
            raw_response=json.dumps({"items": [it.model_dump() for it in extracted]}),
        )

    def _heuristic_extract(self, text: str) -> List[ExtractedItem]:
        """Simple deterministic fallback parsing for unmapped sentences in tests."""
        items: List[ExtractedItem] = []
        words_num = {
            "ek": 1, "one": 1, "a": 1, "an": 1,
            "do": 2, "two": 2,
            "teen": 3, "three": 3,
            "char": 4, "chaar": 4, "four": 4,
            "paanch": 5, "panch": 5, "five": 5,
        }

        # Normalize Hindi numerals to digits
        tokens = text.lower().split()
        normalized_tokens = [str(words_num.get(t, t)) for t in tokens]
        normalized_text = " ".join(normalized_tokens)

        # Pattern: <quantity> [unit] [variant] <name>
        pattern = re.compile(
            r"(\d+)\s*(packet|packets|pkg|kg|kgs|kilo|piece|pieces|bottle|bottles|box|boxes|can|cans)?\s*(blue|black|red|green|ruled|unruled|white)?\s*([a-zA-Z]+)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(normalized_text):
            qty_str, unit_str, variant_str, name_str = match.groups()
            try:
                qty = int(qty_str)
            except ValueError:
                qty = 1

            if name_str in {"packets", "pieces", "kg", "kgs", "box", "boxes", "bottles", "aur", "and", "of", "the"}:
                continue

            # Standardize unit
            unit = "piece"
            if unit_str:
                u = unit_str.lower()
                if "packet" in u or "pkg" in u:
                    unit = "packet"
                elif "kg" in u or "kilo" in u:
                    unit = "kg"
                elif "bottle" in u:
                    unit = "bottle"
                elif "box" in u:
                    unit = "box"

            # Standardize name (remove trailing 's' if plural)
            name = name_str.lower()
            if name.endswith("s") and len(name) > 3 and not name.endswith("ss"):
                name = name[:-1]

            variant = variant_str.lower() if variant_str else None

            items.append(ExtractedItem(
                name=name,
                variant=variant,
                quantity=qty,
                unit=unit,
            ))

        return items
