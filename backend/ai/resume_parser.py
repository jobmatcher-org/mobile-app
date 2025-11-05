import os
import re
from pdfminer.high_level import extract_text
import docx2txt
import spacy
from sentence_transformers import SentenceTransformer, util

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Load Sentence Transformer model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from PDF or DOCX file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.endswith(".pdf"):
        return extract_text(file_path)
    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file format. Use PDF or DOCX.")

def parse_resume(file_path: str):
    """
    Parse resume and extract:
    - name
    - email
    - phone
    - skills
    - education
    - experience
    """
    text = extract_text_from_file(file_path)
    text = re.sub(r"\s+", " ", text)

    # Extract email and phone
    email_match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.findall(r"\+?\d[\d\s-]{7,}\d", text)

    # Name extraction
    name = None
    possible_header = re.split(r"Email|Phone|\|", text)[0].strip()
    parts = possible_header.split()
    candidate = " ".join([p for p in parts if p.isalpha() and p[0].isupper()])
    if 2 <= len(candidate.split()) <= 4:
        name = candidate
    else:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

    # Skills
    skill_keywords = [
        "Python", "Java", "Kotlin", "SQL", "Firebase",
        "Android", "JavaScript", "React", "Machine Learning",
        "Data Analysis", "HTML", "CSS", "FastAPI", "Jetpack", "Compose", "SQLAlchemy"
    ]
    skills_found = [skill for skill in skill_keywords if skill.lower() in text.lower()]

    # Education
    education_keywords = ["Bachelor", "Master", "B.Sc", "Engineering", "Diploma", "High School"]
    education_found = [edu for edu in education_keywords if edu.lower() in text.lower()]

    # ----------------------------
    # Experience extraction (new)
    # ----------------------------
    experience_list = []

    # Look for common experience patterns: "X years at Company", "Worked at Company"
    exp_patterns = [
        r"(\d+ years? of experience(?: in [\w\s]+)?)",
        r"(worked at [\w\s,]+)",
        r"(experience at [\w\s,]+)"
    ]
    for pattern in exp_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        experience_list.extend(matches)

    # Optional: use spaCy named entities to detect ORG + DATE mentions as experience
    doc = nlp(text)
    for sent in doc.sents:
        orgs = [ent.text for ent in sent.ents if ent.label_ == "ORG"]
        dates = [ent.text for ent in sent.ents if ent.label_ in ["DATE", "TIME"]]
        if orgs and dates:
            experience_list.append(f"{' / '.join(orgs)} ({', '.join(dates)})")

    # Deduplicate
    experience_list = list(set(experience_list))

    return {
        "text": text,
        "name": name,
        "email": email_match[0] if email_match else None,
        "phone": phone_match[0] if phone_match else None,
        "skills": skills_found,
        "education": education_found,
        "experience": experience_list  # <--- new field
    }


def score_resume(resume_data: dict, job_description: str):
    """
    Score a resume based on job description
    """
    score = 0

    # 1️⃣ Skill match (max 50 points)
    job_skills = [word for word in job_description.split() if word.istitle()]
    matched_skills = set(resume_data['skills']) & set(job_skills)
    skill_score = (len(matched_skills) / len(job_skills)) * 50 if job_skills else 0
    score += skill_score

    # 2️⃣ Education match (max 20 points)
    edu_match = any(edu.lower() in job_description.lower() for edu in resume_data['education'])
    score += 20 if edu_match else 0

    # 3️⃣ Semantic similarity (max 30 points)
    resume_embedding = model.encode(resume_data['text'], convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(resume_embedding, job_embedding).item()
    semantic_score = similarity * 30
    score += semantic_score

    return round(score, 2)
