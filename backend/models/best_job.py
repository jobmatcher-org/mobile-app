from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..database import Base

class HotJob(Base):
    __tablename__ = "hot_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255))
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopJob(Base):
    __tablename__ = "top_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255))
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
