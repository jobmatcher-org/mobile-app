from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import shutil, os, json
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from backend.database import get_db
from backend.models.user import Applicant, User
from backend.models.job import Resume
from backend.services.auth import get_current_user
from sqlalchemy.exc import SQLAlchemyError
from backend.ai.resume_parser import parse_resume, score_resume

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

UPLOAD_DIR = "backend/uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------
# Helper: Get or create applicant
# ---------------------------
def get_or_create_applicant(db: Session, user_id: int):
    applicant = db.query(Applicant).filter(Applicant.user_id == user_id).first()
    if applicant:
        return applicant
    try:
        applicant = Applicant(user_id=user_id)
        db.add(applicant)
        db.commit()
        db.refresh(applicant)
        return applicant
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ---------------------------
# Main: Upload Resume
# ---------------------------
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
        file: UploadFile = File(...),
        job_description: str = Form(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 1️⃣ Validate file extension
    allowed_extensions = [".pdf", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

    # 2️⃣ Save uploaded file
    backend_file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(backend_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # 3️⃣ Extract text preview for frontend display
    try:
        extracted_text = extract_text(backend_file_path)
    except PDFSyntaxError:
        extracted_text = "⚠️ Could not read PDF (corrupted or encrypted)."
    except Exception as e:
        extracted_text = f"⚠️ Text extraction failed: {str(e)}"

    # 4️⃣ Get or create applicant
    applicant = get_or_create_applicant(db, current_user.id)

    # 5️⃣ Parse resume
    parsed_data = parse_resume(backend_file_path) or {}
    parsed_text = parsed_data.get("text") or ""

    # 6️⃣ Score resume
    try:
        ai_score = float(score_resume(parsed_data, job_description)) if job_description else 0.0
    except Exception as e:
        ai_score = 0.0
        print(f"⚠️ AI scoring failed: {e}")

    # 7️⃣ Prepare JSON fields for DB
    skills = json.dumps(parsed_data.get("skills") or [])
    education = json.dumps(parsed_data.get("education") or [])
    experience = json.dumps(parsed_data.get("experience") or [])

    # 8️⃣ Create Resume record and commit
    try:
        new_resume = Resume(
            applicant_id=applicant.id,
            title=file.filename,
            file_url=f"/uploads/resumes/{file.filename}",
            file_size=os.path.getsize(backend_file_path),
            file_path=backend_file_path,
            parsed_text=parsed_text,
            skills=skills,
            education=education,
            experience=experience,
            score=ai_score,
            ai_status="parsed"
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save resume: {str(e)}")

    # 9️⃣ Return all parsed fields in response
    return {
        "message": "✅ Resume uploaded and parsed successfully!",
        "resume_id": new_resume.id,
        "title": new_resume.title,
        "file_url": new_resume.file_url,
        "file_size": new_resume.file_size,
        "file_path": new_resume.file_path,
        "parsed_text": new_resume.parsed_text,
        "skills": json.loads(new_resume.skills),
        "education": json.loads(new_resume.education),
        "experience": json.loads(new_resume.experience),
        "score": new_resume.score,
        "ai_status": new_resume.ai_status,
        "created_at": new_resume.created_at,
        "updated_at": new_resume.updated_at,
        "parsed_preview": extracted_text[:300]
    }
