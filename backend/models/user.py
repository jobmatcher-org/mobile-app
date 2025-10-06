from sqlalchemy import Column, Integer, String
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)       # max 50 chars
    email = Column(String(100), unique=True, index=True)         # max 100 chars
    hashed_password = Column(String(255))                        # enough for hashed passwords
    role = Column(String(20), default="jobseeker")               # "jobseeker" or "recruiter"


