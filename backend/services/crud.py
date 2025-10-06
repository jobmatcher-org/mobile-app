from sqlalchemy.orm import Session
from ..models import User, Job
from ..schemas.user import UserCreate
from ..schemas.job import JobCreate
from ..services.auth import hash_password

# Users
def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role=getattr(user, "role", "jobseeker")
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Jobs
def create_job(db: Session, job: JobCreate, user_id: int):
    db_job = Job(title=job.title, description=job.description, owner_id=user_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs(db: Session):
    return db.query(Job).all()
