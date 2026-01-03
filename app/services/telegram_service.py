"""
Telegram Service for FlexiTask Job Posting

Uses python-telegram-bot library to send job alerts to Telegram channels.
Supports both text messages and messages with images.
"""

from telegram import Bot
from telegram.constants import ParseMode
from typing import Optional
from app.config import get_settings
from app.models import JobPosting
import logging

logger = logging.getLogger(__name__)


class TelegramService:
    """
    Telegram service for posting to channels
    Uses python-telegram-bot library
    
    Requirements:
    1. Create a bot using @BotFather on Telegram
    2. Get the bot token from BotFather
    3. Create a channel and add the bot as an administrator
    4. Get the channel username (@channelname) or channel ID
    
    Channel ID formats:
    - Public channel: @channelname
    - Private channel: -100123456789 (numeric ID)
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
    
    def format_job_message(self, job: JobPosting) -> str:
        """
        Format job posting message for Telegram
        
        Telegram supports Markdown and HTML formatting.
        Using Markdown for compatibility.
        """
        
        # Map employment types to readable format
        employment_map = {
            "FULL_TIME": "Full Time",
            "PART_TIME": "Part Time",
            "CONTRACT": "Contract"
        }
        
        work_location_map = {
            "ONSITE": "On-site",
            "REMOTE": "Remote",
            "HYBRID": "Hybrid"
        }
        
        experience_map = {
            "ONE_PLUS": "1+ years",
            "TWO_PLUS": "2+ years",
            "FIVE_PLUS": "5+ years"
        }
        
        # Build location string
        location_parts = []
        if job.city:
            location_parts.append(job.city.name)
        if job.country:
            location_parts.append(job.country.name)
        location = ", ".join(location_parts) if location_parts else "Location not specified"
        
        # Get readable types
        employment = self._escape_markdown(employment_map.get(job.employmentType.value, job.employmentType.value))
        work_type = self._escape_markdown(work_location_map.get(job.workLocationType.value, job.workLocationType.value))
        
        # Build message with Telegram Markdown formatting
        message = f"🚀 *New Job Alert\\!*\n\n"
        
        # Escape special characters for MarkdownV2
        title = self._escape_markdown(job.title)
        company = self._escape_markdown(job.companyName)
        location = self._escape_markdown(location)
        
        message += f"📌 *{title}* at _{company}_\n"
        message += f"📍 {location} \\| {work_type}\n"
        message += f"💼 {employment}\n"
        
        # Add category if available
        if job.category:
            category_name = self._escape_markdown(job.category.name)
            message += f"🏷️ {category_name}\n"
        
        # Add experience requirement
        if job.experienceYears:
            experience = self._escape_markdown(experience_map.get(job.experienceYears.value, job.experienceYears.value))
            message += f"📊 Experience: {experience}\n"
        
        # Add internship badge if applicable
        if job.isInternship:
            message += "🎓 *Internship Position*\n"
        
        # Add description preview
        if job.uniqueDescription:
            description = job.uniqueDescription[:200]
            if len(job.uniqueDescription) > 200:
                description += "..."
            description = self._escape_markdown(description)
            message += f"\n{description}\n"
        
        # Add apply link
        job_url = f"{self.settings.job_site_url}/jobs/{job.slug}"
        message += f"\n👉 [Apply Now]({job_url})"
        
        # Add hashtags
        hashtags = ["\\#Jobs", "\\#Hiring", "\\#FlexiTask"]
        if job.category:
            category_tag = "\\#" + job.category.name.replace(" ", "").replace("&", "And")
            hashtags.insert(1, category_tag)
        if job.workLocationType.value == "REMOTE":
            hashtags.append("\\#RemoteJobs")
        
        message += "\n\n" + " ".join(hashtags)
        
        return message
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for Telegram MarkdownV2"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    async def send_to_channel(self, message: str, parse_mode: str = "MarkdownV2") -> dict:
        """
        Send message to Telegram channel
        
        Args:
            message: The formatted message to send
            parse_mode: Message parse mode (MarkdownV2, HTML, or None)
            
        Returns:
            dict: {"success": bool, "message_id": int} or {"success": False, "error": str}
        """
        
        if not self.is_configured():
            logger.warning("Telegram service not configured")
            return {"success": False, "error": "Telegram service not configured"}
        
        try:
            logger.info(f"Sending message to Telegram channel: {self.channel_id}")
            
            # Determine parse mode
            pm = None
            if parse_mode == "MarkdownV2":
                pm = ParseMode.MARKDOWN_V2
            elif parse_mode == "HTML":
                pm = ParseMode.HTML
            elif parse_mode == "Markdown":
                pm = ParseMode.MARKDOWN
            
            sent_message = await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=pm,
                disable_web_page_preview=False
            )
            
            logger.info(f"Telegram message sent successfully. Message ID: {sent_message.message_id}")
            return {"success": True, "message_id": sent_message.message_id}
        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_photo_with_caption(self, photo_url: str, caption: str) -> dict:
        """
        Send photo with caption to Telegram channel
        
        Args:
            photo_url: URL of the image to send
            caption: Caption text for the image
            
        Returns:
            dict: {"success": bool, "message_id": int} or {"success": False, "error": str}
        """
        if not self.is_configured():
            return {"success": False, "error": "Telegram service not configured"}
        
        try:
            sent_message = await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=photo_url,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            
            logger.info(f"Telegram photo sent successfully. Message ID: {sent_message.message_id}")
            return {"success": True, "message_id": sent_message.message_id}
        
        except Exception as e:
            logger.error(f"Error sending Telegram photo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def post_job(self, job: JobPosting) -> dict:
        """
        Post a job to Telegram channel
        
        If the job has an image, sends as photo with caption.
        Otherwise sends as text message.
        
        Args:
            job: The JobPosting object to post
            
        Returns:
            dict: Result of the post operation
        """
        message = self.format_job_message(job)
        
        if job.jobImageUrl:
            # Convert Cloudinary path to full URL if needed
            image_url = job.jobImageUrl
            if not image_url.startswith(('http://', 'https://')):
                # It's a Cloudinary path, convert to full URL
                image_url = f"https://res.cloudinary.com/dqxfwbv1j/image/upload/{job.jobImageUrl}"
            
            # Send with image
            result = await self.send_photo_with_caption(image_url, message)
            
            # If image fails, try sending as text only
            if not result.get("success"):
                logger.warning(f"Photo failed, sending as text: {result.get('error')}")
                return await self.send_to_channel(message)
            return result
        else:
            # Send text only
            return await self.send_to_channel(message)
    
    async def get_channel_info(self) -> dict:
        """Get Telegram channel information (for testing)"""
        if not self.is_configured():
            return {"error": "Not configured"}
        
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
            return {"error": str(e)}
    
    async def get_bot_info(self) -> dict:
        """Get bot information (for testing)"""
        if not self.is_configured():
            return {"error": "Not configured"}
        
        try:
            me = await self.bot.get_me()
            return {
                "id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "can_join_groups": me.can_join_groups,
                "can_read_all_group_messages": me.can_read_all_group_messages
            }
        
        except Exception as e:
            logger.error(f"Error getting bot info: {str(e)}")
            return {"error": str(e)}
