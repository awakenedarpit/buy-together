"""Health Check API Router

Provides system status, environment metadata, and liveness verification.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    environment: str
    ai_provider: str
    version: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def check_health() -> HealthResponse:
    """Liveness probe returning application health status."""
    active_provider = "gemini" if (settings.GEMINI_API_KEY or settings.AI_PROVIDER == "gemini") else settings.AI_PROVIDER
    return HealthResponse(
        status="ok",
        environment=settings.ENVIRONMENT,
        ai_provider=active_provider,
        version="0.1.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
