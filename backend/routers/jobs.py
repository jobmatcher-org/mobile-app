from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.job import JobCreate, JobResponse
from backend.services import crud
from backend.models import job as models  # ✅ Import your Job, Applicant, Resume, JobApplication models

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


@router.post("/apply/{job_id}")
def apply_to_job(
        job_id: int,
        applicant_id: int,
        resume_id: int,
        db: Session = Depends(get_db)
):
    """
    Apply to a specific job with an existing resume.
    """
    # Verify job
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify applicant
    applicant = db.query(models.Applicant).filter(models.Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # Verify resume
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Create application
    job_application = models.JobApplication(
        job_id=job_id,
        applicant_id=applicant_id,
        resume_id=resume_id,
        status="applied"
    )
    db.add(job_application)
    db.commit()
    db.refresh(job_application)

    return {"message": "Applied successfully", "application_id": job_application.id}
