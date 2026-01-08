"""
Core Configuration for Time Tracking Platform
Environment-based settings with comprehensive defaults
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import secrets


class Settings(BaseSettings):
    # ==================== APPLICATION ====================
    APP_NAME: str = "TimeTracker Pro"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # ==================== SERVER ====================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    WORKERS: int = 4
    
    # ==================== DATABASE ====================
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "timetracker"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "timetracker"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # ==================== REDIS ====================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ==================== SECURITY ====================
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # ==================== FILE STORAGE ====================
    STORAGE_TYPE: str = "minio"  # minio, s3, local
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "timetracker"
    
    # AWS S3 (alternative)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "timetracker-uploads"
    
    # Local storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # ==================== EMAIL ====================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@timetracker.com"
    SMTP_FROM_NAME: str = "TimeTracker"
    
    # ==================== OAUTH ====================
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/google/callback"
    
    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_REDIRECT_URI: str = "http://localhost:3000/auth/microsoft/callback"
    
    # ==================== PAYMENT ====================
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Pricing (in cents)
    PRICE_STARTER: int = 1200  # $12/user/month
    PRICE_PROFESSIONAL: int = 2400  # $24/user/month
    PRICE_BUSINESS: int = 4900  # $49/user/month
    PRICE_ENTERPRISE: int = 9900  # $99/user/month
    PRICE_WHITE_LABEL: int = 49900  # $499/month base
    
    # ==================== AI & ML ====================
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 1000
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # ==================== INTEGRATIONS ====================
    # Slack
    SLACK_CLIENT_ID: Optional[str] = None
    SLACK_CLIENT_SECRET: Optional[str] = None
    SLACK_SIGNING_SECRET: Optional[str] = None
    
    # Jira
    JIRA_API_TOKEN: Optional[str] = None
    
    # ==================== FEATURES ====================
    # Screenshots
    SCREENSHOT_ENABLED: bool = True
    SCREENSHOT_INTERVAL: int = 600  # seconds
    SCREENSHOT_QUALITY: int = 85  # JPEG quality
    SCREENSHOT_BLUR_ENABLED: bool = True
    
    # Activity Tracking
    ACTIVITY_TRACKING_ENABLED: bool = True
    IDLE_TIMEOUT: int = 180  # seconds
    
    # AI Features
    AI_INSIGHTS_ENABLED: bool = True
    AI_COACHING_ENABLED: bool = True
    AI_AUTOPILOT_ENABLED: bool = False
    
    # Geolocation
    GEOLOCATION_ENABLED: bool = False
    GEOFENCING_ENABLED: bool = False
    
    # Video Recording
    VIDEO_RECORDING_ENABLED: bool = False
    
    # Blockchain
    BLOCKCHAIN_ENABLED: bool = False
    ETHEREUM_RPC_URL: Optional[str] = None
    ETHEREUM_PRIVATE_KEY: Optional[str] = None
    
    # ==================== MONITORING ====================
    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"
    
    # Prometheus
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    
    # ==================== CELERY ====================
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @property
    def CELERY_BROKER(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL
    
    @property
    def CELERY_BACKEND(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL
    
    # ==================== COMPLIANCE ====================
    GDPR_COMPLIANCE: bool = True
    HIPAA_COMPLIANCE: bool = False
    SOC2_COMPLIANCE: bool = False
    
    # Data retention (days)
    SCREENSHOT_RETENTION_DAYS: int = 90
    ACTIVITY_RETENTION_DAYS: int = 365
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    
    # ==================== RATE LIMITING ====================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ==================== WEBSOCKET ====================
    WEBSOCKET_ENABLED: bool = True
    WEBSOCKET_PATH: str = "/ws"
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, text
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Helper functions
def get_settings() -> Settings:
    """Get settings instance"""
    return settings


def is_production() -> bool:
    """Check if running in production"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """Check if running in development"""
    return settings.ENVIRONMENT == "development"


def feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    feature_map = {
        "screenshots": settings.SCREENSHOT_ENABLED,
        "activity_tracking": settings.ACTIVITY_TRACKING_ENABLED,
        "ai_insights": settings.AI_INSIGHTS_ENABLED,
        "ai_coaching": settings.AI_COACHING_ENABLED,
        "ai_autopilot": settings.AI_AUTOPILOT_ENABLED,
        "geolocation": settings.GEOLOCATION_ENABLED,
        "geofencing": settings.GEOFENCING_ENABLED,
        "video_recording": settings.VIDEO_RECORDING_ENABLED,
        "blockchain": settings.BLOCKCHAIN_ENABLED,
        "websocket": settings.WEBSOCKET_ENABLED,
        "metrics": settings.METRICS_ENABLED,
    }
    return feature_map.get(feature, False)
