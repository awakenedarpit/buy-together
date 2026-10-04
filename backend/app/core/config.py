"""Application Configuration Module

Loads and validates settings from environment variables and `.env` file using Pydantic Settings.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment & Logging
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    # Server Configuration
    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./buy_together.db",
        description="Database connection URL (PostgreSQL in production; SQLite fallback for local test/dev)",
    )

    # Authentication & Security
    JWT_SECRET: str = Field(
        default="development-insecure-jwt-secret-key-do-not-use-in-production-64char",
        description="Cryptographic secret key for signing JWT tokens",
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)  # 24 hours

    # AI Provider Settings
    AI_PROVIDER: str = Field(
        default="mock",
        description="AI engine selection: 'mock', 'local_gemma', or 'hosted'",
    )
    GEMMA_MODEL_PATH: str = Field(default="google/gemma-4-12b-it")
    GEMMA_DEVICE: str = Field(default="cpu")
    GEMMA_PRECISION: str = Field(default="bfloat16")
    HOSTED_INFERENCE_URL: Optional[str] = Field(default=None)
    HF_TOKEN: Optional[str] = Field(default=None)

    # Demo Accounts Configuration (Server-Side Only)
    DEMO_MEMBER_EMAIL: str = Field(default="demo.member@buytogether.app")
    DEMO_MEMBER_PASSWORD: str = Field(default="DemoMemberSecurePass2026!")
    DEMO_MANAGER_EMAIL: str = Field(default="demo.manager@buytogether.app")
    DEMO_MANAGER_PASSWORD: str = Field(default="DemoManagerSecurePass2026!")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None)

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS_ORIGINS string to a clean list."""
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @field_validator("AI_PROVIDER")
    @classmethod
    def validate_ai_provider(cls, v: str) -> str:
        allowed = {"mock", "local_gemma", "hosted", "hosted_gemma"}
        if v.lower() not in allowed:
            raise ValueError(f"AI_PROVIDER must be one of: {allowed}")
        return v.lower()


settings = Settings()
