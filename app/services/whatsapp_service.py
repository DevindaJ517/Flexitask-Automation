import httpx
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    WhatsApp service for sending messages to groups
    
    This uses Twilio API as an example. You can also use:
    - WhatsApp Business API
    - Other third-party APIs like 360Dialog, MessageBird, etc.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.account_sid = self.settings.twilio_account_sid
        self.auth_token = self.settings.twilio_auth_token
        self.whatsapp_from = self.settings.twilio_whatsapp_from
        self.whatsapp_to = self.settings.whatsapp_group_number
    
    def is_configured(self) -> bool:
        """Check if WhatsApp service is configured"""
        return bool(self.account_sid and self.auth_token and self.whatsapp_from and self.whatsapp_to)
    
    async def send_message(self, message: str) -> dict:
        """
        Send message to WhatsApp group
        Message should already contain the apply link.
        
        NOTE: This uses Twilio API. You need to configure:
        - Get account SID and auth token from Twilio Console
        - Use WhatsApp-enabled Twilio number (sandbox or approved)
        - API: https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json
        
        Returns:
            dict: {"success": bool, "message_sid": str} or {"success": False, "error": str}
        """
        
        if not self.is_configured():
            logger.warning("WhatsApp service not configured")
            return {"success": False, "error": "WhatsApp service not configured"}
        
        try:
            # Using Twilio API
            async with httpx.AsyncClient() as client:
                logger.info(f"Sending WhatsApp message to: {self.whatsapp_to}")
                
                # Twilio API endpoint
                url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
                
                response = await client.post(
                    url,
                    auth=(self.account_sid, self.auth_token),
                    data={
                        "From": self.whatsapp_from,
                        "To": self.whatsapp_to,
                        "Body": message
                    }
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    message_sid = result.get("sid", "unknown")
                    logger.info(f"WhatsApp message sent successfully. SID: {message_sid}")
                    return {"success": True, "message_sid": message_sid}
                else:
                    error_msg = response.text
                    logger.error(f"WhatsApp API error: {response.status_code} - {error_msg}")
                    return {"success": False, "error": f"API error: {error_msg}"}
        
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {"success": False, "error": str(e)}
