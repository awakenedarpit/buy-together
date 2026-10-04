# ADR-002: Pluggable AI Provider Abstraction Interface

## Status
Accepted

## Context
The application uses Gemma 4 12B to convert natural language (English and Hinglish) into structured item lists. However, relying on a hardcoded Gemma instance throughout the business layer would tightly couple the application to a specific model, requiring extensive rewrites if the developer needs to run tests offline, switch to a hosted API (e.g. HuggingFace, OpenAI-compatible endpoint), or migrate to a newer model generation in the future.

## Decision
We create a decoupled provider abstraction (`BaseAIProvider`) in `backend/app/ai/base.py`. The application services (`MessageService`) interact solely with this interface.
Concrete providers include:
- `MockAIProvider`: Zero-dependency, deterministic provider for unit tests and local frontend testing.
- `LocalGemmaProvider`: Local execution of Gemma 4 12B using PyTorch / Transformers.
- `HostedInferenceProvider`: Remote execution via HuggingFace Inference API or compatible REST endpoint.

The active provider is resolved at startup via the `AI_PROVIDER` configuration setting.

## Alternatives Considered
1. **Directly calling HuggingFace Transformers in Route Handlers**:
   - *Pros*: Faster to prototype in a single script.
   - *Cons*: Impossible to run unit tests without downloading 24GB of weights or having a dedicated GPU; couples web logic to ML framework.
2. **Heavyweight LLM Orchestration Frameworks (LangChain / LlamaIndex)**:
   - *Pros*: Pre-built abstractions.
   - *Cons*: Massive dependency footprint, rapid breaking API changes, black-box prompt abstractions that obscure system behavior.

## Consequences
- Clean separation between NLP extraction and business logic.
- Fast, zero-GPU unit and integration testing.
- Easy migration to future model architectures.
