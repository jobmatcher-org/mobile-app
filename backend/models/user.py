from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, DateTime, Text
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applicant = relationship("Applicant", back_populates="user", uselist=False)
    employer = relationship("Employer", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")


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


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    biography = Column(Text)  # Use Text for long biography text
    date_of_birth = Column(Date)
    nationality = Column(String(50))
    marital_status = Column(String(20))
    gender = Column(String(10))
    education = Column(String(100))
    website_url = Column(String(255))
    location = Column(String(255))
    experience = Column(String(255))
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applicant")
    resumes = relationship("Resume", back_populates="applicant")
    applications = relationship("JobApplication", back_populates="applicant")
    saved_jobs = relationship("SavedJob", back_populates="applicant")


class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String(100))  # renamed from name
    description = Column(Text)
    avatar_url = Column(String(255))
    banner_image_url = Column(String(255))
    organization_type = Column(String(100))
    team_size = Column(String(50))
    year_of_establishment = Column(String(10))
    website = Column(String(255))  # renamed from website_url
    location = Column(String(255))
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="employer")
    jobs = relationship("Job", back_populates="employer")
