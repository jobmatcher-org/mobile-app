# import os
# import re
# from pdfminer.high_level import extract_text
# import docx2txt
# import spacy
# from sentence_transformers import SentenceTransformer, util
#
# # Load spaCy NLP model
# nlp = spacy.load("en_core_web_sm")
#
# # Load Sentence Transformer model for embeddings
# model = SentenceTransformer('all-MiniLM-L6-v2')
#
# def extract_text_from_file(file_path: str) -> str:
#     """
#     Extract text from PDF or DOCX file
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"File not found: {file_path}")
#
#     if file_path.endswith(".pdf"):
#         return extract_text(file_path)
#     elif file_path.endswith(".docx"):
#         return docx2txt.process(file_path)
#     else:
#         raise ValueError("Unsupported file format. Use PDF or DOCX.")
#
# def parse_resume(file_path: str):
#     """
#     Parse resume and extract:
#     - name
#     - email
#     - phone
#     - skills
#     - education
#     - experience
#     """
#     text = extract_text_from_file(file_path)
#     text = re.sub(r"\s+", " ", text)
#
#     # Extract email and phone
#     email_match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
#     phone_match = re.findall(r"\+?\d[\d\s-]{7,}\d", text)
#
#     # Name extraction
#     name = None
#     possible_header = re.split(r"Email|Phone|\|", text)[0].strip()
#     parts = possible_header.split()
#     candidate = " ".join([p for p in parts if p.isalpha() and p[0].isupper()])
#     if 2 <= len(candidate.split()) <= 4:
#         name = candidate
#     else:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 name = ent.text
#                 break
#
#     # Skills
#     skill_keywords = [
#         "Python", "Java", "Kotlin", "SQL", "Firebase",
#         "Android", "JavaScript", "React", "Machine Learning",
#         "Data Analysis", "HTML", "CSS", "FastAPI", "Jetpack", "Compose", "SQLAlchemy"
#     ]
#     skills_found = [skill for skill in skill_keywords if skill.lower() in text.lower()]
#
#     # Education
#     education_keywords = ["Bachelor", "Master", "B.Sc", "Engineering", "Diploma", "High School"]
#     education_found = [edu for edu in education_keywords if edu.lower() in text.lower()]
#
#     # ----------------------------
#     # Experience extraction (new)
#     # ----------------------------
#     experience_list = []
#
#     # Look for common experience patterns: "X years at Company", "Worked at Company"
#     exp_patterns = [
#         r"(\d+ years? of experience(?: in [\w\s]+)?)",
#         r"(worked at [\w\s,]+)",
#         r"(experience at [\w\s,]+)"
#     ]
#     for pattern in exp_patterns:
#         matches = re.findall(pattern, text, re.IGNORECASE)
#         experience_list.extend(matches)
#
#     # Optional: use spaCy named entities to detect ORG + DATE mentions as experience
#     doc = nlp(text)
#     for sent in doc.sents:
#         orgs = [ent.text for ent in sent.ents if ent.label_ == "ORG"]
#         dates = [ent.text for ent in sent.ents if ent.label_ in ["DATE", "TIME"]]
#         if orgs and dates:
#             experience_list.append(f"{' / '.join(orgs)} ({', '.join(dates)})")
#
#     # Deduplicate
#     experience_list = list(set(experience_list))
#
#     return {
#         "text": text,
#         "name": name,
#         "email": email_match[0] if email_match else None,
#         "phone": phone_match[0] if phone_match else None,
#         "skills": skills_found,
#         "education": education_found,
#         "experience": experience_list  # <--- new field
#     }
#
#
# def score_resume(resume_data: dict, job_description: str):
#     """
#     Score a resume based on job description
#     """
#     score = 0
#
#     # 1️⃣ Skill match (max 50 points)
#     job_skills = [word for word in job_description.split() if word.istitle()]
#     matched_skills = set(resume_data['skills']) & set(job_skills)
#     skill_score = (len(matched_skills) / len(job_skills)) * 50 if job_skills else 0
#     score += skill_score
#
#     # 2️⃣ Education match (max 20 points)
#     edu_match = any(edu.lower() in job_description.lower() for edu in resume_data['education'])
#     score += 20 if edu_match else 0
#
#     # 3️⃣ Semantic similarity (max 30 points)
#     resume_embedding = model.encode(resume_data['text'], convert_to_tensor=True)
#     job_embedding = model.encode(job_description, convert_to_tensor=True)
#     similarity = util.pytorch_cos_sim(resume_embedding, job_embedding).item()
#     semantic_score = similarity * 30
#     score += semantic_score
#
#     return round(score, 2)

import os
import re
import json
from pypdf import PdfReader
import docx2txt
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from dotenv import load_dotenv

# -----------------------------
# LOAD API KEY
# -----------------------------
dotenv_path = r"C:\jobmatcher\backend\.env"
print("Looking for .env at:", dotenv_path)

if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f".env not found at {dotenv_path}")

load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv("GEM_API_KEY")
if not API_KEY:
    raise ValueError("GEM_API_KEY not found in .env")

print("GEM_API_KEY loaded successfully")

genai.configure(api_key=API_KEY)
GEM_MODEL = genai.GenerativeModel("gemini-2.5-flash")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# SANITIZATION
# -----------------------------
def clean_str(s):
    if not isinstance(s, str):
        try:
            s = str(s)
        except:
            return ""
    return s.encode("utf-8", "ignore").decode("utf-8", "ignore")

def sanitize_obj(obj):
    if isinstance(obj, (bytes, bytearray)):
        return clean_str(obj)
    if isinstance(obj, str):
        return clean_str(obj)
    if isinstance(obj, list):
        return [sanitize_obj(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): sanitize_obj(v) for k, v in obj.items()}
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except:
        pass
    if obj is None or isinstance(obj, (int, float, bool)):
        return obj
    return clean_str(obj)

# -----------------------------
# EXTRACT TEXT FROM FILE
# -----------------------------
def extract_text_from_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text = ""
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            try:
                part = page.extract_text()
                if part:
                    text += part + "\n"
            except:
                continue
    elif file_path.lower().endswith(".docx"):
        text = docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF/DOCX allowed.")

    # Truncate long resumes for Gemini
    words = text.split()
    if len(words) > 3000:  # keep smaller to avoid Gemini rejection
        text = " ".join(words[:3000])
    return clean_str(text)

# -----------------------------
# PARSE RESUME
# -----------------------------
def parse_resume(file_path: str) -> dict:
    raw_text = extract_text_from_file(file_path)
    text = clean_str(re.sub(r"\s+", " ", raw_text))

    prompt = f"""
    You are an AI resume parser. Extract ONLY the following fields from the resume text and RETURN STRICT JSON.
    
    Required JSON format:
    {{
      "name": "",
      "email": "",
      "phone": "",
      "skills": [],
      "education": [],
      "experience": []
    }}
    
    Rules:
    - DO NOT add extra text or commentary.
    - RETURN ONLY pure JSON.
    - Skills must be a list of strings.
    - Education must be a list.
    - Experience must be a list.
    - If not found, return empty list or null.
    
    Resume text begins below:
    ---------------------------
    {text}
    ---------------------------
    """

    try:
        print("Sending to Gemini...")
        response = GEM_MODEL.generate_content(prompt)
        resp_text = response.text.strip()
        if resp_text.startswith("```"):
            resp_text = resp_text.strip("`").strip()
        parsed = json.loads(resp_text)
    except Exception as e:
        print("Gemini failed or returned invalid JSON, using fallback regex:", e)
        # Fallback
        email_match = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        phone_match = re.findall(r"\+?\d[\d\s-]{7,}\d", text)
        skill_keywords = [
            "Python", "Java", "Kotlin", "SQL", "Firebase",
            "Android", "JavaScript", "React", "Machine Learning",
            "Data Analysis", "HTML", "CSS", "FastAPI", "Jetpack", "Compose", "SQLAlchemy"
        ]
        skills_found = [skill for skill in skill_keywords if skill.lower() in text.lower()]
        education_keywords = ["Bachelor", "Master", "B.Sc", "Engineering", "Diploma", "High School"]
        education_found = [edu for edu in education_keywords if edu.lower() in text.lower()]
        parsed = {
            "name": None,
            "email": email_match[0] if email_match else None,
            "phone": phone_match[0] if phone_match else None,
            "skills": skills_found,
            "education": education_found,
            "experience": []
        }

    parsed = sanitize_obj(parsed)
    parsed["text"] = sanitize_obj(text)
    return parsed

# -----------------------------
# SCORE RESUME
# -----------------------------
def score_resume(resume_data: dict, job_description: str) -> float:
    score = 0
    resume_skills = resume_data.get("skills", [])
    job_skills = [w for w in job_description.split() if w.istitle()]
    matched = set(resume_skills) & set(job_skills)
    if job_skills:
        score += (len(matched) / len(job_skills)) * 50
    edu_list = resume_data.get("education", [])
    edu_match = any(isinstance(edu, str) and edu.lower() in job_description.lower() for edu in edu_list)
    if edu_match:
        score += 20
    try:
        res_emb = embed_model.encode(resume_data["text"], convert_to_tensor=True)
        job_emb = embed_model.encode(job_description, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(res_emb, job_emb).item()
        score += similarity * 30
    except:
        pass
    return round(score, 2)

if __name__ == "__main__":
    resume_path = r"C:\jobmatcher\backend\uploads\resumes\AAYUSH SHRESTHA.pdf"
    parsed = parse_resume(resume_path)
    print("Parsed Resume:", parsed)
