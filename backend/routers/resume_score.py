from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.job import Job
from backend.models.resume_score import ResumeScore
from backend.schemas.job import JobResponse

router = APIRouter(prefix="/resume-scores", tags=["Resume Scores"])

@router.get("/hot/{user_id}", response_model=List[JobResponse])
def get_hot_jobs(user_id: int, db: Session = Depends(get_db)):
    # Find latest resume
    user_resume = db.query(ResumeScore).join(Job).filter(ResumeScore.user_id == user_id).first()
    if not user_resume:
        raise HTTPException(status_code=404, detail="No resume score found")

    hot_jobs = (
        db.query(Job, ResumeScore.score)
        .join(ResumeScore, ResumeScore.job_id == Job.id)
        .filter(ResumeScore.resume_id == user_resume.id)
        .order_by(ResumeScore.score.desc())
        .limit(10)
        .all()
    )
    return [job for job, score in hot_jobs]
