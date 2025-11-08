# backend/services/crud.py

from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from backend import models, schemas

# ---------------------------
# USERS
# ---------------------------

def get_user_by_email(db: Session, email: EmailStr):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.user.UserCreate, hashed_pw: str):
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw  # match your DB column name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    return db.query(models.User).all()


# ---------------------------
# EMPLOYERS
# ---------------------------

def create_employer(db: Session, employer: schemas.employer.EmployerCreate):
    db_employer = models.Employer(
        user_id=employer.user_id,
        company_name=employer.company_name,
        website=employer.website_url,
        location=employer.location,
        description=employer.description,
        avatar_url=employer.avatar_url,
        banner_image_url=employer.banner_image_url,
        organization_type=employer.organization_type,
        team_size=employer.team_size,
        year_of_establishment=employer.year_of_establishment
    )
    db.add(db_employer)
    db.commit()
    db.refresh(db_employer)
    return db_employer

def get_employers(db: Session):
    return db.query(models.Employer).all()


# ---------------------------
# JOBS
# ---------------------------

def create_job(db: Session, job: schemas.job.JobCreate):
    new_job = models.Job(
        title=job.title,
        description=job.description,
        tags=job.tags,
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        salary_currency=job.salary_currency,
        salary_period=job.salary_period,
        job_types=job.job_types,
        job_level=job.job_level,
        experience=job.experience,
        education=job.education,
        is_active=job.is_active,
        employer_id=job.employer_id
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

def get_jobs(db: Session):
    """Get all active jobs."""
    return db.query(models.Job).filter(models.Job.is_active == True).all()


# ---------------------------
# RESUMES
# ---------------------------

def get_latest_resume(db: Session, user_id: int):
    """Return the latest resume uploaded by the user."""
    return (
        db.query(models.Resume)
        .filter(models.Resume.user_id == user_id)
        .order_by(models.Resume.created_at.desc())
        .first()
    )

def get_resume_score_for_job(db: Session, resume_id: int, job_id: int):
    """Return the ResumeScore for a specific resume-job combination."""
    return (
        db.query(models.ResumeScore)
        .filter(models.ResumeScore.resume_id == resume_id,
                models.ResumeScore.job_id == job_id)
        .first()
    )


# ---------------------------
# JOB RECOMMENDATION / SCORING
# ---------------------------

def get_top_jobs(db: Session, limit: int = 10):
    """Jobs with the most applicants (global)."""
    return (
        db.query(models.Job)
        .filter(models.Job.is_active == True)
        .order_by(models.Job.applicant_count.desc())
        .limit(limit)
        .all()
    )

def get_hot_jobs(db: Session, limit: int = 10, days: int = 7):
    """Recently posted jobs (trending)."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(models.Job)
        .filter(models.Job.is_active == True, models.Job.created_at >= cutoff)
        .order_by(models.Job.created_at.desc())
        .limit(limit)
        .all()
    )

def get_recommended_jobs(db: Session, user_id: int, limit: int = 10):
    """
    Personalized recommended jobs based on latest resume and ResumeScore.
    Returns list of jobs with score descending.
    """
    resume = get_latest_resume(db, user_id)
    if not resume:
        return []

    # Join Jobs with ResumeScore
    results = (
        db.query(models.Job, models.ResumeScore.score)
        .join(models.ResumeScore, models.ResumeScore.job_id == models.Job.id)
        .filter(models.ResumeScore.resume_id == resume.id)
        .order_by(models.ResumeScore.score.desc())
        .limit(limit)
        .all()
    )

    # Return just the jobs (can also return tuple of (Job, score) if needed)
    return [job for job, score in results]


# ---------------------------
# NEWS
# ---------------------------

from backend.models.news import NewsItem
from backend.schemas.news import NewsCreate

def get_all_news(db: Session, skip: int = 0, limit: int = 20):
    return db.query(NewsItem).offset(skip).limit(limit).all()

def create_news(db: Session, news: NewsCreate):
    db_news = NewsItem(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news
