from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Example .env content:
# DATABASE_URL=mysql+pymysql://root:password@localhost/jobmatcher

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/jobmatcher")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,          # <-- prints all SQL commands
    pool_pre_ping=True  # <-- avoids hanging if MySQL closes idle connections
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Dependency to use inside FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
