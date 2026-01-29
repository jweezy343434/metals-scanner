"""
Configuration settings using Pydantic for validation
"""
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings with validation"""

    # API Keys
    EBAY_API_KEY: str
    METALS_API_KEY: str

    # Database
    DATABASE_URL: str = "sqlite:////app/data/metals_scanner.db"

    # Scheduler
    ENABLE_AUTO_SCAN: bool = True
    SCAN_INTERVAL_HOURS: int = 2

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limits
    EBAY_DAILY_LIMIT: int = 5000
    METALS_API_MONTHLY_LIMIT: int = 50

    # Caching (minutes)
    CACHE_MARKET_HOURS: int = 15
    CACHE_OFF_HOURS: int = 60
    CACHE_WEEKEND: int = 240

    # API Timeouts (seconds)
    API_TIMEOUT: int = 10
    API_RETRY_ATTEMPTS: int = 3

    @validator('EBAY_API_KEY', 'METALS_API_KEY')
    def validate_api_keys(cls, v, field):
        """Ensure API keys are not placeholders"""
        if not v or v.startswith('your_') or v == '':
            raise ValueError(
                f'{field.name} must be set to a valid API key, not a placeholder'
            )
        return v

    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Ensure log level is valid"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()

    @validator('SCAN_INTERVAL_HOURS')
    def validate_scan_interval(cls, v):
        """Ensure scan interval is reasonable"""
        if v < 1 or v > 24:
            raise ValueError('SCAN_INTERVAL_HOURS must be between 1 and 24')
        return v

    class Config:
        env_file = '.env'
        case_sensitive = True


# Global settings instance
settings = Settings()
