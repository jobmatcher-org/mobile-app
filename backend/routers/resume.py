from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
from pdfminer.high_level import extract_text

from backend.database import get_db
from backend.models.user import Applicant
from backend.models.job import Resume
from backend.services.auth import get_current_user  # your auth dependency
from backend.models.user import User  # logged-in user model

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

UPLOAD_DIR = "backend/uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_resume(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # fetch logged-in user
):
    """
    Upload a resume for the logged-in user.
    """
    try:
        # 1️⃣ Save file to backend/uploads/resumes
        backend_file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(backend_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2️⃣ Extract text (optional preview)
        extracted_text = extract_text(backend_file_path)

        # 3️⃣ Fetch Applicant record
        applicant = db.query(Applicant).filter(Applicant.user_id == current_user.id).first()
        if not applicant:
            applicant = Applicant(
                user_id=current_user.id,
                biography="",
                education="",
                location=""
            )
            db.add(applicant)
            db.commit()
            db.refresh(applicant)


    # 4️⃣ Create Resume record
        new_resume = Resume(
            applicant_id=applicant.id,
            title=file.filename,
            file_url=f"/uploads/resumes/{file.filename}",
            file_size=os.path.getsize(backend_file_path),
            file_path=backend_file_path
        )

        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)

        # 5️⃣ Return response
        return {
            "message": "✅ Resume uploaded successfully!",
            "resume_id": new_resume.id,
            "title": new_resume.title,
            "file_size": new_resume.file_size,
            "parsed_preview": extracted_text[:300]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume upload failed: {e}")
