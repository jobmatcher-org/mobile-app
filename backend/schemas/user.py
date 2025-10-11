from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

# ------------------------------
# Base User Schemas
# ------------------------------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    model_config = {
        "from_attributes": True
    }

# ------------------------------
# Session Schemas
# ------------------------------
class SessionBase(BaseModel):
    user_agent: Optional[str] = None
    expires_at: Optional[datetime] = None

class SessionResponse(SessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

# ------------------------------
# Applicant Schemas
# ------------------------------
class ApplicantBase(BaseModel):
    biography: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    website_url: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[str] = None

class ApplicantCreate(ApplicantBase):
    user_id: int

class ApplicantResponse(ApplicantBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

# ------------------------------
# Employer Schemas
# ------------------------------
class EmployerBase(BaseModel):
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    organization_type: Optional[str] = None
    team_size: Optional[str] = None
    year_of_establishment: Optional[str] = None
    website_url: Optional[str] = None
    location: Optional[str] = None

class EmployerCreate(EmployerBase):
    user_id: int

class EmployerResponse(EmployerBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
