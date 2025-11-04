from pydantic import EmailStr
from backend import models, schemas
from sqlalchemy.orm import Session
from backend.models.news import NewsItem
from backend.schemas.news import NewsCreate
# ---------------------------
# USERS
# ---------------------------
def get_user_by_email(db: Session, email: EmailStr):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.user.UserCreate, hashed_pw: str):
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw  # ✅ match your DB column name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(models.User).all()

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
    return db.query(models.Job).filter(models.Job.is_active == True).all()

def create_employer(db: Session, employer: schemas.employer.EmployerCreate):
    db_employer = models.Employer(
        user_id=employer.user_id,
        company_name=employer.company_name,
        website=employer.website_url,  # <- keep Pydantic field name
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

def get_all_news(db: Session, skip: int = 0, limit: int = 20):
    return db.query(NewsItem).offset(skip).limit(limit).all()

def create_news(db: Session, news: NewsCreate):
    db_news = NewsItem(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news