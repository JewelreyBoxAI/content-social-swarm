"""
Application settings and configuration management.

This module handles all configuration settings for ContentSocialSwarm,
including environment variables, API keys, and platform-specific settings.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Application Settings
    APP_NAME: str = "ContentSocialSwarm"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database Settings
    DATABASE_URL: str = Field(default="sqlite:///./data/contentsocialswarm.db", env="DATABASE_URL")
    VECTOR_STORE_PATH: str = Field(default="./data/vectorstore", env="VECTOR_STORE_PATH")
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # OpenAI Settings
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Facebook/Instagram Settings
    FACEBOOK_APP_ID: str = Field(env="FACEBOOK_APP_ID")
    FACEBOOK_APP_SECRET: str = Field(env="FACEBOOK_APP_SECRET")
    FACEBOOK_ACCESS_TOKEN: Optional[str] = Field(default=None, env="FACEBOOK_ACCESS_TOKEN")
    INSTAGRAM_BUSINESS_ACCOUNT_ID: Optional[str] = Field(default=None, env="INSTAGRAM_BUSINESS_ACCOUNT_ID")
    
    # X (Twitter) Settings
    TWITTER_API_KEY: str = Field(env="TWITTER_API_KEY")
    TWITTER_API_SECRET: str = Field(env="TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: str = Field(env="TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET: str = Field(env="TWITTER_ACCESS_TOKEN_SECRET")
    TWITTER_BEARER_TOKEN: str = Field(env="TWITTER_BEARER_TOKEN")
    
    # TikTok Settings
    TIKTOK_CLIENT_KEY: str = Field(env="TIKTOK_CLIENT_KEY")
    TIKTOK_CLIENT_SECRET: str = Field(env="TIKTOK_CLIENT_SECRET")
    TIKTOK_ACCESS_TOKEN: Optional[str] = Field(default=None, env="TIKTOK_ACCESS_TOKEN")
    
    # GoHighLevel Settings
    GHL_API_KEY: str = Field(env="GHL_API_KEY")
    GHL_BASE_URL: str = Field(default="https://services.leadconnectorhq.com", env="GHL_BASE_URL")
    GHL_LOCATION_ID: Optional[str] = Field(default=None, env="GHL_LOCATION_ID")
    
    # Security Settings
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Content Generation Settings
    MAX_CONTENT_LENGTH: int = Field(default=2000, env="MAX_CONTENT_LENGTH")
    DEFAULT_HASHTAG_COUNT: int = Field(default=5, env="DEFAULT_HASHTAG_COUNT")
    CONTENT_GENERATION_TIMEOUT: int = Field(default=30, env="CONTENT_GENERATION_TIMEOUT")
    
    # Rate Limiting Settings
    FACEBOOK_RATE_LIMIT: int = Field(default=600, env="FACEBOOK_RATE_LIMIT")  # requests per hour
    TWITTER_RATE_LIMIT: int = Field(default=300, env="TWITTER_RATE_LIMIT")    # requests per 15 min
    TIKTOK_RATE_LIMIT: int = Field(default=100, env="TIKTOK_RATE_LIMIT")      # requests per hour
    INSTAGRAM_RATE_LIMIT: int = Field(default=200, env="INSTAGRAM_RATE_LIMIT") # requests per hour
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="./logs/contentsocialswarm.log", env="LOG_FILE")
    
    # MCP Settings
    MCP_SERVER_URL: str = Field(default="http://localhost:8001", env="MCP_SERVER_URL")
    MCP_TIMEOUT: int = Field(default=30, env="MCP_TIMEOUT")
    
    # Agency Settings
    AGENCY_NAME: str = Field(default="Your Marketing Agency", env="AGENCY_NAME")
    AGENCY_LOGO_URL: Optional[str] = Field(default=None, env="AGENCY_LOGO_URL")
    WHITE_LABEL_MODE: bool = Field(default=True, env="WHITE_LABEL_MODE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 