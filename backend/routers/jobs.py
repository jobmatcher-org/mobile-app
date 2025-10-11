from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.job import JobCreate, JobResponse
from backend.services import crud

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """
    Create a new job post by an employer.
    """
    created_job = crud.create_job(db=db, job=job)
    if not created_job:
        raise HTTPException(status_code=400, detail="Failed to create job")
    return created_job


@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    """
    Get all active job posts.
    """
    return crud.get_jobs(db)
