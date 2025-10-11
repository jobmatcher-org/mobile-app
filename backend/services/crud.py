from sqlalchemy.orm import Session
from backend import models, schemas


# ---------------------------
# USERS
# ---------------------------
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.user.UserCreate):
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password  # You can later hash this using passlib
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


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
