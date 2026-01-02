from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EmploymentType(str, Enum):
    """Employment type enum matching FlexiTask database"""
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"


class WorkLocationType(str, Enum):
    """Work location type enum matching FlexiTask database"""
    ONSITE = "ONSITE"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"


class ExperienceYears(str, Enum):
    """Experience years enum matching FlexiTask database"""
    ONE_PLUS = "ONE_PLUS"
    TWO_PLUS = "TWO_PLUS"
    FIVE_PLUS = "FIVE_PLUS"


class JobCategory(BaseModel):
    """Job category from FlexiTask database"""
    id: str
    name: str
    slug: str


class Country(BaseModel):
    """Country from FlexiTask database"""
    id: str
    name: str
    code: Optional[str] = None


class City(BaseModel):
    """City from FlexiTask database"""
    id: str
    name: str
    countryId: Optional[str] = None


class JobPosting(BaseModel):
    """Job posting data model matching FlexiTask database structure"""
    id: str
    title: str
    slug: str
    companyName: str
    employmentType: EmploymentType
    workLocationType: WorkLocationType
    isInternship: bool = False
    categoryId: Optional[str] = None
    countryId: Optional[str] = None
    cityId: Optional[str] = None
    uniqueDescription: Optional[str] = None
    linkedInApplyURL: str
    isPublished: bool = True
    jobImageUrl: Optional[str] = None
    experienceYears: Optional[ExperienceYears] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    # Related data (populated from joins)
    category: Optional[JobCategory] = None
    country: Optional[Country] = None
    city: Optional[City] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "clx1234567890",
                "title": "Senior Software Engineer",
                "slug": "senior-software-engineer-techcorp",
                "companyName": "TechCorp Inc.",
                "employmentType": "FULL_TIME",
                "workLocationType": "HYBRID",
                "isInternship": False,
                "uniqueDescription": "We are looking for a talented engineer...",
                "linkedInApplyURL": "https://www.linkedin.com/jobs/view/123456789",
                "isPublished": True,
                "experienceYears": "TWO_PLUS"
            }
        }


class SharedJob(BaseModel):
    """Model to track which jobs have been shared to Telegram"""
    job_id: str
    shared_at: datetime
    telegram_shared: bool = False
    telegram_message_id: Optional[int] = None
    error_message: Optional[str] = None


class PostResponse(BaseModel):
    """Response model for job posting"""
    success: bool
    message: str
    results: dict  # Detailed results for each platform


class PlatformResult(BaseModel):
    """Result from posting to Telegram"""
    success: bool
    platform: str = "telegram"
    message_id: Optional[int] = None
    error: Optional[str] = None


class JobMonitorStatus(BaseModel):
    """Status of the job monitoring service"""
    is_running: bool
    last_check: Optional[datetime] = None
    jobs_processed: int = 0
    last_job_id: Optional[str] = None
    errors: List[str] = []
