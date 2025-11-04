# backend/schemas/news.py
from pydantic import BaseModel
from typing import Optional

class NewsBase(BaseModel):
    title: str
    image_url: Optional[str] = None
    link: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class NewsResponse(NewsBase):
    id: int

    class Config:
        orm_mode = True
