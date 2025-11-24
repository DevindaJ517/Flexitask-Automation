from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # WhatsApp Configuration
    whatsapp_api_key: str = ""
    whatsapp_phone_number: str = ""
    whatsapp_group_id: str = ""
    
    # Facebook Configuration
    facebook_access_token: str = ""
    facebook_group_id: str = ""
    
    # Telegram Configuration
    telegram_bot_token: str = ""
    telegram_channel_id: str = ""
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Job Site Configuration
    job_site_url: str = "https://yourjobsite.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
