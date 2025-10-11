from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ------------------------------
# Job Schemas
# ------------------------------
class JobBase(BaseModel):
    title: str
    description: str
    tags: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    job_types: Optional[str] = None
    job_level: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    is_active: Optional[bool] = True

class JobCreate(JobBase):
    employer_id: int

class JobResponse(JobBase):
    id: int
    employer_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# ------------------------------
# Job Application Schemas
# ------------------------------
class JobApplicationBase(BaseModel):
    cover_letter: Optional[str] = None
    resume_id: Optional[int] = None
    bookmarked: Optional[bool] = False
    status: Optional[str] = "applied"
    notes: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    job_id: int
    applicant_id: int

class JobApplicationResponse(JobApplicationBase):
    id: int
    job_id: int
    applicant_id: int
    applied_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# ------------------------------
# Saved Job Schemas
# ------------------------------
class SavedJobBase(BaseModel):
    notes: Optional[str] = None

class SavedJobCreate(SavedJobBase):
    job_id: int
    applicant_id: int

class SavedJobResponse(SavedJobBase):
    id: int
    job_id: int
    applicant_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# ------------------------------
# Resume Schemas
# ------------------------------
class ResumeBase(BaseModel):
    title: str
    file_url: str
    file_size: Optional[int] = None
    is_primary: Optional[bool] = False

class ResumeCreate(ResumeBase):
    applicant_id: int
    application_id: Optional[int] = None

class ResumeResponse(ResumeBase):
    id: int
    applicant_id: int
    application_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
