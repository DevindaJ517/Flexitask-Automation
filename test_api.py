#!/usr/bin/env python3
"""
Test script for the Social Media Automation Service
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

# Test job data matching frontend form structure
test_job_full = {
    "title": "Senior Software Engineer",
    "companyName": "TechCorp Inc.",
    "workLocationType": "HYBRID",
    "employmentType": "FULL_TIME",
    "category": "IT & Software",
    "country": "United States",
    "city": "San Francisco",
    "experienceYears": "TWO_PLUS",
    "isInternship": False,
    "linkedInApplyURL": "https://www.linkedin.com/jobs/view/123456789",
    "uniqueDescription": "We are looking for an experienced software engineer to join our team. Must have strong Python and JavaScript skills.",
    "jobImage": None
}

test_job_minimal = {
    "title": "Full Stack Developer",
    "companyName": "StartupXYZ",
    "workLocationType": "REMOTE",
    "employmentType": "FULL_TIME",
    "linkedInApplyURL": "https://www.linkedin.com/jobs/view/987654321"
}


def test_root():
    """Test root endpoint"""
    print("\n1. Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_health():
    """Test health endpoint"""
    print("\n2. Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_post_job_full():
    """Test job posting with all fields"""
    print("\n3. Testing Job Posting (Full Details)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/post-job",
            json=test_job_full,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_post_job_minimal():
    """Test job posting with minimal required fields"""
    print("\n4. Testing Job Posting (Minimal Fields)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/post-job",
            json=test_job_minimal,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    print("=" * 70)
    print("Flexitask Social Media Automation - Test Script")
    print("=" * 70)
    
    # Run tests
    test_root()
    test_health()
    test_post_job_full()
    test_post_job_minimal()
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    print("\nNote: Check service logs to see if messages were sent:")
    print("  docker-compose logs -f")


if __name__ == "__main__":
    main()
