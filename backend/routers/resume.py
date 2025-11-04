# backend/routers/resume.py

from fastapi import (
    APIRouter, UploadFile, File, Depends, HTTPException, status
)
from sqlalchemy.orm import Session
import shutil
import os
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from backend.database import get_db
from backend.models.user import Applicant, User
from backend.models.job import Resume
from backend.services.auth import get_current_user
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# 🧠 Import AI parser
from backend.ai.resume_parser import parse_resume

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

UPLOAD_DIR = "backend/uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------------------
# 🔹 Helper: Get or create applicant
# ---------------------------
def get_or_create_applicant(db: Session, user_id: int):
    """Return existing applicant or create one if missing."""
    applicant = db.query(Applicant).filter(Applicant.user_id == user_id).first()
    if applicant:
        return applicant

    try:
        applicant = Applicant(user_id=user_id)
        db.add(applicant)
        db.commit()
        db.refresh(applicant)
        return applicant
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Applicant creation failed: Integrity error.")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ---------------------------
# 🔹 Main: Resume Upload Endpoint
# ---------------------------
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Upload a resume for the logged-in user.
    Validates file type, saves file, parses text, and records in DB.
    """
    # 1️⃣ Validate extension
    allowed_extensions = [".pdf", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {ext}. Allowed: {', '.join(allowed_extensions)}"
        )

    # 2️⃣ Save to disk
    backend_file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(backend_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # 3️⃣ Extract text for preview
    try:
        extracted_text = extract_text(backend_file_path)
    except PDFSyntaxError:
        extracted_text = "⚠️ Could not read PDF (corrupted or encrypted)."
    except Exception as e:
        extracted_text = f"⚠️ Text extraction failed: {str(e)}"

    # 4️⃣ Create or fetch applicant
    applicant = get_or_create_applicant(db, current_user.id)

    # 5️⃣ Create Resume record (initial)
    try:
        new_resume = Resume(
            applicant_id=applicant.id,
            title=file.filename,
            file_url=f"/uploads/resumes/{file.filename}",
            file_size=os.path.getsize(backend_file_path),
            file_path=backend_file_path,
            ai_status="pending"
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 6️⃣ Parse resume using our custom parser
    parsed_data = parse_resume(backend_file_path)

    # 7️⃣ Save parsed data if available
    if parsed_data:
        new_resume.parsed_text = parsed_data.get("text")
        new_resume.skills = parsed_data.get("skills")
        new_resume.education = parsed_data.get("education")
        new_resume.ai_status = "parsed"
        db.commit()
        db.refresh(new_resume)

    # 8️⃣ Final response
    return {
        "message": "✅ Resume uploaded and parsed successfully!",
        "resume_id": new_resume.id,
        "title": new_resume.title,
        "file_size": new_resume.file_size,
        "parsed_preview": extracted_text[:300],
        "parsed_data": parsed_data or {}
    }
