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
    # Validate extension
    allowed_extensions = [".pdf", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {ext}. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save to disk
    backend_file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(backend_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # Extract text
    try:
        extracted_text = extract_text(backend_file_path)
    except PDFSyntaxError:
        extracted_text = "⚠️ Could not read PDF (corrupted or encrypted)."
    except Exception as e:
        extracted_text = f"⚠️ Text extraction failed: {str(e)}"

    # Create or fetch applicant
    applicant = get_or_create_applicant(db, current_user.id)

    # Insert Resume record
    try:
        new_resume = Resume(
            applicant_id=applicant.id,
            title=file.filename,
            file_url=f"/uploads/resumes/{file.filename}",
            file_size=os.path.getsize(backend_file_path),
            file_path=backend_file_path,
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Final response
    return {
        "message": "✅ Resume uploaded successfully!",
        "resume_id": new_resume.id,
        "title": new_resume.title,
        "file_size": new_resume.file_size,
        "parsed_preview": extracted_text[:300],
    }
