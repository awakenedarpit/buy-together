"""Local Gemma 4 12B AI Provider using HuggingFace Transformers and PyTorch."""

import json
import os
import re
from pathlib import Path
from typing import Optional, Any
from backend.app.ai.base import BaseAIProvider
from backend.app.ai.exceptions import (
    AIProviderConfigurationError,
    AIProviderRuntimeError,
    AIExtractionValidationError,
)
from backend.app.schemas.ai import ExtractedItem, ExtractionResult
from backend.app.core.config import settings
from backend.app.core.logging import logger


class LocalGemmaProvider(BaseAIProvider):
    """Local inference provider for Gemma 4 12B.
    
    Loads weights lazily upon the first extraction request.
    Validates machine environment, device availability, and model path prior to initialization.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        precision: Optional[str] = None,
    ):
        self.model_path = model_path or settings.GEMMA_MODEL_PATH
        self.device = device or settings.GEMMA_DEVICE
        self.precision = precision or settings.GEMMA_PRECISION
        self._pipeline: Optional[Any] = None
        self._is_loaded: bool = False
        self._prompt_template: Optional[str] = None

    @property
    def provider_name(self) -> str:
        return "local_gemma"

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def _load_prompt_template(self) -> str:
        """Load versioned extraction prompt template from disk."""
        if self._prompt_template is not None:
            return self._prompt_template

        prompt_path = Path(__file__).parent / "prompts" / "v1_extract.txt"
        if not prompt_path.is_file():
            raise AIProviderConfigurationError(f"Prompt template missing at: {prompt_path}")

        try:
            self._prompt_template = prompt_path.read_text(encoding="utf-8")
            return self._prompt_template
        except Exception as exc:
            raise AIProviderConfigurationError(f"Failed to read prompt template: {exc}")

    def _lazy_load_pipeline(self) -> None:
        """Lazily initialize HuggingFace transformers pipeline."""
        if self._is_loaded:
            return

        if not self.model_path:
            raise AIProviderConfigurationError(
                "GEMMA_MODEL_PATH is not configured. Provide a valid local directory or HuggingFace identifier."
            )

        # Check for local directory existence if path looks like a filesystem path
        if os.path.exists(self.model_path) and not os.path.isdir(self.model_path):
            raise AIProviderConfigurationError(f"Configured model path is not a valid directory: {self.model_path}")

        logger.info(
            f"[LocalGemmaProvider] Attempting to load model '{self.model_path}' on device '{self.device}' with {self.precision} precision..."
        )

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        except ImportError as exc:
            logger.error(f"[LocalGemmaProvider] Missing deep learning libraries: {exc}")
            raise AIProviderRuntimeError(
                "PyTorch or Transformers not installed in environment. "
                "Install torch and transformers to use LocalGemmaProvider."
            ) from exc

        try:
            # Map precision
            dtype = torch.bfloat16 if self.precision == "bfloat16" else (
                torch.float16 if self.precision == "float16" else torch.float32
            )

            tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=dtype,
                device_map=self.device if self.device != "cpu" else None,
                local_files_only=True,
            )

            self._pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device.startswith("cuda") else -1,
            )
            self._is_loaded = True
            logger.info(f"[LocalGemmaProvider] Model '{self.model_path}' loaded successfully.")

        except Exception as exc:
            self._is_loaded = False
            self._pipeline = None
            logger.error(f"[LocalGemmaProvider] Failed loading model: {exc}")
            raise AIProviderRuntimeError(
                f"Failed to initialize local Gemma model from '{self.model_path}': {exc}"
            ) from exc

    async def extract_items(self, text: str) -> ExtractionResult:
        """Run text through prompt and extract items using local model."""
        self._lazy_load_pipeline()

        if self._pipeline is None:
            raise AIProviderRuntimeError("Local model pipeline is not initialized")

        template = self._load_prompt_template()
        prompt = template.replace("{message}", text)

        try:
            outputs = self._pipeline(
                prompt,
                max_new_tokens=512,
                do_sample=False,
                temperature=0.0,
                return_full_text=False,
            )
            raw_text = outputs[0]["generated_text"].strip()
        except Exception as exc:
            logger.error(f"[LocalGemmaProvider] Inference execution failure: {exc}")
            raise AIProviderRuntimeError(f"Gemma inference execution failed: {exc}") from exc

        # Parse JSON from model output
        return self._parse_model_json(raw_text)

    def _parse_model_json(self, raw_text: str) -> ExtractionResult:
        """Safely extract and validate JSON payload from raw model generation."""
        # Strip potential markdown fences (```json ... ```)
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE).strip()

        # Find first '{' and matching '}' if surrounding fluff exists
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx : end_idx + 1]

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.warning(f"[LocalGemmaProvider] Model output was not valid JSON: {raw_text}")
            raise AIExtractionValidationError(f"Invalid JSON returned by model: {exc}") from exc

        if not isinstance(data, dict) or "items" not in data or not isinstance(data["items"], list):
            raise AIExtractionValidationError("Model JSON output missing 'items' array")

        valid_items: list[ExtractedItem] = []
        for raw_item in data["items"]:
            try:
                valid_items.append(ExtractedItem(**raw_item))
            except Exception as item_err:
                logger.warning(f"[LocalGemmaProvider] Skipping invalid item object {raw_item}: {item_err}")

        return ExtractionResult(items=valid_items, raw_response=raw_text)
