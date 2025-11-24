from pydantic import BaseModel, HttpUrl
from typing import Optional


class JobPosting(BaseModel):
    """Job posting data model with minimal info for social media sharing"""
    title: str
    companyName: str
    workLocationType: str  # ONSITE, REMOTE, HYBRID
    employmentType: str  # FULL_TIME, PART_TIME, CONTRACT
    linkedInApplyURL: str
    
    # Optional fields
    category: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    experienceYears: Optional[str] = None  # ONE_PLUS, TWO_PLUS, FIVE_PLUS
    isInternship: Optional[bool] = False
    uniqueDescription: Optional[str] = None
    jobImage: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Software Engineer",
                "companyName": "TechCorp Inc.",
                "workLocationType": "HYBRID",
                "employmentType": "FULL_TIME",
                "category": "IT & Software",
                "country": "United States",
                "city": "San Francisco",
                "experienceYears": "TWO_PLUS",
                "isInternship": False,
                "linkedInApplyURL": "https://www.linkedin.com/jobs/view/123456789"
            }
        }


class PostResponse(BaseModel):
    """Response model for job posting"""
    success: bool
    message: str
    results: dict  # Detailed results for each platform
