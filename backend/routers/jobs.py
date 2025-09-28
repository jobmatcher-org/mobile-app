from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.job import JobCreate, JobResponse
from ..services import crud
from typing import List

router = APIRouter()

@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    return crud.create_job(db, job, user_id=1)  # Hardcoded user for now

@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return crud.get_jobs(db)
