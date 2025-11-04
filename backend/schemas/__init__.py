# backend/schemas/__init__.py
from .user import UserCreate, UserResponse
from .job import JobCreate, JobResponse, JobApplicationCreate
from .employer import EmployerResponse, EmployerCreate
from .applicant import ApplicantCreate, ApplicantResponse
from .news import NewsCreate, NewsResponse
