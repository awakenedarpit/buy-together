"""Google Gemini AI Provider for Natural Language Purchase Requirement Extraction.

Uses official Google GenAI SDK (or direct Gemini REST API) with strict JSON output mode.
Implements the Zero-Trust BaseAIProvider interface.
"""

import json
import os
from typing import Optional, List
from backend.app.ai.base import BaseAIProvider
from backend.app.ai.exceptions import AIProviderError, AIProviderRuntimeError, AIProviderConfigurationError
from backend.app.schemas.ai import ExtractedItem, ExtractionResult
from backend.app.core.config import settings
from backend.app.core.logging import logger

SYSTEM_INSTRUCTION = """You extract purchase requirements from natural language.
Return ONLY JSON matching the required schema:
{
  "items": [
    {
      "name": "item name",
      "quantity": 2,
      "unit": "piece",
      "variant": "optional variant/color/size or null"
    }
  ]
}

Extraction rules:
1. Identify every requested item.
2. Extract quantity. If quantity is genuinely missing, use quantity = 1 unless the phrase clearly indicates otherwise.
3. Extract unit when present (default to 'piece' if not explicitly stated).
4. Extract variant/color/size when present (e.g. 'blue', 'black', 'A4', 'ruled', 'red'). If absent, set variant to null.
5. Normalize obvious singular/plural differences (e.g. 'notebooks' -> 'notebook', 'pens' -> 'pen', 'files' -> 'file', 'pencils' -> 'pencil').
6. Preserve meaningful variants.
7. Never invent an item.
8. Never invent a quantity.
9. Never invent a price.
10. Never invent availability.

Do not answer the user.
Do not explain your reasoning.
Do not invent information.
Return ONLY the raw JSON object.
Support English, Hindi, and Hinglish.
"""


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI Provider for requirement extraction."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        self.model_name = model or os.getenv("GEMINI_MODEL") or settings.GEMINI_MODEL or "gemini-2.5-flash"
        self._client = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _get_client(self):
        """Lazily initialize Google GenAI client."""
        if not self.api_key:
            raise AIProviderConfigurationError(
                "GEMINI_API_KEY is not configured in environment or settings."
            )
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                logger.error(f"[GeminiProvider] Failed to initialize google-genai client: {exc}")
                raise AIProviderRuntimeError(f"Could not initialize GenAI client: {exc}")
        return self._client

    async def extract_items(self, text: str) -> ExtractionResult:
        """Call Gemini to extract structured purchase items from natural language text."""
        clean_text = text.strip()
        if not clean_text:
            return ExtractionResult(items=[], raw_response=json.dumps({"items": []}))

        if not self.api_key:
            logger.warning("[GeminiProvider] No GEMINI_API_KEY provided. Triggering provider failure for fallback.")
            raise AIProviderConfigurationError("GEMINI_API_KEY is missing")

        logger.info(f"[GeminiProvider] Submitting request to Gemini model '{self.model_name}'")

        try:
            client = self._get_client()
            from google.genai import types

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                temperature=0.1,
            )

            # Call async generation
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=clean_text,
                config=config,
            )

            raw_text = response.text or ""
            logger.info(f"[GeminiProvider] Received response from Gemini (length: {len(raw_text)})")

            # Parse JSON
            parsed = self._parse_json(raw_text)
            items_raw = parsed.get("items", [])
            if not isinstance(items_raw, list):
                logger.warning(f"[GeminiProvider] 'items' in response is not a list: {items_raw}")
                items_raw = []

            extracted_items: List[ExtractedItem] = []
            for raw_item in items_raw:
                try:
                    if not isinstance(raw_item, dict):
                        continue
                    name = str(raw_item.get("name", "")).strip().lower()
                    if not name:
                        continue
                    qty = raw_item.get("quantity", 1)
                    if not isinstance(qty, int) or qty < 1:
                        try:
                            qty = int(qty)
                            if qty < 1:
                                qty = 1
                        except Exception:
                            qty = 1

                    unit = str(raw_item.get("unit") or "piece").strip().lower()
                    variant = raw_item.get("variant")
                    if variant:
                        variant = str(variant).strip().lower()
                    else:
                        variant = None

                    extracted_items.append(
                        ExtractedItem(
                            name=name,
                            quantity=qty,
                            unit=unit,
                            variant=variant,
                        )
                    )
                except Exception as parse_err:
                    logger.warning(f"[GeminiProvider] Error parsing item {raw_item}: {parse_err}")
                    continue

            return ExtractionResult(items=extracted_items, raw_response=raw_text)

        except Exception as exc:
            logger.error(f"[GeminiProvider] Inference failure: {exc}")
            raise AIProviderRuntimeError(f"Gemini API inference error: {exc}") from exc

    def _parse_json(self, raw_text: str) -> dict:
        """Safely parse JSON from model output, stripping markdown if present."""
        clean = raw_text.strip()
        if clean.startswith("```"):
            # Strip markdown code blocks
            lines = clean.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            clean = "\n".join(lines).strip()

        try:
            return json.loads(clean)
        except json.JSONDecodeError as err:
            logger.warning(f"[GeminiProvider] Failed to decode JSON from Gemini output: {err}")
            raise
