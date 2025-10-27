from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ApplicantBase(BaseModel):
    biography: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None

class ApplicantCreate(ApplicantBase):
    user_id: int

class ApplicantResponse(ApplicantBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
