"""
GitHub Actions runner script for job monitoring.
This script is called by the GitHub Actions workflow.
"""

import asyncio
import sys
import os
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    # Log environment variables (without sensitive values)
    print("=" * 60)
    print("Environment Check:")
    print(f"  SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Not set'}")
    print(f"  SUPABASE_KEY: {'✅ Set' if os.getenv('SUPABASE_KEY') else '❌ Not set'}")
    print(f"  TELEGRAM_BOT_TOKEN: {'✅ Set' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Not set'}")
    print(f"  TELEGRAM_CHANNEL_ID: {os.getenv('TELEGRAM_CHANNEL_ID', '❌ Not set')}")
    print(f"  REDIS_URL: {'✅ Set' if os.getenv('REDIS_URL') else '❌ Not set'}")
    print("=" * 60)
    
    from app.services.supabase_service import SupabaseService
    from app.services.telegram_service import TelegramService
    
    # Check services
    supabase_service = SupabaseService()
    telegram_service = TelegramService()
    
    print(f"\nService Status:")
    print(f"  Supabase configured: {supabase_service.is_configured()}")
    print(f"  Telegram configured: {telegram_service.is_configured()}")
    
    if not supabase_service.is_configured():
        print("❌ Supabase not configured! Check SUPABASE_URL and SUPABASE_KEY")
        sys.exit(1)
    
    if not telegram_service.is_configured():
        print("❌ Telegram not configured! Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID")
        sys.exit(1)
    
    # Get jobs from last 7 days to start
    from datetime import datetime, timezone, timedelta
    since = datetime.now(timezone.utc) - timedelta(days=7)
    
    print(f"\nFetching jobs created since: {since.isoformat()}")
    
    jobs = await supabase_service.get_new_published_jobs(since=since)
    
    print(f"Found {len(jobs)} unshared jobs")
    
    if not jobs:
        print("No new jobs to share. This could mean:")
        print("  1. No published jobs in the database in the last 7 days")
        print("  2. All jobs have already been shared (tracked in Redis)")
        
        # Let's check if there are ANY jobs
        print("\nChecking for any published jobs...")
        all_jobs = await supabase_service.get_new_published_jobs(since=datetime.now(timezone.utc) - timedelta(days=365))
        print(f"Total published jobs in last year: {len(all_jobs)}")
        
        await supabase_service.close()
        return
    
    # Try to share the first job as a test
    print(f"\nSharing jobs to Telegram...")
    
    for job in jobs[:5]:  # Share up to 5 jobs
        print(f"\n  Job: {job.title}")
        print(f"  Company: {job.companyName}")
        print(f"  Slug: {job.slug}")
        
        try:
            result = await telegram_service.post_job(job)
            print(f"  Result: {result}")
            
            if result.get("success"):
                await supabase_service.mark_job_as_shared(
                    job_id=job.id,
                    telegram_shared=True,
                    telegram_message_id=result.get("message_id")
                )
                print(f"  ✅ Shared successfully!")
            else:
                print(f"  ❌ Failed: {result.get('error')}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    await supabase_service.close()
    print("\n✅ Job check completed!")


if __name__ == "__main__":
    asyncio.run(main())
