from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmployerBase(BaseModel):
    company_name: str
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

    model_config = {"from_attributes": True}
