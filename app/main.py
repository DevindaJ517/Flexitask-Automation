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
        "status": "online",
        "service": "Job Posting Automation",
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


async def post_to_platforms(job: JobPosting):
    """Post job to all social media platforms"""
    
    # Generate job URL
    job_url = f"{settings.job_site_url}/jobs/{job.job_id}"
    
    # Format message
    message = format_job_message(job, job_url)
    
    results = {}
    
    # Post to WhatsApp
    try:
        whatsapp_result = await whatsapp_service.send_message(message, job_url)
        results["whatsapp"] = whatsapp_result
        logger.info(f"WhatsApp post successful for job {job.job_id}")
    except Exception as e:
        logger.error(f"WhatsApp post failed for job {job.job_id}: {str(e)}")
        results["whatsapp"] = False
    
    # Post to Facebook
    try:
        facebook_result = await facebook_service.post_to_group(message, job_url)
        results["facebook"] = facebook_result
        logger.info(f"Facebook post successful for job {job.job_id}")
    except Exception as e:
        logger.error(f"Facebook post failed for job {job.job_id}: {str(e)}")
        results["facebook"] = False
    
    # Post to Telegram
    try:
        telegram_result = await telegram_service.send_to_channel(message, job_url)
        results["telegram"] = telegram_result
        logger.info(f"Telegram post successful for job {job.job_id}")
    except Exception as e:
        logger.error(f"Telegram post failed for job {job.job_id}: {str(e)}")
        results["telegram"] = False
    
    return results


def format_job_message(job: JobPosting, job_url: str) -> str:
    """Format job posting message"""
    message = f"""
🔔 New Job Alert! 🔔

📋 Position: {job.title}
🏢 Company: {job.company}
📍 Location: {job.location}
"""
    
    if job.job_type:
        message += f"⏰ Type: {job.job_type}\n"
    
    if job.salary:
        message += f"💰 Salary: {job.salary}\n"
    
    message += f"\n📝 Description:\n{job.description[:200]}{'...' if len(job.description) > 200 else ''}\n"
    message += f"\n🔗 Apply Now: {job_url}"
    
    return message


@app.post("/api/post-job", response_model=PostResponse)
async def post_job(job: JobPosting, background_tasks: BackgroundTasks):
    """
    Main endpoint to post job to all social media platforms
    
    This endpoint receives job posting data and automatically posts it to:
    - WhatsApp groups
    - Facebook groups
    - Telegram channels
    """
    try:
        logger.info(f"Received job posting request for job ID: {job.job_id}")
        
        # Post to platforms in background
        background_tasks.add_task(post_to_platforms, job)
        
        return PostResponse(
            success=True,
            message="Job posting is being distributed to social media platforms",
            job_id=job.job_id,
            platforms={
                "whatsapp": True,
                "facebook": True,
                "telegram": True
            }
        )
    
    except Exception as e:
        logger.error(f"Error processing job posting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/post-job-sync", response_model=PostResponse)
async def post_job_sync(job: JobPosting):
    """
    Synchronous endpoint to post job to all social media platforms
    Waits for all platforms to complete before responding
    """
    try:
        logger.info(f"Received sync job posting request for job ID: {job.job_id}")
        
        # Post to platforms synchronously
        results = await post_to_platforms(job)
        
        success = any(results.values())
        
        return PostResponse(
            success=success,
            message="Job posted to social media platforms" if success else "Failed to post to any platform",
            job_id=job.job_id,
            platforms=results
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
