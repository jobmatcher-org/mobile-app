import os
from pdfminer.high_level import extract_text
from backend.database import SessionLocal
from backend.models.job import Resume

# 1️⃣ Create DB session
db = SessionLocal()

# 2️⃣ Dynamically get path to the resume file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(BASE_DIR, "uploads", "resumes", "test_resume.pdf")

# 3️⃣ Check file
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

# 4️⃣ Extract text
extracted_text = extract_text(pdf_path)

# 5️⃣ Save to DB
resume = Resume(
    applicant_id=1,
    file_path="uploads/resumes/test_resume.pdf"
)


db.add(resume)
db.commit()
db.refresh(resume)

# 6️⃣ Output results
print(f"✅ Resume saved with ID: {resume.id}")
print(f"Extracted Text (first 500 chars):\n{extracted_text[:500]}")
