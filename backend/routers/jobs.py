from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Job, Employer, Resume
from backend.schemas import JobCreate, JobResponse
from backend.services.auth import get_current_user
from backend.ai.resume_parser import score_resume
import json

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# -----------------------
# GET all jobs
# -----------------------
@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    jobs = db.query(Job).filter(Job.is_active == True).all()

    response = []
    for job in jobs:
        response.append(JobResponse(
            id=job.id,
            employer_id=job.employer_id,
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
            required_skills=json.loads(job.required_skills or "[]"),  # ✅ convert here
            created_at=job.created_at,
            updated_at=job.updated_at
        ))

    return response

# -----------------------
# POST a new job (Employer only)
# -----------------------
@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
        job_in: JobCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=403, detail="Only employers can create jobs.")

    job = Job(
        title=job_in.title,
        description=job_in.description,
        tags=job_in.tags,
        min_salary=job_in.min_salary,
        max_salary=job_in.max_salary,
        salary_currency=job_in.salary_currency,
        salary_period=job_in.salary_period,
        job_types=job_in.job_types,
        job_level=job_in.job_level,
        experience=job_in.experience,
        education=job_in.education,
        required_skills=json.dumps(job_in.required_skills or []),
        is_active=job_in.is_active,
        employer_id=employer.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# -----------------------
# Search jobs & score
# -----------------------
@router.get("/search", response_model=List[dict])
def search_jobs(
        query: Optional[str] = Query(None, description="Search keyword for job title or description"),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )

    if not resume:
        raise HTTPException(status_code=400, detail="Upload a resume first to enable job recommendations.")

    # Convert stored JSON fields
    user_skills = json.loads(resume.skills or "[]")
    user_experience = json.loads(resume.experience or "[]")
    user_education = json.loads(resume.education or "[]")

    user_profile = {
        "skills": user_skills,
        "experience": user_experience,
        "education": user_education,
    }

    jobs_query = db.query(Job).filter(Job.is_active == True)
    if query:
        jobs_query = jobs_query.filter(Job.title.ilike(f"%{query}%"))

    jobs = jobs_query.all()

    scored_jobs = []
    for job in jobs:
        try:
            job_score = score_resume(user_profile, job.description)
        except:
            job_score = 0.0
        scored_jobs.append({"job": job, "score": float(job_score)})

    scored_jobs.sort(key=lambda x: x["score"], reverse=True)

    # Return clean response with safe list fields
    return [
        {
            "id": item["job"].id,
            "title": item["job"].title,
            "company": item["job"].employer.company_name if item["job"].employer else None,
            "location": item["job"].employer.location if item["job"].employer else None,
            "description": item["job"].description,
            "score": round(item["score"], 2)
        }
        for item in scored_jobs
    ]
