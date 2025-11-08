from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.job import Job
from backend.models.resume_score import ResumeScore
from backend.models.resume import Resume
from backend.models.user import User
from backend.models.applicant import Applicant
from backend.schemas.job import JobResponse

router = APIRouter(prefix="/best-jobs", tags=["Best Jobs"])

# -----------------------------
# ✅ Top Jobs (global, highest engagement)
# -----------------------------
@router.get("/top", response_model=List[JobResponse])
def get_top_jobs(db: Session = Depends(get_db)):
    jobs = (
        db.query(Job)
        .filter(Job.is_active == True)
        .order_by(Job.applicant_count.desc())
        .limit(10)
        .all()
    )
    if not jobs:
        raise HTTPException(status_code=404, detail="No top jobs found")
    return jobs


# -----------------------------
# ✅ Hot Jobs (personalized, highest score for user)
# -----------------------------
@router.get("/hot", response_model=List[JobResponse])
def get_hot_jobs(current_user: User = Depends(), db: Session = Depends(get_db)):
    # Get the user's latest resume
    user_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    if not user_resume:
        raise HTTPException(status_code=404, detail="No resume found for user")

    # Fetch jobs sorted by ResumeScore for this resume
    hot_jobs = (
        db.query(Job, ResumeScore.score)
        .join(ResumeScore, ResumeScore.job_id == Job.id)
        .filter(ResumeScore.resume_id == user_resume.id)
        .order_by(ResumeScore.score.desc())
        .limit(10)
        .all()
    )

    if not hot_jobs:
        raise HTTPException(status_code=404, detail="No hot jobs found")

    # Return Job objects only
    return [job for job, score in hot_jobs]


# -----------------------------
# ✅ Recommended Jobs (matching skills)
# -----------------------------
@router.get("/recommended/{applicant_id}", response_model=List[JobResponse])
def get_recommended_jobs(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # Get latest resume
    if not applicant.resumes:
        raise HTTPException(status_code=404, detail="Applicant has no resumes")

    resume = applicant.resumes[-1]  # latest resume uploaded
    skills = resume.skills or []

    # Match jobs containing at least one matching skill
    # Note: Assuming `Job.required_skills` is JSON/array field (PostgreSQL)
    jobs = (
        db.query(Job)
        .filter(Job.is_active == True)
        .filter(Job.required_skills.overlap(skills))
        .all()
    )

    return jobs
