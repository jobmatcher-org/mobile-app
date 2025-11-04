# backend/models/news.py
from sqlalchemy import Column, Integer, String, Text
from backend.database import Base

class NewsItem(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    image_url = Column(String(500), nullable=True)
    link = Column(String(500), nullable=True)  # optional link to full article
    category = Column(String(50), nullable=True)  # e.g., Tech, Career, Job
    description = Column(Text, nullable=True)
