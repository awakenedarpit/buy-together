# AI Extraction & Model Integration Guide

## Project: Buy Together
**Target Model**: Gemma 4 12B  
**Primary Framework**: PyTorch / HuggingFace Transformers (Local) & HuggingFace Inference API (Hosted)  
**Testing Provider**: `MockAIProvider`  

---

## 1. Purpose & Domain Scope

The role of the AI component in **Buy Together** is strictly linguistic extraction and normalization. Group members frequently communicate in conversational, informal English, Hindi, or Hinglish (e.g. *"bhai 2 notebook aur ek blue pen"*).

The AI model parses this informal natural language and maps it into a structured, validated JSON payload representing concrete items, quantities, units, and variants.

---

## 2. Extraction Contract & Examples

### 2.1 JSON Schema Contract
The model must strictly produce JSON conforming to this contract:

```json
{
  "items": [
    {
      "name": "string (lowercase, singular, normalized item name)",
      "variant": "string | null (color, brand, ruling, or null if unspecified)",
      "quantity": "integer (positive integer >= 1)",
      "unit": "string (piece, packet, box, bottle, kg, liter)"
    }
  ]
}
```

### 2.2 Concrete Hinglish Examples

#### Example 1 (Mixed Hinglish):
- **User Input**: `"bhai 2 notebook aur ek blue pen"`
- **Expected Output**:
  ```json
  {
    "items": [
      {
        "name": "notebook",
        "variant": null,
        "quantity": 2,
        "unit": "piece"
      },
      {
        "name": "pen",
        "variant": "blue",
        "quantity": 1,
        "unit": "piece"
      }
    ]
  }
  ```

#### Example 2 (Complex Grocery/Stationery Request):
- **User Input**: `"Please add 3 packets of milk, 1kg sugar and 2 black gel pens"`
- **Expected Output**:
  ```json
  {
    "items": [
      {
        "name": "milk",
        "variant": null,
        "quantity": 3,
        "unit": "packet"
      },
      {
        "name": "sugar",
        "variant": null,
        "quantity": 1,
        "unit": "kg"
      },
      {
        "name": "gel pen",
        "variant": "black",
        "quantity": 2,
        "unit": "piece"
      }
    ]
  }
  ```

#### Example 3 (Unclear or Zero-item Message):
- **User Input**: `"hello sab log kaise ho?"` (Conversational greeting, no purchase intent)
- **Expected Output**:
  ```json
  {
    "items": []
  }
  ```

---

## 3. Strict Demarcation of AI Responsibilities

### AI Responsibilities (Linguistic Only):
1. **Linguistic Parsing**: Detecting items, numbers (e.g. "ek" -> 1, "do" -> 2), and units.
2. **Variant Extraction**: Extracting modifiers (colors, rulings, sizes) into the `variant` field.
3. **Canonical Normalization**: Standardizing terms (e.g., "pens" -> "pen", "doodh" -> "milk").
4. **Structured JSON Output**: Emitting valid JSON.

### AI Non-Responsibilities (Handled Strictly by Python Backend):
1. **NO Business Authorization**: AI never checks permissions or modifies role access.
2. **NO Pricing Decisions**: Gemma never suggests or sets prices.
3. **NO Database Mutations**: The model has zero database connections.
4. **NO Arithmetic Totals**: The model never calculates totals or grand sums.
5. **NO Trust**: Pydantic validates all types, constraints, and ranges prior to persistence.

---

## 4. AI Provider Abstraction Interface

To prevent tight coupling to a single model runtime, all interactions route through an abstract interface:

```python
# backend/app/ai/base.py
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractedItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    variant: Optional[str] = Field(None, max_length=100)
    quantity: int = Field(1, ge=1)
    unit: str = Field("piece", max_length=50)

class ExtractionResult(BaseModel):
    items: List[ExtractedItem] = Field(default_factory=list)
    raw_response: Optional[str] = None

class BaseAIProvider(ABC):
    @abstractmethod
    async def extract_items(self, text: str) -> ExtractionResult:
        """Extract structured items from natural language text."""
        pass
```

### Supported Provider Implementations:
1. **`MockAIProvider`**: Uses rule-based regex and canned Hinglish/English fixtures for fast, zero-dependency testing without requiring a GPU.
2. **`LocalGemmaProvider`**: Uses HuggingFace `transformers` and `torch` to run `google/gemma-4-12b-it` locally with optional 4-bit / 8-bit quantization.
3. **`HostedInferenceProvider`**: Calls HuggingFace Serverless Inference API or an OpenAI-compatible completion endpoint via HTTP.

Switching providers is controlled by the `AI_PROVIDER` environment variable (`mock`, `local_gemma`, `hosted`).

---

## 5. Prompt Engineering & Versioning

Prompts are stored as distinct versioned template files in `backend/app/ai/prompts/` (e.g., `v1_extract.txt`).

### Prompt Template Strategy (`v1_extract.txt`):
- System Persona: High-precision multilingual purchase extraction engine.
- Instruction: Extract items into strict JSON containing only the `"items"` array.
- Few-shot Hinglish examples.
- Anti-hallucination instruction: "If no purchase requirements are mentioned, return `{\"items\": []}`."
- Guardrails: "Do NOT output markdown commentary or explanation. Return ONLY raw JSON."
