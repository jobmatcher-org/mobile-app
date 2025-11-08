from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String(100))
    description = Column(Text)
    avatar_url = Column(String(255))
    banner_image_url = Column(String(255))
    organization_type = Column(String(100))
    team_size = Column(String(50))
    year_of_establishment = Column(String(10))
    website = Column(String(255))
    location = Column(String(255))
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="employer")
    jobs = relationship("Job", back_populates="employer")
