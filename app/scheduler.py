"""
APScheduler for FlexiTask Automation

Replaces Celery for simpler deployment on free cloud platforms.
Runs the job check task on a configurable interval.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService
from app.models import JobPosting

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

settings = get_settings()


async def check_and_share_new_jobs() -> Dict[str, Any]:
    """
    Main task: Check for new published jobs and share them to Telegram
    
    This task runs periodically to:
    1. Query Supabase for new published jobs
    2. Filter out already shared jobs
    3. Share each new job to Telegram
    4. Track shared jobs in Redis
    """
    logger.info("Starting scheduled job check...")
    
    supabase_service = SupabaseService()
    telegram_service = TelegramService()
    
    if not supabase_service.is_configured():
        logger.error("Supabase service not configured")
        return {"success": False, "error": "Supabase not configured"}
    
    if not telegram_service.is_configured():
        logger.error("Telegram service not configured")
        return {"success": False, "error": "Telegram not configured"}
    
    try:
        # Get last check timestamp
        last_check = await supabase_service.get_last_check_timestamp()
        
        # If no last check, look back 24 hours
        if last_check is None:
            last_check = datetime.now(timezone.utc) - timedelta(hours=24)
        
        logger.info(f"Checking for jobs since: {last_check.isoformat()}")
        
        # Fetch new published jobs
        new_jobs = await supabase_service.get_new_published_jobs(since=last_check)
        
        if not new_jobs:
            logger.info("No new jobs to share")
            await supabase_service.set_last_check_timestamp()
            await supabase_service.close()
            return {"success": True, "jobs_processed": 0, "message": "No new jobs"}
        
        logger.info(f"Found {len(new_jobs)} new jobs to share")
        
        # Process each job
        results = []
        for job in new_jobs:
            try:
                result = await share_job_to_telegram(job, telegram_service, supabase_service)
                results.append({
                    "job_id": job.id,
                    "title": job.title,
                    **result
                })
            except Exception as e:
                logger.error(f"Error sharing job {job.id}: {e}")
                results.append({
                    "job_id": job.id,
                    "title": job.title,
                    "success": False,
                    "error": str(e)
                })
        
        # Update last check timestamp
        await supabase_service.set_last_check_timestamp()
        
        successful = sum(1 for r in results if r.get("success", False))
        logger.info(f"Job check completed. Shared {successful}/{len(new_jobs)} jobs.")
        
        return {
            "success": True,
            "jobs_processed": len(new_jobs),
            "jobs_shared": successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in check_and_share_new_jobs: {e}")
        return {"success": False, "error": str(e)}
    finally:
        await supabase_service.close()


async def share_job_to_telegram(
    job: JobPosting,
    telegram_service: TelegramService,
    supabase_service: SupabaseService
) -> Dict[str, Any]:
    """Share a single job to Telegram"""
    
    try:
        result = await telegram_service.post_job(job)
        
        # Mark job as shared
        await supabase_service.mark_job_as_shared(
            job_id=job.id,
            telegram_shared=result.get("success", False),
            telegram_message_id=result.get("message_id"),
            error_message=None if result.get("success") else result.get("error")
        )
        
        return {
            "success": result.get("success", False),
            "telegram": result
        }
        
    except Exception as e:
        logger.error(f"Error sharing job {job.id}: {e}")
        return {"success": False, "error": str(e)}


def start_scheduler():
    """Start the background scheduler"""
    if scheduler.running:
        logger.info("Scheduler already running")
        return
    
    # Add the job check task
    scheduler.add_job(
        check_and_share_new_jobs,
        trigger=IntervalTrigger(seconds=settings.polling_interval_seconds),
        id="check_new_jobs",
        name="Check for new jobs and share to Telegram",
        replace_existing=True,
        max_instances=1  # Prevent overlapping runs
    )
    
    scheduler.start()
    logger.info(f"Scheduler started. Checking for new jobs every {settings.polling_interval_seconds} seconds.")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def get_scheduler_status() -> Dict[str, Any]:
    """Get current scheduler status"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        })
    
    return {
        "running": scheduler.running,
        "jobs": jobs
    }
