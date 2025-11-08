from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100))
    file_url = Column(String(255))
    file_path = Column(String(255))
    file_size = Column(Integer)

    # AI/parsed fields
    parsed_text = Column(Text)
    skills = Column(JSON)
    education = Column(JSON)
    experience = Column(JSON)
    ai_status = Column(String(50), default="pending")  # pending / parsed / scored / failed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
    applications = relationship("JobApplication", back_populates="resume")
    scores = relationship("ResumeScore", viewonly=True, overlaps="resume_scores")# keeps link to ResumeScore table
