from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.job import JobCreate, JobResponse, JobApplicationCreate
from backend.models import Job, JobApplication, SavedJob, Resume, Applicant
from backend.services import crud

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# -----------------------------
# Create a new job
# -----------------------------
@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    created_job = crud.create_job(db=db, job=job)
    if not created_job:
        raise HTTPException(status_code=400, detail="Failed to create job")
    return created_job

# -----------------------------
# Get all active jobs
# -----------------------------
@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return crud.get_jobs(db)

# -----------------------------
# Apply to a job using JSON body
# -----------------------------
@router.post("/apply")
def apply_to_job(
        body: JobApplicationCreate = Body(...),
        db: Session = Depends(get_db)
):
    job_id = body.job_id
    applicant_id = body.applicant_id
    resume_id = body.resume_id

    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify applicant exists
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # Verify resume exists
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Create job application
    job_application = JobApplication(
        job_id=job_id,
        applicant_id=applicant_id,
        resume_id=resume_id,
        status="applied"
    )
    db.add(job_application)
    db.commit()
    db.refresh(job_application)

    return {"message": "Applied successfully", "application_id": job_application.id}
