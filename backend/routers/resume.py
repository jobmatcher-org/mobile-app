from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import shutil, os
from pdfminer.high_level import extract_text
from sqlalchemy.exc import SQLAlchemyError

from backend.database import get_db
from backend.models.user import User
from backend.models.resume import Resume
from backend.services.auth import get_current_user
from backend.ai.resume_parser import parse_resume, score_resume

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

def sanitize_obj(obj):
    """
    Recursively sanitizes any object so FastAPI can JSON encode it safely.
    Removes non-UTF8 characters, converts bytes → string, lists → safe lists, etc.
    """

    if obj is None:
        return None

    # If bytes → try decode, else convert to safe ascii
    if isinstance(obj, bytes):
        try:
            return obj.decode("utf-8", errors="ignore")
        except:
            return obj.decode("latin-1", errors="ignore")

    # If string → clean unsafe bytes
    if isinstance(obj, str):
        return obj.encode("utf-8", "ignore").decode("utf-8", "ignore")

    # If list → sanitize all items
    if isinstance(obj, list):
        return [sanitize_obj(i) for i in obj]

    # If dict → sanitize keys + values
    if isinstance(obj, dict):
        return {sanitize_obj(k): sanitize_obj(v) for k, v in obj.items()}

    # Numbers / bool / None → safe
    if isinstance(obj, (int, float, bool)):
        return obj

    # For any unknown object (SQLAlchemy, custom classes, etc.)
    try:
        return str(obj)
    except:
        return None


UPLOAD_DIR = "backend/uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
        file: UploadFile = File(...),
        job_description: str = Form(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # verify user
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # validate extension
    allowed_extensions = [".pdf", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

    # save file safely
    backend_file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(backend_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # extract preview text (use same extractor you have)
    try:
        extracted_text = extract_text(backend_file_path)
    except Exception:
        extracted_text = "⚠️ Preview unavailable"

    # sanitize extracted_text before returning or passing to score
    extracted_text = sanitize_obj(extracted_text)

    # parse resume (parser already returns sanitized dict)
    parsed_data = parse_resume(backend_file_path) or {}
    # ensure parsed_data is sanitized (double-safety)
    parsed_data = sanitize_obj(parsed_data)

    parsed_text = parsed_data.get("text") or ""
    skills = parsed_data.get("skills") or []
    education = parsed_data.get("education") or []
    experience = parsed_data.get("experience") or []

    # update profile fields safely (strings are sanitized)
    try:
        user.biography = parsed_data.get("biography") or user.biography
        user.experience = parsed_data.get("experience_summary") or user.experience
        user.education = parsed_data.get("education_summary") or user.education
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")

    # save resume object (DB model columns accept strings/lists — ensure your model types accept lists)
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

    # return only primitives (strings, lists) — everything sanitized above
    return {
        "message": "✅ Resume uploaded and parsed successfully!",
        "resume_id": new_resume.id,
        "title": new_resume.title,
        "skills": new_resume.skills,
        "education": new_resume.education,
        "experience": new_resume.experience,
        "parsed_preview": extracted_text[:300]
    }


@router.get("/me")
def get_my_resume(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )

    if not resume:
        return {"resume": None}

    return {
        "resume_id": resume.id,
        "title": resume.title,
        "skills": resume.skills,
        "education": resume.education,
        "experience": resume.experience,
        "parsed_preview": resume.parsed_text[:300] if resume.parsed_text else None,
        "file_url": resume.file_url,
    }
