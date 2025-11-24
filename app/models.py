from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class JobPosting(BaseModel):
    """Job posting data model"""
    job_id: str
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    posted_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "12345",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "Remote",
                "description": "We are looking for an experienced Python developer...",
                "salary": "$100,000 - $150,000",
                "job_type": "Full-time"
            }
        }


class PostResponse(BaseModel):
    """Response model for job posting"""
    success: bool
    message: str
    job_id: str
    platforms: dict[str, bool]  # Status for each platform
