from telegram import Bot
from telegram.constants import ParseMode
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)


class TelegramService:
    """
    Telegram service for posting to channels
    Uses python-telegram-bot library
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.bot_token = self.settings.telegram_bot_token
        self.channel_id = self.settings.telegram_channel_id
        self.bot = None
        
        if self.is_configured():
            self.bot = Bot(token=self.bot_token)
    
    def is_configured(self) -> bool:
        """Check if Telegram service is configured"""
        return bool(self.bot_token and self.channel_id)
    
    async def send_to_channel(self, message: str, job_url: str) -> bool:
        """
        Send message to Telegram channel
        
        Requirements:
        1. Create a bot using @BotFather on Telegram
        2. Get the bot token from BotFather
        3. Create a channel and add the bot as an administrator
        4. Get the channel username (@channelname) or channel ID
        
        Channel ID formats:
        - Public channel: @channelname
        - Private channel: -100123456789 (numeric ID)
        
        API Documentation:
        https://core.telegram.org/bots/api
        """
        
        if not self.is_configured():
            logger.warning("Telegram service not configured")
            return False
        
        try:
            # Format message with Markdown
            formatted_message = self._format_message_markdown(message, job_url)
            
            logger.info(f"Sending message to Telegram channel: {self.channel_id}")
            
            # Send message to channel
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            
            logger.info("Telegram message sent successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def _format_message_markdown(self, message: str, job_url: str) -> str:
        """Format message with Telegram Markdown"""
        # Escape special characters for Markdown
        # Note: python-telegram-bot handles most escaping automatically
        
        formatted = f"{message}\n\n[🔗 Apply Now]({job_url})"
        return formatted
    
    async def get_channel_info(self) -> dict:
        """Get Telegram channel information (for testing)"""
        if not self.is_configured():
            return {}
        
        try:
            chat = await self.bot.get_chat(chat_id=self.channel_id)
            return {
                "id": chat.id,
                "title": chat.title,
                "type": chat.type,
                "username": chat.username
            }
        
        except Exception as e:
            logger.error(f"Error getting channel info: {str(e)}")
            return {}
    
    async def send_photo_with_caption(self, photo_url: str, caption: str, job_url: str) -> bool:
        """
        Send photo with caption to Telegram channel
        Useful if you want to include company logo or job image
        """
        if not self.is_configured():
            return False
        
        try:
            formatted_caption = f"{caption}\n\n[🔗 Apply Now]({job_url})"
            
            await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=photo_url,
                caption=formatted_caption,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info("Telegram photo sent successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error sending Telegram photo: {str(e)}")
            return False
