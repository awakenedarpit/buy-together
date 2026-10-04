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
    return HealthResponse(
        status="ok",
        environment=settings.ENVIRONMENT,
        ai_provider=settings.AI_PROVIDER,
        version="0.1.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
