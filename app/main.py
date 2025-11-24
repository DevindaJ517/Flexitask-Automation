from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.models import JobPosting, PostResponse
from app.config import get_settings
from app.services.whatsapp_service import WhatsAppService
from app.services.facebook_service import FacebookService
from app.services.telegram_service import TelegramService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Job Posting Social Media Automation",
    description="Microservice for automatically posting jobs to social media platforms",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get settings
settings = get_settings()

# Initialize services
whatsapp_service = WhatsAppService()
facebook_service = FacebookService()
telegram_service = TelegramService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Flexitask Social Media Automation",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "whatsapp": whatsapp_service.is_configured(),
            "facebook": facebook_service.is_configured(),
            "telegram": telegram_service.is_configured()
        }
    }


@app.post("/api/preview-message")
async def preview_message(job: JobPosting):
    """
    Preview what the formatted message will look like
    Useful for testing message format without posting
    """
    try:
        message = format_job_message(job)
        return {
            "success": True,
            "formatted_message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def post_to_platforms(job: JobPosting):
    """Post job to all social media platforms with brief summary and link"""
    
    # Format brief message with key details and apply link
    message = format_job_message(job)
    
    results = {}
    
    # Post to WhatsApp
    try:
        whatsapp_result = await whatsapp_service.send_message(message)
        results["whatsapp"] = whatsapp_result
        logger.info(f"WhatsApp post successful for job: {job.title}")
    except Exception as e:
        logger.error(f"WhatsApp post failed for job {job.title}: {str(e)}")
        results["whatsapp"] = {"success": False, "error": str(e)}
    
    # Post to Facebook
    try:
        facebook_result = await facebook_service.post_to_group(message)
        results["facebook"] = facebook_result
        logger.info(f"Facebook post successful for job: {job.title}")
    except Exception as e:
        logger.error(f"Facebook post failed for job {job.title}: {str(e)}")
        results["facebook"] = {"success": False, "error": str(e)}
    
    # Post to Telegram
    try:
        telegram_result = await telegram_service.send_to_channel(message)
        results["telegram"] = telegram_result
        logger.info(f"Telegram post successful for job: {job.title}")
    except Exception as e:
        logger.error(f"Telegram post failed for job {job.title}: {str(e)}")
        results["telegram"] = {"success": False, "error": str(e)}
    
    return results


def format_job_message(job: JobPosting) -> str:
    """Format brief job posting message with key details and apply link"""
    
    # Map employment types to readable format
    employment_map = {
        "FULL_TIME": "Full Time",
        "PART_TIME": "Part Time",
        "CONTRACT": "Contract"
    }
    
    work_location_map = {
        "ONSITE": "Onsite",
        "REMOTE": "Remote",
        "HYBRID": "Hybrid"
    }
    
    experience_map = {
        "ONE_PLUS": "1+ years",
        "TWO_PLUS": "2+ years",
        "FIVE_PLUS": "5+ years"
    }
    
    # Build message with emojis and brief info
    message = f"🎯 **New Job Opportunity!**\n\n"
    message += f"**{job.title}**\n"
    message += f"🏢 {job.companyName}\n\n"
    
    # Location info
    if job.city and job.country:
        message += f"📍 {job.city}, {job.country}\n"
    elif job.country:
        message += f"📍 {job.country}\n"
    
    # Employment details
    employment = employment_map.get(job.employmentType, job.employmentType)
    work_type = work_location_map.get(job.workLocationType, job.workLocationType)
    message += f"💼 {employment} | {work_type}\n"
    
    # Category
    if job.category:
        message += f"🏷️ {job.category}\n"
    
    # Experience requirement
    if job.experienceYears:
        experience = experience_map.get(job.experienceYears, job.experienceYears)
        message += f"📊 Experience: {experience}\n"
    
    # Internship badge
    if job.isInternship:
        message += f"🎓 Internship Position\n"
    
    # Apply link
    message += f"\n🔗 **Apply now:** {job.linkedInApplyURL}"
    
    return message


@app.post("/api/post-job", response_model=PostResponse)
async def post_job(job: JobPosting):
    """
    Main endpoint to post job to all social media platforms
    
    This endpoint receives job posting data and automatically posts it to:
    - WhatsApp groups
    - Facebook groups
    - Telegram channels
    
    Only brief summary with key details and apply link is shared.
    """
    try:
        logger.info(f"Received job posting request: {job.title} at {job.companyName}")
        
        # Post to platforms synchronously to get results
        results = await post_to_platforms(job)
        
        # Check if at least one platform succeeded
        success = any(
            r.get("success", False) if isinstance(r, dict) else r 
            for r in results.values()
        )
        
        return PostResponse(
            success=success,
            message="Job posted successfully to all platforms" if success else "Failed to post to some platforms",
            results=results
        )
    
    except Exception as e:
        logger.error(f"Error processing job posting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
