"""
FlexiTask Automation Server

FastAPI application for monitoring FlexiTask job postings and
automatically sharing them to Telegram.

Features:
- Real-time job monitoring via Supabase
- Automatic posting to Telegram channel
- Background scheduling with APScheduler (free tier compatible)
- REST API for manual control and monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, timezone
import logging

from app.models import JobPosting, PostResponse, JobMonitorStatus
from app.config import get_settings
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService
from app.scheduler import start_scheduler, stop_scheduler, get_scheduler_status, check_and_share_new_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize services
supabase_service = SupabaseService()
telegram_service = TelegramService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown"""
    # Startup
    logger.info("Starting FlexiTask Automation Server...")
    logger.info(f"Job site URL: {settings.job_site_url}")
    logger.info(f"Polling interval: {settings.polling_interval_seconds} seconds")
    
    # Log service status
    logger.info(f"Supabase configured: {supabase_service.is_configured()}")
    logger.info(f"Telegram configured: {telegram_service.is_configured()}")
    
    # Start the background scheduler
    if supabase_service.is_configured() and telegram_service.is_configured():
        start_scheduler()
        logger.info("Background scheduler started")
    else:
        logger.warning("Scheduler not started - services not configured")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FlexiTask Automation Server...")
    stop_scheduler()
    await supabase_service.close()


# Initialize FastAPI app
app = FastAPI(
    title="FlexiTask Automation",
    description="""
    Automation service for monitoring FlexiTask job postings and 
    sharing them to Telegram.
    
    ## Features
    - 🔍 Monitors Supabase database for new job posts
    - 📱 Posts to Telegram channel
    - ⚡ Background scheduling with APScheduler
    - 📊 Tracking and statistics
    """,
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= Health Check Endpoints =============

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with service info"""
    return {
        "service": "FlexiTask Automation",
        "version": "2.0.0",
        "status": "running",
        "job_site": settings.job_site_url
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check for all services"""
    stats = await supabase_service.get_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "supabase": {
                "configured": supabase_service.is_configured(),
                "stats": stats
            },
            "telegram": {
                "configured": telegram_service.is_configured()
            }
        },
        "configuration": {
            "polling_interval": settings.polling_interval_seconds,
            "job_site_url": settings.job_site_url
        }
    }


# ============= Job Monitoring Endpoints =============

@app.get("/api/jobs/new", tags=["Jobs"])
async def get_new_jobs(
    hours: int = Query(default=24, description="Look back period in hours")
):
    """
    Get list of new jobs that haven't been shared yet
    
    Returns jobs created in the last N hours that haven't been posted
    to Telegram.
    """
    if not supabase_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Supabase service not configured"
        )
    
    from datetime import timedelta
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    jobs = await supabase_service.get_new_published_jobs(since=since)
    
    return {
        "count": len(jobs),
        "since": since.isoformat(),
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "company": job.companyName,
                "slug": job.slug,
                "created_at": job.createdAt.isoformat() if job.createdAt else None
            }
            for job in jobs
        ]
    }


@app.get("/api/jobs/{job_id}", tags=["Jobs"])
async def get_job(job_id: str):
    """Get details of a specific job"""
    if not supabase_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Supabase service not configured"
        )
    
    job = await supabase_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    # Get sharing info
    shared_info = await supabase_service.get_shared_job_info(job_id)
    
    return {
        "job": job.model_dump(),
        "shared": shared_info
    }


@app.get("/api/jobs/shared/recent", tags=["Jobs"])
async def get_recently_shared_jobs(
    limit: int = Query(default=50, le=100, description="Maximum number of jobs to return")
):
    """Get list of recently shared jobs"""
    jobs = await supabase_service.get_recently_shared_jobs(limit=limit)
    
    return {
        "count": len(jobs),
        "jobs": jobs
    }


# ============= Manual Posting Endpoints =============

# ============= Scheduler Endpoints =============

@app.get("/api/scheduler/status", tags=["Scheduler"])
async def scheduler_status():
    """Get current scheduler status"""
    return get_scheduler_status()


@app.post("/api/scheduler/trigger", tags=["Scheduler"])
async def trigger_manual_check():
    """
    Manually trigger a job check
    
    This runs the job check immediately, outside of the schedule.
    """
    result = await check_and_share_new_jobs()
    return result


@app.post("/api/share/{job_id}", response_model=PostResponse, tags=["Sharing"])
async def share_job(job_id: str):
    """
    Manually trigger sharing for a specific job to Telegram
    
    Use this to manually share a job to Telegram.
    """
    if not supabase_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Supabase service not configured"
        )
    
    # Fetch job
    job = await supabase_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    if not job.isPublished:
        raise HTTPException(
            status_code=400,
            detail="Cannot share unpublished job"
        )
    
    # Share to Telegram
    result = await post_to_telegram(job)
    
    # Mark as shared
    success = result.get("success", False)
    
    if success:
        await supabase_service.mark_job_as_shared(
            job_id=job.id,
            telegram_shared=True,
            telegram_message_id=result.get("message_id")
        )
    
    return PostResponse(
        success=success,
        message="Job shared to Telegram successfully" if success else "Failed to share job",
        results={"telegram": result}
    )


@app.post("/api/share/trigger-check", tags=["Sharing"])
async def trigger_job_check(background_tasks: BackgroundTasks):
    """
    Manually trigger a check for new jobs
    
    This will check for new jobs and share them in the background.
    Useful for testing or forcing an immediate check.
    """
    background_tasks.add_task(check_and_share_jobs_background)
    
    return {
        "message": "Job check triggered",
        "status": "processing"
    }


async def check_and_share_jobs_background():
    """Background task to check and share new jobs"""
    try:
        from datetime import timedelta
        
        last_check = await supabase_service.get_last_check_timestamp()
        if last_check is None:
            last_check = datetime.now(timezone.utc) - timedelta(hours=24)
        
        jobs = await supabase_service.get_new_published_jobs(since=last_check)
        
        for job in jobs:
            result = await post_to_telegram(job)
            if result.get("success"):
                await supabase_service.mark_job_as_shared(
                    job_id=job.id,
                    telegram_shared=True,
                    telegram_message_id=result.get("message_id")
                )
        
        await supabase_service.set_last_check_timestamp()
        
        logger.info(f"Background check completed. Processed {len(jobs)} jobs.")
        
    except Exception as e:
        logger.error(f"Error in background job check: {e}")


async def post_to_telegram(job: JobPosting) -> dict:
    """Post job to Telegram"""
    
    if not telegram_service.is_configured():
        return {"success": False, "error": "Telegram not configured"}
    
    try:
        result = await telegram_service.post_job(job)
        logger.info(f"Telegram post {'successful' if result.get('success') else 'failed'} for: {job.title}")
        return result
    except Exception as e:
        logger.error(f"Telegram post failed for {job.title}: {str(e)}")
        return {"success": False, "error": str(e)}


# ============= Preview Endpoints =============

@app.post("/api/preview/telegram", tags=["Preview"])
async def preview_telegram_message(job_id: str):
    """Preview what the Telegram message will look like"""
    job = await supabase_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    message = telegram_service.format_job_message(job)
    
    return {
        "platform": "telegram",
        "job_id": job_id,
        "formatted_message": message
    }


# ============= Statistics Endpoints =============

@app.get("/api/stats", tags=["Statistics"])
async def get_statistics():
    """Get sharing statistics"""
    stats = await supabase_service.get_stats()
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
