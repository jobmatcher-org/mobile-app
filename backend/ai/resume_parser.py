# backend/ai/resume_parser.py

import os
import re
from pdfminer.high_level import extract_text

def parse_resume(file_path: str):
    """
    Extract text from PDF/DOCX and parse basic info like:
    - name
    - email
    - phone
    - skills
    - education
    """

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    # 1️⃣ Extract text
    try:
        text = extract_text(file_path)
    except Exception as e:
        print(f"❌ Could not extract text: {e}")
        return None

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # 2️⃣ Extract email
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    email = emails[0] if emails else None

    # 3️⃣ Extract phone number
    phones = re.findall(r"\+?\d[\d\s-]{7,}\d", text)
    phone = phones[0] if phones else None

    # 4️⃣ Extract skills (example list, can expand)
    skill_keywords = [
        "Python", "Java", "Kotlin", "SQL", "Firebase",
        "Android", "JavaScript", "React", "Machine Learning",
        "Data Analysis", "HTML", "CSS", "FastAPI"
    ]
    skills_found = [skill for skill in skill_keywords if skill.lower() in text.lower()]

    # 5️⃣ Extract education (simple keywords)
    education_keywords = ["B\.?Sc", "M\.?Sc", "Bachelor", "Master", "High School", "Engineering", "Diploma"]
    education_found = [edu for edu in education_keywords if edu.lower() in text.lower()]

    return {
        "text": text,
        "email": email,
        "phone": phone,
        "skills": skills_found,
        "education": education_found
    }
