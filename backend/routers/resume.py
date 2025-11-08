from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import shutil, os
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from sqlalchemy.exc import SQLAlchemyError

from backend.database import get_db
from backend.models.user import User
from backend.models.applicant import Applicant
from backend.models.resume import Resume
from backend.services.auth import get_current_user
from backend.ai.resume_parser import parse_resume, score_resume

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

UPLOAD_DIR = "backend/uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
        file: UploadFile = File(...),
        job_description: str = Form(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1) Validate file extension
    allowed_extensions = [".pdf", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

    # 2) Save uploaded file
    backend_file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(backend_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except:
        raise HTTPException(status_code=500, detail="Failed to save file")

    # 3) Extract preview text (best effort)
    try:
        extracted_text = extract_text(backend_file_path)
    except:
        extracted_text = "⚠️ Preview unavailable"

    # 4) Parse resume using your AI parser
    parsed_data = parse_resume(backend_file_path) or {}
    parsed_text = parsed_data.get("text") or ""

    skills = parsed_data.get("skills") or []
    education = parsed_data.get("education") or []
    experience = parsed_data.get("experience") or []

    # 6) Update USER profile fields (not applicant)
    try:
        user.biography = parsed_data.get("biography") or user.biography
        user.experience = parsed_data.get("experience_summary") or user.experience
        user.education = parsed_data.get("education_summary") or user.education

        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")

    # 7) Save Resume linked to USER
    try:
        new_resume = Resume(
            user_id=user.id,
            title=file.filename,
            file_url=f"/uploads/resumes/{file.filename}",
            file_path=backend_file_path,
            file_size=os.path.getsize(backend_file_path),
            parsed_text=parsed_text,
            skills=skills,
            education=education,
            experience=experience,
            ai_status="parsed"
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save resume: {str(e)}")

    return {
        "message": "✅ Resume uploaded and parsed successfully!",
        "resume_id": new_resume.id,
        "title": new_resume.title,
        "skills": new_resume.skills,
        "education": new_resume.education,
        "experience": new_resume.experience,
        "parsed_preview": extracted_text[:300]
    }

