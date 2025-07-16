"""
Configuration settings for Wiki Impact Assessment System
维基影响评估系统的配置设置
"""

import os
from typing import List, Optional, Any
from pydantic import field_validator, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用程序设置，基于Pydantic的BaseSettings
    用于配置维基影响评估系统的各项参数
    """
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")
    
    # Basic application settings
    APP_NAME: str = "Wiki Entry Impact Assessment"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "200211"
    DB_NAME: str = "wiki_impact"
    
    # Redis settings
    REDIS_ENABLED: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 900  # 15 minutes
    
    # Wikipedia API settings
    WIKIPEDIA_API_URL: str = "https://en.wikipedia.org/w/api.php"
    WIKIPEDIA_RATE_LIMIT: int = 10  # requests per second
    
    # Celery settings (for background tasks)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @computed_field(return_type=str)
    def DATABASE_URL(self) -> str:
        """
        Build database URL from individual components.
        从各个组件构建数据库URL。
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field(return_type=str)
    def REDIS_URL(self) -> str:
        """
        Build Redis URL from individual components.
        从各个组件构建Redis URL。
        """
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return (
            f"redis://{password_part}{self.REDIS_HOST}:"
            f"{self.REDIS_PORT}/{self.REDIS_DB}"
        )

    @model_validator(mode='after')
    def set_celery_urls(self) -> 'Settings':
        """
        Use Redis URL for Celery broker and result backend if not specified.
        如果未指定，则使用Redis URL作为Celery代理和结果后端。
        """
        if self.CELERY_BROKER_URL is None:
            self.CELERY_BROKER_URL = self.REDIS_URL  # type: ignore[assignment]
        if self.CELERY_RESULT_BACKEND is None:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL  # type: ignore[assignment]
        return self
    
    @field_validator("ALLOWED_HOSTS", mode='before')
    def validate_allowed_hosts(cls, v: Any) -> List[str]:
        """
        Validate and process allowed hosts
        验证和处理允许的主机
        """
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    # The Config class is replaced by model_config in Pydantic v2
    # class Config:
    #     env_file = ".env"
    #     case_sensitive = True


# Create global settings instance
settings = Settings()


# Environment-specific configurations
class DevelopmentConfig(Settings):
    """Development environment configuration"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionConfig(Settings):
    """Production environment configuration"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"


class TestingConfig(Settings):
    """Testing environment configuration"""
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    DB_NAME: str = "wiki_impact_test"
    REDIS_DB: int = 1


def get_settings() -> Settings:
    """
    Factory function to get environment-specific settings
    获取环境特定设置的工厂函数
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig() 