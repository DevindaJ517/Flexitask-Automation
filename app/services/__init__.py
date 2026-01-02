"""
Services package for FlexiTask Automation

Contains all service modules for:
- Supabase database monitoring
- Telegram channel posting
"""

from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService

__all__ = [
    "SupabaseService",
    "TelegramService"
]
