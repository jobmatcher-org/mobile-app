from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    email_verified_at = Column(DateTime)

    # Profile fields (moved from Applicant)
    biography = Column(Text)
    date_of_birth = Column(Date)
    nationality = Column(String(50))
    marital_status = Column(String(20))
    gender = Column(String(10))
    education = Column(String(100))
    website_url = Column(String(255))
    location = Column(String(255))
    experience = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user")
    #resume_scores = relationship("ResumeScore", back_populates="user")
    employer = relationship("Employer", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")
    applicants = relationship("Applicant", back_populates="user")  # created when applying


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_agent = Column(String(255))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="sessions")
