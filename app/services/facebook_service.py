import httpx
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)


class FacebookService:
    """
    Facebook service for posting to groups
    Uses Facebook Graph API
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.access_token = self.settings.facebook_access_token
        self.group_id = self.settings.facebook_group_id
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    def is_configured(self) -> bool:
        """Check if Facebook service is configured"""
        return bool(self.access_token and self.group_id)
    
    async def post_to_group(self, message: str) -> dict:
        """
        Post message to Facebook group
        Message should already contain the apply link.
        
        Requirements:
        1. Create a Facebook App at developers.facebook.com
        2. Get a Page Access Token or User Access Token
        3. Grant necessary permissions: publish_to_groups, groups_access_member_info
        4. Get the Group ID from the group URL
        
        API Documentation:
        https://developers.facebook.com/docs/graph-api/reference/group/feed
        
        Returns:
            dict: {"success": bool, "post_id": str} or {"success": False, "error": str}
        """
        
        if not self.is_configured():
            logger.warning("Facebook service not configured")
            return {"success": False, "error": "Facebook service not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                # Prepare the post data
                post_data = {
                    "message": message,
                    "access_token": self.access_token
                }
                
                # Post to Facebook group feed
                url = f"{self.base_url}/{self.group_id}/feed"
                
                logger.info(f"Posting to Facebook group: {self.group_id}")
                
                response = await client.post(url, data=post_data)
                
                if response.status_code == 200:
                    result = response.json()
                    post_id = result.get('id', 'unknown')
                    logger.info(f"Facebook post successful. Post ID: {post_id}")
                    return {"success": True, "post_id": post_id}
                else:
                    error_msg = response.text
                    logger.error(f"Facebook API error: {response.status_code} - {error_msg}")
                    return {"success": False, "error": f"API error: {error_msg}"}
        
        except Exception as e:
            logger.error(f"Error posting to Facebook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_group_info(self) -> dict:
        """Get Facebook group information (for testing)"""
        if not self.is_configured():
            return {}
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/{self.group_id}"
                params = {
                    "access_token": self.access_token,
                    "fields": "name,description,member_count"
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                return {}
        
        except Exception as e:
            logger.error(f"Error getting group info: {str(e)}")
            return {}
