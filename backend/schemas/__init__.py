# backend/schemas/__init__.py

# User
from .user import UserCreate, UserResponse, UserLogin

# Applicant
from .applicant import ApplicantCreate, ApplicantResponse

# Employer
from .employer import EmployerCreate, EmployerResponse

# Job
from .job import (
    JobCreate,
    JobResponse,
    JobApplicationCreate,
    JobApplicationResponse,
    SavedJobCreate,
    SavedJobResponse,
    ResumeCreate,
    ResumeResponse
)

# News
from .news import NewsCreate, NewsResponse
