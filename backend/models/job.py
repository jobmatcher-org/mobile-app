from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    Boolean,
    DateTime,
    Text
)
from sqlalchemy.dialects.mysql import JSON

from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=False)
    tags = Column(String(255))
    min_salary = Column(Float)
    max_salary = Column(Float)
    salary_currency = Column(String(10))
    salary_period = Column(String(50))
    job_types = Column(String(50))
    job_level = Column(String(50))
    experience = Column(String(50))
    education = Column(String(100))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=False)

    # Relationships
    employer = relationship("Employer", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job")
    saved_jobs = relationship("SavedJob", back_populates="job")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    cover_letter = Column(Text)
    bookmarked = Column(Boolean, default=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="applied")
    notes = Column(Text)
    deleted_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="applications")
    applicant = relationship("Applicant", back_populates="applications")
    resume = relationship("Resume", back_populates="applications", foreign_keys=[resume_id])


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="saved_jobs")
    applicant = relationship("Applicant", back_populates="saved_jobs")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    title = Column(String(100))
    file_url = Column(String(255))
    file_size = Column(Integer)
    file_path=Column(String(255))

    # New fields
    parsed_text = Column(Text)  # store full parsed text from the resume
    skills = Column(JSON)       # store extracted skills (could be JSON or comma-separated)
    education = Column(JSON)    # extracted education details
    experience = Column(JSON)   # extracted experience details
    score = Column(Float)       # AI evaluation score (0–100 or similar)
    ai_status = Column(String(50), default="pending")  # parsed / scored / failed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applicant = relationship("Applicant", back_populates="resumes")
    applications = relationship("JobApplication", back_populates="resume")