from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True, nullable=False)       # max 100 chars
    description = Column(String(500), nullable=False)             # max 500 chars
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship to User
    owner = relationship("User", back_populates="jobs")
