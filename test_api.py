#!/usr/bin/env python3
"""
Test script for the Social Media Automation Service
"""

import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://localhost:8000"

# Test job data
test_job = {
    "job_id": "TEST-12345",
    "title": "Senior Python Developer",
    "company": "Tech Innovation Ltd",
    "location": "Remote / Hybrid",
    "description": "We are looking for an experienced Python developer to join our growing team. Must have 5+ years of experience with Python, FastAPI, and cloud technologies.",
    "salary": "$100,000 - $150,000",
    "job_type": "Full-time",
    "posted_at": datetime.now().isoformat()
}


def test_health():
    """Test health endpoint"""
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")


def test_post_job_async():
    """Test async job posting"""
    print("\n2. Testing Async Job Posting...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/post-job",
            json=test_job,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")


def test_post_job_sync():
    """Test sync job posting"""
    print("\n3. Testing Sync Job Posting...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/post-job-sync",
            json=test_job,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")


def main():
    print("=" * 60)
    print("Social Media Automation Service - Test Script")
    print("=" * 60)
    
    # Run tests
    test_health()
    test_post_job_async()
    test_post_job_sync()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
