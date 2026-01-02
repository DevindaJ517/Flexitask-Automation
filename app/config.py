from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Supabase Configuration
    supabase_url: str = ""
    supabase_key: str = ""  # Service role key for server-side access
    
    # Telegram Configuration
    telegram_bot_token: str = ""
    telegram_channel_id: str = ""
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Job Site Configuration
    job_site_url: str = "https://flexi-task-zeta.vercel.app"
    
    # Polling Configuration
    polling_interval_seconds: int = 60  # How often to check for new jobs
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
