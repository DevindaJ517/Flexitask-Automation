"""
Supabase Service for FlexiTask Job Monitoring

This service connects to the FlexiTask Supabase database to:
1. Monitor new job postings
2. Track which jobs have been shared to social media
3. Fetch job details with related data (category, country, city)
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
import redis.asyncio as redis
import json
import logging

from app.config import get_settings
from app.models import JobPosting, JobCategory, Country, City, SharedJob

logger = logging.getLogger(__name__)


class SupabaseService:
    """
    Service for interacting with FlexiTask Supabase database
    
    Uses Supabase client for database queries and Redis for tracking
    shared jobs to avoid duplicate posts.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase: Optional[Client] = None
        self.redis: Optional[redis.Redis] = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Supabase and Redis clients"""
        # Initialize Supabase client
        if self.settings.supabase_url and self.settings.supabase_key:
            try:
                self.supabase = create_client(
                    self.settings.supabase_url,
                    self.settings.supabase_key
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
    
    async def _get_redis(self) -> redis.Redis:
        """Get Redis connection (lazy initialization)"""
        if self.redis is None:
            self.redis = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis
    
    def is_configured(self) -> bool:
        """Check if Supabase service is properly configured"""
        return self.supabase is not None
    
    async def get_new_published_jobs(self, since: Optional[datetime] = None) -> List[JobPosting]:
        """
        Fetch new published jobs from FlexiTask database
        
        Args:
            since: Only fetch jobs created after this timestamp
            
        Returns:
            List of JobPosting objects that haven't been shared yet
        """
        if not self.is_configured():
            logger.warning("Supabase service not configured")
            return []
        
        try:
            # Build query for published jobs
            query = self.supabase.table("job_posts").select(
                "*,"
                "job_categories:categoryId(id, name, slug),"
                "countries:countryId(id, name, code),"
                "cities:cityId(id, name, countryId)"
            ).eq("isPublished", True)
            
            # Filter by creation date if specified
            if since:
                query = query.gte("createdAt", since.isoformat())
            
            # Order by creation date, newest first
            query = query.order("createdAt", desc=True)
            
            response = query.execute()
            
            if not response.data:
                return []
            
            jobs = []
            for job_data in response.data:
                try:
                    # Check if job has already been shared
                    if await self._is_job_shared(job_data["id"]):
                        continue
                    
                    # Parse related data
                    category = None
                    if job_data.get("job_categories"):
                        category = JobCategory(**job_data["job_categories"])
                    
                    country = None
                    if job_data.get("countries"):
                        country = Country(**job_data["countries"])
                    
                    city = None
                    if job_data.get("cities"):
                        city = City(**job_data["cities"])
                    
                    # Create JobPosting object
                    job = JobPosting(
                        id=job_data["id"],
                        title=job_data["title"],
                        slug=job_data["slug"],
                        companyName=job_data["companyName"],
                        employmentType=job_data["employmentType"],
                        workLocationType=job_data["workLocationType"],
                        isInternship=job_data.get("isInternship", False),
                        categoryId=job_data.get("categoryId"),
                        countryId=job_data.get("countryId"),
                        cityId=job_data.get("cityId"),
                        uniqueDescription=job_data.get("uniqueDescription"),
                        linkedInApplyURL=job_data["linkedInApplyURL"],
                        isPublished=job_data["isPublished"],
                        jobImageUrl=job_data.get("jobImageUrl"),
                        experienceYears=job_data.get("experienceYears"),
                        createdAt=datetime.fromisoformat(job_data["createdAt"].replace("Z", "+00:00")) if job_data.get("createdAt") else None,
                        updatedAt=datetime.fromisoformat(job_data["updatedAt"].replace("Z", "+00:00")) if job_data.get("updatedAt") else None,
                        category=category,
                        country=country,
                        city=city
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.error(f"Error parsing job {job_data.get('id')}: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} new jobs to share")
            return jobs
            
        except Exception as e:
            logger.error(f"Error fetching jobs from Supabase: {e}")
            return []
    
    async def get_job_by_id(self, job_id: str) -> Optional[JobPosting]:
        """Fetch a specific job by ID"""
        if not self.is_configured():
            return None
        
        try:
            response = self.supabase.table("job_posts").select(
                "*,"
                "job_categories:categoryId(id, name, slug),"
                "countries:countryId(id, name, code),"
                "cities:cityId(id, name, countryId)"
            ).eq("id", job_id).single().execute()
            
            if not response.data:
                return None
            
            job_data = response.data
            
            # Parse related data
            category = None
            if job_data.get("job_categories"):
                category = JobCategory(**job_data["job_categories"])
            
            country = None
            if job_data.get("countries"):
                country = Country(**job_data["countries"])
            
            city = None
            if job_data.get("cities"):
                city = City(**job_data["cities"])
            
            return JobPosting(
                id=job_data["id"],
                title=job_data["title"],
                slug=job_data["slug"],
                companyName=job_data["companyName"],
                employmentType=job_data["employmentType"],
                workLocationType=job_data["workLocationType"],
                isInternship=job_data.get("isInternship", False),
                categoryId=job_data.get("categoryId"),
                countryId=job_data.get("countryId"),
                cityId=job_data.get("cityId"),
                uniqueDescription=job_data.get("uniqueDescription"),
                linkedInApplyURL=job_data["linkedInApplyURL"],
                isPublished=job_data["isPublished"],
                jobImageUrl=job_data.get("jobImageUrl"),
                experienceYears=job_data.get("experienceYears"),
                createdAt=datetime.fromisoformat(job_data["createdAt"].replace("Z", "+00:00")) if job_data.get("createdAt") else None,
                updatedAt=datetime.fromisoformat(job_data["updatedAt"].replace("Z", "+00:00")) if job_data.get("updatedAt") else None,
                category=category,
                country=country,
                city=city
            )
            
        except Exception as e:
            logger.error(f"Error fetching job {job_id}: {e}")
            return None
    
    async def _is_job_shared(self, job_id: str) -> bool:
        """Check if a job has already been shared (using Redis)"""
        try:
            redis_client = await self._get_redis()
            return await redis_client.exists(f"shared_job:{job_id}") > 0
        except Exception as e:
            logger.error(f"Redis error checking shared job: {e}")
            return False
    
    async def mark_job_as_shared(
        self,
        job_id: str,
        telegram_shared: bool = False,
        telegram_message_id: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Mark a job as shared in Redis
        
        Stores sharing metadata with a TTL of 30 days to prevent
        re-sharing the same job.
        """
        try:
            redis_client = await self._get_redis()
            
            shared_data = {
                "job_id": job_id,
                "shared_at": datetime.now(timezone.utc).isoformat(),
                "telegram_shared": telegram_shared,
                "telegram_message_id": telegram_message_id,
                "error_message": error_message
            }
            
            # Store in Redis with 30-day TTL
            await redis_client.setex(
                f"shared_job:{job_id}",
                60 * 60 * 24 * 30,  # 30 days
                json.dumps(shared_data)
            )
            
            # Also maintain a sorted set for tracking order
            await redis_client.zadd(
                "shared_jobs_timeline",
                {job_id: datetime.now(timezone.utc).timestamp()}
            )
            
            logger.info(f"Marked job {job_id} as shared")
            return True
            
        except Exception as e:
            logger.error(f"Error marking job as shared: {e}")
            return False
    
    async def get_shared_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get sharing information for a specific job"""
        try:
            redis_client = await self._get_redis()
            data = await redis_client.get(f"shared_job:{job_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting shared job info: {e}")
            return None
    
    async def get_recently_shared_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of recently shared jobs"""
        try:
            redis_client = await self._get_redis()
            
            # Get most recent job IDs from sorted set
            job_ids = await redis_client.zrevrange("shared_jobs_timeline", 0, limit - 1)
            
            jobs = []
            for job_id in job_ids:
                info = await self.get_shared_job_info(job_id)
                if info:
                    jobs.append(info)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting recently shared jobs: {e}")
            return []
    
    async def get_last_check_timestamp(self) -> Optional[datetime]:
        """Get the timestamp of the last job check"""
        try:
            redis_client = await self._get_redis()
            timestamp = await redis_client.get("last_job_check_timestamp")
            if timestamp:
                return datetime.fromisoformat(timestamp)
            return None
        except Exception as e:
            logger.error(f"Error getting last check timestamp: {e}")
            return None
    
    async def set_last_check_timestamp(self, timestamp: Optional[datetime] = None) -> bool:
        """Set the timestamp of the last job check"""
        try:
            redis_client = await self._get_redis()
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
            await redis_client.set("last_job_check_timestamp", timestamp.isoformat())
            return True
        except Exception as e:
            logger.error(f"Error setting last check timestamp: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get sharing statistics"""
        try:
            redis_client = await self._get_redis()
            
            # Count total shared jobs
            total_shared = await redis_client.zcard("shared_jobs_timeline")
            
            # Get last check timestamp
            last_check = await self.get_last_check_timestamp()
            
            return {
                "total_jobs_shared": total_shared,
                "last_check": last_check.isoformat() if last_check else None,
                "supabase_connected": self.is_configured()
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_jobs_shared": 0,
                "last_check": None,
                "supabase_connected": self.is_configured(),
                "error": str(e)
            }
    
    async def delete_old_jobs(self, days: int = 30) -> Dict[str, Any]:
        """
        Delete jobs older than specified days from the database
        
        Args:
            days: Number of days after which jobs should be deleted (default: 30)
            
        Returns:
            Dict with deletion results including count of deleted jobs
        """
        if not self.is_configured():
            logger.warning("Supabase service not configured")
            return {"success": False, "error": "Supabase not configured", "deleted_count": 0}
        
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # First, get the count of jobs to be deleted
            count_response = self.supabase.table("job_posts").select(
                "id", count="exact"
            ).lt("createdAt", cutoff_date.isoformat()).execute()
            
            jobs_to_delete = count_response.count if count_response.count else 0
            
            if jobs_to_delete == 0:
                logger.info(f"No jobs older than {days} days found")
                return {"success": True, "deleted_count": 0, "message": "No old jobs to delete"}
            
            # Delete jobs older than cutoff date
            delete_response = self.supabase.table("job_posts").delete().lt(
                "createdAt", cutoff_date.isoformat()
            ).execute()
            
            deleted_count = len(delete_response.data) if delete_response.data else jobs_to_delete
            
            logger.info(f"Deleted {deleted_count} jobs older than {days} days")
            
            # Also clean up Redis entries for deleted jobs
            if delete_response.data:
                redis_client = await self._get_redis()
                for job in delete_response.data:
                    job_id = job.get("id")
                    if job_id:
                        await redis_client.delete(f"shared_job:{job_id}")
                        await redis_client.zrem("shared_jobs_timeline", job_id)
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_date.isoformat(),
                "message": f"Successfully deleted {deleted_count} jobs older than {days} days"
            }
            
        except Exception as e:
            logger.error(f"Error deleting old jobs: {e}")
            return {"success": False, "error": str(e), "deleted_count": 0}

    async def close(self):
        """Close connections"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
