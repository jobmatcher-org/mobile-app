from sqlalchemy.orm import Session
from backend import models, schemas
from passlib.context import CryptContext
from backend.services import crud
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------
# Password utilities
# ---------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ---------------------------
# User registration
# ---------------------------
def register_user(db: Session, user: schemas.user.UserCreate):
    # Check if email already exists
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise ValueError("Email already registered")

    # Hash the plain password
    hashed_pw = hash_password(user.password)

    # Pass the hashed password to CRUD
    return crud.create_user(db, user, hashed_pw)

# ---------------------------
# User login
# ---------------------------
def login_user(db: Session, user: schemas.user.UserCreate):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user:
        raise ValueError("Invalid credentials")

    if not verify_password(user.password, db_user.password):
        raise ValueError("Invalid credentials")

    return db_user
def get_current_user(db: Session = Depends(get_db)):
    """
    Temporary function to simulate an authenticated user.
    In real auth, you'll decode a JWT and fetch the actual user.
    """
    user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found in database. Please register one first."
        )
    return user