"""
GitHub Actions runner script for job monitoring.
This script is called by the GitHub Actions workflow.
"""

import asyncio
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scheduler import check_and_share_new_jobs


async def main():
    print("Starting job check...")
    result = await check_and_share_new_jobs()
    print(f"Result: {result}")
    
    if result.get("success"):
        print(f"✅ Jobs processed: {result.get('jobs_processed', 0)}")
        print(f"✅ Jobs shared: {result.get('jobs_shared', 0)}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
